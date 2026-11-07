"""Tests for the session lifecycle, run through the real CLI entry point."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "src"
EXPECTED_MEMBERS = {"transcript.txt", "summary.md", "metadata.json", "metrics.json"}


def run_cli(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run ``python -m breezy_roleplay`` in ``cwd`` and capture its output."""
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join([str(SRC_DIR), env.get("PYTHONPATH", "")]).rstrip(
        os.pathsep
    )
    env["BREEZY_TRACE_ID"] = "integration-test-trace"
    return subprocess.run(
        [sys.executable, "-m", "breezy_roleplay", *args],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.integration
def test_session_lifecycle(tmp_path: Path) -> None:
    """Create, populate, archive, and inspect a session end to end."""
    session_id = "test-session-123"

    created = run_cli(tmp_path, "create", session_id)
    assert created.returncode == 0, created.stderr
    assert f"Created session: {session_id}" in created.stdout

    session_dir = tmp_path / "sessions" / session_id
    for name in ("transcript.txt", "summary.md", "metadata.json", "metrics.json"):
        assert (session_dir / name).is_file(), f"{name} was not created"

    (session_dir / "transcript.txt").write_text("User: Hello\nAssistant: Hi there!\n")
    (session_dir / "summary.md").write_text("# Test Session\n\nA brief summary.")

    archived = run_cli(tmp_path, "archive", session_id)
    assert archived.returncode == 0, archived.stderr
    assert f"Archived session: {session_id}" in archived.stdout

    zip_path = tmp_path / "sessions" / f"{session_id}.zip"
    assert zip_path.is_file()

    with zipfile.ZipFile(zip_path) as archive:
        assert set(archive.namelist()) == EXPECTED_MEMBERS
        # Members must be relative: a nested session path would break extraction.
        assert all(not name.startswith("/") and ".." not in name for name in archive.namelist())

        assert archive.read("transcript.txt").decode() == "User: Hello\nAssistant: Hi there!\n"

        metadata = json.loads(archive.read("metadata.json"))
        assert metadata["id"] == session_id
        assert metadata["schema_version"] == "1.0"

        metrics = json.loads(archive.read("metrics.json"))
        assert metrics["duration_ms"] == 0
        assert metrics["steps"] == 0
        assert metrics["created_at"] == metadata["created_at"]


@pytest.mark.integration
def test_list_and_demo_commands(tmp_path: Path) -> None:
    """``list`` reflects created sessions and ``demo`` produces a valid archive."""
    empty = run_cli(tmp_path, "list")
    assert empty.returncode == 0, empty.stderr
    assert empty.stdout.strip() == "No sessions found"

    assert run_cli(tmp_path, "create", "alpha").returncode == 0

    listed = run_cli(tmp_path, "list")
    assert listed.returncode == 0, listed.stderr
    assert listed.stdout.split() == ["alpha"]

    demo = run_cli(tmp_path, "demo")
    assert demo.returncode == 0, demo.stderr
    archives = sorted((tmp_path / "sessions").glob("demo-*.zip"))
    assert len(archives) == 1
    with zipfile.ZipFile(archives[0]) as archive:
        assert set(archive.namelist()) == EXPECTED_MEMBERS
        assert archive.read("transcript.txt").strip()


@pytest.mark.integration
def test_failures_exit_nonzero_and_record_errors(tmp_path: Path) -> None:
    """A rejected session ID exits 1 and does not leave a half-built session."""
    assert run_cli(tmp_path, "create", "ok-session").returncode == 0

    rejected = run_cli(tmp_path, "create", "ok-session")
    assert rejected.returncode == 1
    assert "already exists" in rejected.stderr

    errors_path = tmp_path / "sessions" / "ok-session" / "errors.json"
    assert errors_path.is_file()
    payload = json.loads(errors_path.read_text())
    assert payload["error"]["type"] == "FileExistsError"
    assert payload["context"] == {"command": "create"}

    missing = run_cli(tmp_path, "archive", "does-not-exist")
    assert missing.returncode == 1
    assert "Session directory not found" in missing.stderr


@pytest.mark.integration
def test_structured_logs_are_json_on_stderr(tmp_path: Path) -> None:
    """Structured logs stay on stderr so stdout remains pipeable."""
    result = run_cli(tmp_path, "create", "logged-session")
    assert result.returncode == 0, result.stderr

    entries = [json.loads(line) for line in result.stderr.splitlines() if line.strip()]
    assert entries, "expected at least one structured log line"
    create_entry = next(entry for entry in entries if entry["event"] == "session.create")
    assert create_entry["session_id"] == "logged-session"
    assert create_entry["trace_id"] == "integration-test-trace"
    assert create_entry["level"] == "info"
