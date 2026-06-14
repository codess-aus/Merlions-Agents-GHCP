"""Governance: policy as configuration, fail-closed, audit-logged.

Usage:

    from merlions.governance import govern, load_policy

    policy = load_policy("hawker")

    @govern(policy)
    def find_stalls(location: str, cuisine: str | None = None): ...
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass, field
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Iterable

import yaml

from merlions.telemetry import emit_event

POLICY_DIR = Path(__file__).parent / "policies"
AUDIT_DIR = Path(os.environ.get("MERLIONS_AUDIT_DIR", ".audit"))


@dataclass(frozen=True)
class Policy:
    name: str
    allowed_tools: tuple[str, ...]
    blocked_patterns: tuple[re.Pattern[str], ...] = field(default_factory=tuple)
    max_calls_per_request: int = 25
    require_citation: bool = False


def load_policy(name: str) -> Policy:
    """Load a policy from YAML. Fails closed if the file is missing or malformed."""

    path = POLICY_DIR / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Policy not found: {name}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    try:
        return Policy(
            name=raw["name"],
            allowed_tools=tuple(raw.get("allowed_tools", ())),
            blocked_patterns=tuple(re.compile(p) for p in raw.get("blocked_patterns", ())),
            max_calls_per_request=int(raw.get("max_calls_per_request", 25)),
            require_citation=bool(raw.get("require_citation", False)),
        )
    except (KeyError, TypeError, re.error) as exc:
        # Fail closed: a malformed policy denies everything by raising.
        raise ValueError(f"Malformed policy {name}: {exc}") from exc


class PolicyViolation(PermissionError):
    """Raised when a governance check denies an action. Fails closed."""


def _scan_args(values: Iterable[Any], patterns: tuple[re.Pattern[str], ...]) -> str | None:
    for v in values:
        if not isinstance(v, str):
            continue
        for pat in patterns:
            if pat.search(v):
                return pat.pattern
    return None


_call_counter: dict[str, int] = {}


def _audit(record: dict[str, Any]) -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    path = AUDIT_DIR / "audit.jsonl"
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


def govern(policy: Policy, *, tool_name: str | None = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Wrap a tool/agent function with governance checks.

    Checks (in order, fail closed):
      1. Tool name is in the allowlist.
      2. Per-request call counter is under the cap.
      3. String arguments do not match any blocked pattern.

    Every decision (allow or deny) is recorded to the audit log and to
    structured telemetry. Raw argument values are never logged.
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        resolved_tool = tool_name or fn.__name__

        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            decision: str = "allow"
            matched: str | None = None

            if resolved_tool not in policy.allowed_tools:
                decision, matched = "deny", f"tool_not_allowlisted:{resolved_tool}"
            else:
                count = _call_counter.get(policy.name, 0) + 1
                _call_counter[policy.name] = count
                if count > policy.max_calls_per_request:
                    decision, matched = "deny", "rate_limit_exceeded"
                else:
                    hit = _scan_args(list(args) + list(kwargs.values()), policy.blocked_patterns)
                    if hit is not None:
                        decision, matched = "deny", f"blocked_patterns/{hit}"

            record = {
                "timestamp": time.time(),
                "policy": policy.name,
                "tool": resolved_tool,
                "decision": decision,
                "matched_rule": matched,
            }
            _audit(record)
            emit_event(f"policy.{decision}", policy=policy.name, tool=resolved_tool, matched_rule=matched)

            if decision == "deny":
                raise PolicyViolation(f"{policy.name} denied {resolved_tool}: {matched}")
            return fn(*args, **kwargs)

        wrapper.__merlions_policy__ = policy  # type: ignore[attr-defined]
        wrapper.__merlions_tool__ = resolved_tool  # type: ignore[attr-defined]
        return wrapper

    return decorator


def reset_call_counter() -> None:
    """Reset per-policy call counter between requests."""

    _call_counter.clear()
