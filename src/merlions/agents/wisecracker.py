"""Merlion Wisecracker Agent — personality with guardrails."""

from __future__ import annotations

import random
import time

from merlions.governance import govern, load_policy
from merlions.models import AgentReply, Joke

POLICY = load_policy("wisecracker")


_SAFE_JOKES: list[Joke] = [
    Joke(
        text="Why do Python devs love the sea? Because they prefer high tide and high code quality.",
        style="pun",
    ),
    Joke(
        text="A good Python dev is like the Merlion — half lion, half fish, *fully* type-hinted.",
        style="wordplay",
    ),
    Joke(
        text="I told my agent a joke about recursion. It told it back to me… and back to me… and back…",
        style="observation",
    ),
]


@govern(POLICY, tool_name="tell_joke")
def tell_joke(style: str | None = None) -> Joke:
    """Return a safe, on-tone joke."""

    pool = [j for j in _SAFE_JOKES if not style or j.style == style] or _SAFE_JOKES
    return random.choice(pool)


def quip(style: str | None = None) -> AgentReply:
    started = time.perf_counter()
    joke = tell_joke(style)
    return AgentReply(
        agent_id="wisecracker",
        summary=f"😎 {joke.text}",
        citations=[],
        latency_ms=int((time.perf_counter() - started) * 1000),
    )
