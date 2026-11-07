"""Shared fixtures for the breezy-roleplay test suite."""

from __future__ import annotations

from pathlib import Path

import pytest

from breezy_roleplay.session import SessionStore


@pytest.fixture
def session_root(tmp_path: Path) -> Path:
    """Return a temporary directory to use as the sessions root."""
    return tmp_path / "sessions"


@pytest.fixture
def store(session_root: Path) -> SessionStore:
    """Return a :class:`SessionStore` rooted in a temporary directory."""
    return SessionStore(root=session_root)


@pytest.fixture
def metrics_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point ``BREEZY_METRICS_FILE`` at a temporary Prometheus textfile."""
    path = tmp_path / "metrics" / "breezy.prom"
    monkeypatch.setenv("BREEZY_METRICS_FILE", str(path))
    return path
