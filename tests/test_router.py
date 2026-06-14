"""Tests for the router — composite intents fan out to multiple agents."""

from __future__ import annotations

import pytest

from merlions.agents.router import classify, handle
from merlions.governance import reset_call_counter
from merlions.tools.nea import reset_alert_dedupe


@pytest.fixture(autouse=True)
def _reset():
    reset_call_counter()
    reset_alert_dedupe()
    yield
    reset_call_counter()
    reset_alert_dedupe()


def test_classify_composite_intent():
    intent = classify("Dinner near Marina Bay, is the air OK to walk there, and make me laugh.")
    assert intent.wants_food and intent.wants_air and intent.wants_humour


def test_handle_composite_question_returns_three_parts():
    reply = handle("Dinner near Marina Bay, is the air OK to walk there, and make me laugh.")
    assert len(reply.parts) == 3
    ids = [p.agent_id for p in reply.parts]
    assert ids == ["hawker", "haze", "wisecracker"]
    # Every factual agent must cite. The wisecracker is allowed to be uncited.
    for part in reply.parts:
        if part.agent_id != "wisecracker":
            assert part.citations, f"{part.agent_id} must cite sources"


def test_handle_food_only():
    reply = handle("recommend dinner near chinatown")
    assert [p.agent_id for p in reply.parts] == ["hawker"]
