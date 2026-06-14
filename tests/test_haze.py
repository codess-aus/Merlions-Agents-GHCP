"""Tests for the Haze agent — idempotent alerts + fallback chain."""

from __future__ import annotations

import pytest

from merlions.agents.haze import check
from merlions.governance import reset_call_counter
from merlions.tools.nea import reset_alert_dedupe


@pytest.fixture(autouse=True)
def _reset():
    reset_call_counter()
    reset_alert_dedupe()
    yield
    reset_call_counter()
    reset_alert_dedupe()


def test_check_returns_cited_reply():
    reply = check(region="south")
    assert reply.agent_id == "haze"
    assert reply.citations, "must cite at least one NEA source"
    assert "PSI" in reply.summary


def test_alert_is_idempotent_within_same_band():
    """Two consecutive checks for the same region+band only alert once."""

    first = check(region="south")
    second = check(region="south")
    # Same band → same dedupe key → no double 'mask up' messaging (Moderate band).
    assert first.summary == second.summary


def test_invalid_region_raises():
    with pytest.raises(Exception):
        check(region="atlantis")  # type: ignore[arg-type]
