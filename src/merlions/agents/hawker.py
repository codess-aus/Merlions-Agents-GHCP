"""Hawker Recommender Agent.

Pattern: tool → retrieve → ground → cite.
"""

from __future__ import annotations

import time

from merlions.governance import govern, load_policy
from merlions.models import AgentReply, InvalidInput
from merlions.telemetry import span
from merlions.tools.maps import maps_search
from merlions.tools.menu_index import menu_index_search

POLICY = load_policy("hawker")


@govern(POLICY, tool_name="find_stalls")
def find_stalls(location: str, cuisine: str | None = None):
    """Governed tool wrapper for maps_search. Demo 1 illustrates this pattern."""

    return maps_search(location, cuisine)


def recommend(location: str, cuisine: str | None = None) -> AgentReply:
    """Recommend a stall, grounded in the menu index, with a citation."""

    started = time.perf_counter()
    with span("agent.hawker", location=location, cuisine=cuisine or ""):
        stalls = find_stalls(location=location, cuisine=cuisine)
        if not stalls:
            # Refusal is a feature — don't hallucinate a stall.
            return AgentReply(
                agent_id="hawker",
                summary=(
                    f"I don't have a verified stall near {location} right now — "
                    "try a more specific area or different cuisine."
                ),
                citations=[],
                latency_ms=int((time.perf_counter() - started) * 1000),
            )
        top = stalls[0]
        snippet = menu_index_search(top.source)
        if snippet is None:
            # No grounding source → refuse gracefully.
            raise InvalidInput(f"no verified menu source for {top.name}")
        summary = (
            f"🍜 Try {top.name} at {top.centre} — {top.signature_dish} "
            f"is a local favourite tonight."
        )
        return AgentReply(
            agent_id="hawker",
            summary=summary,
            citations=[top.source],
            latency_ms=int((time.perf_counter() - started) * 1000),
        )
