"""Tests for reliability.py — @retry and FallbackChain."""

from __future__ import annotations

import pytest

from merlions.reliability import FallbackChain, retry


# ---------------------------------------------------------------------------
# @retry
# ---------------------------------------------------------------------------


def test_retry_succeeds_first_try():
    calls = []

    @retry(max_attempts=3, base_delay=0)
    def fn():
        calls.append(1)
        return "ok"

    assert fn() == "ok"
    assert len(calls) == 1


def test_retry_recovers_after_transient_failure():
    calls = []

    @retry(max_attempts=3, base_delay=0, exceptions=(ValueError,))
    def fn():
        calls.append(1)
        if len(calls) < 2:
            raise ValueError("transient")
        return "ok"

    assert fn() == "ok"
    assert len(calls) == 2


def test_retry_raises_after_max_attempts():
    @retry(max_attempts=2, base_delay=0, exceptions=(RuntimeError,))
    def fn():
        raise RuntimeError("always fails")

    with pytest.raises(RuntimeError, match="always fails"):
        fn()


def test_retry_does_not_catch_unexpected_exceptions():
    """Exceptions not in the `exceptions` tuple propagate immediately."""

    @retry(max_attempts=3, base_delay=0, exceptions=(ValueError,))
    def fn():
        raise TypeError("unexpected")

    with pytest.raises(TypeError):
        fn()


# ---------------------------------------------------------------------------
# FallbackChain
# ---------------------------------------------------------------------------


def test_fallback_chain_returns_primary_on_success():
    result = FallbackChain(
        primary=lambda: "primary",
        fallbacks=[lambda: "fallback"],
        label="test",
    ).run()
    assert result == "primary"


def test_fallback_chain_falls_through_on_primary_failure():
    def bad_primary():
        raise RuntimeError("down")

    result = FallbackChain(
        primary=bad_primary,
        fallbacks=[lambda: "cached", lambda: "default"],
        label="test",
    ).run()
    assert result == "cached"


def test_fallback_chain_reaches_last_fallback():
    def fail():
        raise RuntimeError("down")

    result = FallbackChain(
        primary=fail,
        fallbacks=[fail, lambda: "safe default"],
        label="test",
    ).run()
    assert result == "safe default"


def test_fallback_chain_raises_when_all_fail():
    def fail():
        raise RuntimeError("all gone")

    with pytest.raises(RuntimeError):
        FallbackChain(primary=fail, fallbacks=[fail], label="test").run()
