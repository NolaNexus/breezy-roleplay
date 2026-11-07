"""Tests for :mod:`breezy_roleplay.errors`."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from breezy_roleplay.errors import record_error


def make_session(tmp_path: Path, session_id: str = "broken") -> Path:
    """Create the session directory ``record_error`` writes into."""
    session_dir = tmp_path / "sessions" / session_id
    session_dir.mkdir(parents=True)
    return session_dir


def test_record_error_writes_payload(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """An error is persisted with type, message, traceback, and context."""
    monkeypatch.chdir(tmp_path)
    session_dir = make_session(tmp_path)

    try:
        raise RuntimeError("boom")
    except RuntimeError as exc:
        path = record_error("broken", exc, {"command": "create"})

    assert path == session_dir / "errors.json"
    payload = json.loads(path.read_text())
    assert payload["error"] == {"type": "RuntimeError", "message": "boom"}
    assert payload["context"] == {"command": "create"}
    assert "RuntimeError: boom" in payload["traceback"]
    assert payload["timestamp"].endswith("+00:00")
    assert "errors.record" in capsys.readouterr().err


def test_record_error_without_context(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Context is optional and omitted from the payload when absent."""
    monkeypatch.chdir(tmp_path)
    session_dir = make_session(tmp_path, "no-context")

    path = record_error("no-context", ValueError("bad input"))

    assert path is not None
    payload = json.loads((session_dir / "errors.json").read_text())
    assert "context" not in payload
    assert payload["error"]["type"] == "ValueError"


def test_record_error_missing_session_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A missing session directory is logged and skipped, never created."""
    monkeypatch.chdir(tmp_path)

    assert record_error("absent", ValueError("x")) is None
    assert not (tmp_path / "sessions" / "absent").exists()
    assert "Session directory not found" in capsys.readouterr().err
