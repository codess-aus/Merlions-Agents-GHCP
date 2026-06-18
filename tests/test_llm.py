"""Tests for the LLM integration layer — offline mode (no API key needed)."""

from __future__ import annotations

import pytest

from merlions.llm import LLMResponse, complete


def test_complete_returns_mock_when_no_endpoint(monkeypatch):
    """Without env vars, complete() returns a deterministic mock."""
    monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_KEY", raising=False)

    result = complete(system="You are helpful.", user="Hello?", agent_id="hawker")
    assert isinstance(result, LLMResponse)
    assert result.mock is True
    assert result.text  # non-empty


def test_complete_attaches_citations(monkeypatch):
    monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_KEY", raising=False)

    result = complete(
        system="sys",
        user="user",
        grounded_on=["menu_index/satay-bay/2026-06-13"],
        agent_id="hawker",
    )
    assert result.grounded_on == ["menu_index/satay-bay/2026-06-13"]


def test_complete_returns_default_mock_for_unknown_agent(monkeypatch):
    monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_KEY", raising=False)

    result = complete(system="sys", user="user", agent_id="unknown_agent_xyz")
    assert result.mock is True
    assert result.text  # falls back to _MOCKS["default"]
