"""Tests for the governance decorator itself."""

from __future__ import annotations

import re

import pytest

from merlions.governance import Policy, PolicyViolation, govern, reset_call_counter


@pytest.fixture(autouse=True)
def _reset():
    reset_call_counter()
    yield
    reset_call_counter()


def _policy(**overrides) -> Policy:
    base = dict(
        name="test",
        allowed_tools=("ok",),
        blocked_patterns=(re.compile("(?i)password"),),
        max_calls_per_request=2,
    )
    base.update(overrides)
    return Policy(**base)


def test_allows_tool_on_allowlist():
    @govern(_policy(), tool_name="ok")
    def fn(x: str) -> str:
        return x

    assert fn("hello") == "hello"


def test_denies_tool_not_on_allowlist():
    @govern(_policy())
    def not_ok(x: str) -> str:
        return x

    with pytest.raises(PolicyViolation):
        not_ok("hi")


def test_denies_when_arg_matches_blocked_pattern():
    @govern(_policy(), tool_name="ok")
    def fn(x: str) -> str:
        return x

    with pytest.raises(PolicyViolation):
        fn("my password=hunter2")


def test_enforces_rate_limit():
    @govern(_policy(), tool_name="ok")
    def fn() -> str:
        return "x"

    fn()
    fn()
    with pytest.raises(PolicyViolation):
        fn()
