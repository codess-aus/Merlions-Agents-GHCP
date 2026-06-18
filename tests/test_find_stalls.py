"""Tests for the governed find_stalls tool — Demo 1 lives here."""

from __future__ import annotations

import pytest

from merlions.tools.find_stalls import find_stalls
from merlions.governance import PolicyViolation, reset_call_counter
from merlions.models import InvalidInput, Stall


@pytest.fixture(autouse=True)
def _reset():
    reset_call_counter()
    yield
    reset_call_counter()


def test_find_stalls_happy_path():
    """Marina Bay returns a typed list of Stall with citations."""

    results = find_stalls(location="marina bay")
    assert isinstance(results, list)
    assert results and all(isinstance(r, Stall) for r in results)
    assert all(r.source.startswith("menu_index/") for r in results)


def test_find_stalls_empty_location_raises():
    """Empty input must raise — refusal is a feature."""

    with pytest.raises(InvalidInput):
        find_stalls(location="")


def test_find_stalls_blocks_credential_in_arg():
    """Governance fails closed when an arg looks like a credential."""

    with pytest.raises(PolicyViolation):
        find_stalls(location="api_key=AKIA...something")


def test_find_stalls_rate_limit():
    """Per-request cap denies the 11th call (cap is 10 in hawker.yaml)."""

    for _ in range(10):
        find_stalls(location="marina bay")
    with pytest.raises(PolicyViolation):
        find_stalls(location="marina bay")


def test_find_stalls_unknown_location_returns_empty():
    """Unknown but non-empty location returns [] — caller decides what to do."""

    assert find_stalls(location="middle of the ocean") == []
