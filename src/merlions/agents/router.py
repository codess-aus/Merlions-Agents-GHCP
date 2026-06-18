"""Router — classifies intent and dispatches to specialised agents.

For the demo we use a deterministic keyword router so the conference Wi-Fi
isn't on the critical path. Swap classify() for an LLM call in production.
"""

from __future__ import annotations

import concurrent.futures
import time
from dataclasses import dataclass

from merlions.agents import hawker, haze, wisecracker
from merlions.governance import reset_call_counter
from merlions.models import AgentReply, RouterReply
from merlions.telemetry import new_trace_id, span


@dataclass
class Intent:
    wants_food: bool
    wants_air: bool
    wants_humour: bool

    def any(self) -> bool:
        return self.wants_food or self.wants_air or self.wants_humour


_FOOD = ("dinner", "lunch", "eat", "food", "hawker", "hungry", "supper", "breakfast")
_AIR = ("air", "psi", "haze", "smoke", "walk", "outside", "outdoor")
_HUMOUR = ("laugh", "joke", "pun", "funny", "humour", "humor", "make me smile")


def classify(prompt: str) -> Intent:
    p = prompt.lower()
    return Intent(
        wants_food=any(k in p for k in _FOOD),
        wants_air=any(k in p for k in _AIR),
        wants_humour=any(k in p for k in _HUMOUR),
    )


def _extract_location(prompt: str) -> str:
    p = prompt.lower()
    for loc in ("marina bay", "chinatown"):
        if loc in p:
            return loc
    return "marina bay"


def handle(prompt: str) -> RouterReply:
    """Route a user prompt to the right agents and compose the answer."""

    reset_call_counter()
    trace_id = new_trace_id()
    started = time.perf_counter()
    intent = classify(prompt)

    location = _extract_location(prompt)

    with span("router.handle", wants_food=intent.wants_food, wants_air=intent.wants_air, wants_humour=intent.wants_humour):
        tasks: list[tuple[str, object]] = []

        if intent.wants_food or not intent.any():
            tasks.append(("hawker", lambda: hawker.recommend(location=location)))
        if intent.wants_air:
            tasks.append(("haze", lambda: haze.check(region="south")))
        if intent.wants_humour:
            tasks.append(("wisecracker", lambda: wisecracker.quip()))

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(tasks) or 1) as executor:
            submitted = [executor.submit(fn) for _, fn in tasks]
            parts = [f.result() for f in submitted]

        return RouterReply(
            parts=parts,
            total_latency_ms=int((time.perf_counter() - started) * 1000),
            trace_id=trace_id,
        )
