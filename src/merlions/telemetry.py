"""Structured telemetry that mimics Azure Application Insights shape.

Writes JSON Lines so the demo can show 'App Insights-style' traces without
needing an Azure subscription.

=============================================================================
PRODUCTION: swap the JSON-lines emitter for Azure Monitor like this:

    from azure.monitor.opentelemetry import configure_azure_monitor
    from opentelemetry import trace

    configure_azure_monitor(
        connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
    )

    tracer = trace.get_tracer(__name__)

    # Then replace the `span` context manager below with:
    with tracer.start_as_current_span("agent.hawker") as s:
        s.set_attribute("agent_id", "hawker")
        ...

The rest of the codebase (agents, governance, tools) calls only `span()`
and `emit_event()` from this module — swap this file and everything else
stays the same.

Cost tip: use sampling (e.g. 10%) in production to avoid paying for every
single tool call. Keep denials and errors at 100% sample rate.
=============================================================================
"""

from __future__ import annotations

import json
import os
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

TRACE_DIR = Path(os.environ.get("MERLIONS_TRACE_DIR", ".traces"))


def _trace_file() -> Path:
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    return TRACE_DIR / "traces.jsonl"


@dataclass
class Span:
    name: str
    trace_id: str
    span_id: str
    parent_id: str | None
    start_ms: float
    custom_dimensions: dict[str, Any] = field(default_factory=dict)

    def end(self, **extra: Any) -> dict[str, Any]:
        duration = round((time.perf_counter() - self.start_ms) * 1000, 2)
        record = {
            "timestamp": time.time(),
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_id": self.parent_id,
            "duration_ms": duration,
            "custom_dimensions": {**self.custom_dimensions, **extra},
        }
        with _trace_file().open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
        return record


_current_trace: list[str | None] = [None]
_current_parent: list[str | None] = [None]


def new_trace_id() -> str:
    tid = uuid.uuid4().hex[:16]
    _current_trace[0] = tid
    _current_parent[0] = None
    return tid


@contextmanager
def span(name: str, **dims: Any) -> Iterator[Span]:
    """Open a span. Auto-nests via module-level parent stack."""

    trace_id = _current_trace[0] or new_trace_id()
    span_id = uuid.uuid4().hex[:12]
    parent = _current_parent[0]
    s = Span(
        name=name,
        trace_id=trace_id,
        span_id=span_id,
        parent_id=parent,
        start_ms=time.perf_counter(),
        custom_dimensions=dims,
    )
    prev_parent = _current_parent[0]
    _current_parent[0] = span_id
    try:
        yield s
    finally:
        _current_parent[0] = prev_parent
        s.end()


def emit_event(event: str, **dims: Any) -> None:
    """One-off structured event (e.g. policy.deny). Never logs raw user content."""

    record = {
        "timestamp": time.time(),
        "event": event,
        "trace_id": _current_trace[0],
        "span_id": _current_parent[0],
        "custom_dimensions": dims,
    }
    with _trace_file().open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")
