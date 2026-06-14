"""Pytest fixtures."""

from __future__ import annotations

import os
import tempfile

import pytest


@pytest.fixture(autouse=True)
def _isolate_trace_and_audit_dirs(monkeypatch):
    """Keep test artifacts out of the repo working directory."""

    tmp = tempfile.mkdtemp(prefix="merlions-test-")
    monkeypatch.setenv("MERLIONS_TRACE_DIR", os.path.join(tmp, "traces"))
    monkeypatch.setenv("MERLIONS_AUDIT_DIR", os.path.join(tmp, "audit"))
    # Force re-read at module level.
    from merlions import governance, telemetry
    from pathlib import Path

    telemetry.TRACE_DIR = Path(os.environ["MERLIONS_TRACE_DIR"])
    governance.AUDIT_DIR = Path(os.environ["MERLIONS_AUDIT_DIR"])
    yield
