"""Tests for the governed find_stalls tool — Demo 1 lives here."""

from __future__ import annotations

import pytest

from merlions.governance import PolicyViolation, reset_call_counter
from merlions.models import InvalidInput, Stall
from merlions.tools.find_stalls import find_stalls


@pytest.fixture(autouse=True)
def reset_counter():
    reset_call_counter()
    yield
    reset_call_counter()


def test_happy_path_marina_bay_returns_stalls():
    """Happy path — marina bay returns a non-empty list of Stall with citations."""
    results = find_stalls("marina bay")

    assert isinstance(results, list)
    assert len(results) > 0
    for stall in results:
        assert isinstance(stall, Stall)
        assert stall.source_citation, f"Stall {stall!r} is missing a source citation"


def test_empty_location_raises_invalid_input():
    """Empty location string raises InvalidInput."""
    with pytest.raises(InvalidInput):
        find_stalls("")


def test_credential_in_location_raises_policy_violation():
    """A credential string in the location arg triggers a PolicyViolation."""
    with pytest.raises(PolicyViolation):
        find_stalls("api_key=demo_key")


def test_rate_limit_raises_policy_violation_on_16th_call():
    """After 15 calls the 16th raises PolicyViolation (hawker max_calls_per_request is 15)."""
    for _ in range(15):
        find_stalls("marina bay")

    with pytest.raises(PolicyViolation):
        find_stalls("marina bay")


def test_unknown_location_returns_empty_list():
    """An unknown but non-empty location returns an empty list without raising."""
    results = find_stalls("xyzzy-no-such-place-42")

    assert isinstance(results, list)
    assert len(results) == 0
