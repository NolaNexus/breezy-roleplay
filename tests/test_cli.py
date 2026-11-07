"""Tests for the command-line interface.

The CLI is exercised through :func:`breezy_roleplay.cli.main` with the working
directory pointed at a temporary path, so the real ``SessionStore`` is used and
the on-disk effects are asserted alongside the exit codes.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from breezy_roleplay.cli import EXIT_FAILURE, EXIT_OK, main


@pytest.fixture
def workdir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Run the CLI as if it were invoked from an empty project directory."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_create_prints_and_writes_session(
    workdir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """``create`` reports the session and lays it out on disk."""
    assert main(["create", "test-session"]) == EXIT_OK

    captured = capsys.readouterr()
    assert captured.out.strip() == "Created session: test-session"
    assert (workdir / "sessions" / "test-session" / "metadata.json").is_file()


def test_archive_reports_zip_path(workdir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """``archive`` zips an existing session."""
    assert main(["create", "archivable"]) == EXIT_OK
    capsys.readouterr()

    assert main(["archive", "archivable"]) == EXIT_OK

    assert capsys.readouterr().out.strip() == "Archived session: archivable"
    assert (workdir / "sessions" / "archivable.zip").is_file()


def test_list_reports_empty_state(workdir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """With nothing created, ``list`` explains the empty state."""
    assert main(["list"]) == EXIT_OK
    assert capsys.readouterr().out.strip() == "No sessions found"


def test_list_prints_session_names(workdir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """``list`` prints one directory name per line, sorted."""
    for session_id in ("beta", "alpha"):
        assert main(["create", session_id]) == EXIT_OK
    capsys.readouterr()

    assert main(["list"]) == EXIT_OK
    assert capsys.readouterr().out.split() == ["alpha", "beta"]


def test_demo_creates_archive(workdir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """``demo`` performs the create and archive cycle in one command."""
    assert main(["demo"]) == EXIT_OK

    out = capsys.readouterr().out
    assert "Demo session created and archived at:" in out
    assert len(list((workdir / "sessions").glob("demo-*.zip"))) == 1


def test_create_duplicate_exits_one_and_records_error(
    workdir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A failed command exits 1, explains itself, and records the error."""
    assert main(["create", "dup"]) == EXIT_OK
    capsys.readouterr()

    assert main(["create", "dup"]) == EXIT_FAILURE

    captured = capsys.readouterr()
    assert "already exists" in captured.err
    assert captured.out == ""
    payload = json.loads((workdir / "sessions" / "dup" / "errors.json").read_text())
    assert payload["error"]["type"] == "FileExistsError"
    assert payload["context"] == {"command": "create"}


def test_archive_missing_session_exits_one(
    workdir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Archiving an unknown session fails cleanly with exit code 1."""
    assert main(["archive", "missing"]) == EXIT_FAILURE
    assert "Session directory not found" in capsys.readouterr().err


def test_create_rejects_invalid_id(workdir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """An unsafe session ID is refused before anything is written."""
    assert main(["create", "bad/id"]) == EXIT_FAILURE

    assert "may only contain" in capsys.readouterr().err
    assert not (workdir / "sessions" / "bad").exists()


def test_unknown_command_exits_two(workdir: Path) -> None:
    """Argparse rejects unknown commands with usage exit code 2."""
    with pytest.raises(SystemExit) as exc_info:
        main(["invalid-command"])
    assert exc_info.value.code == 2


def test_missing_argument_exits_two(workdir: Path) -> None:
    """A required positional argument is enforced by argparse."""
    with pytest.raises(SystemExit) as exc_info:
        main(["create"])
    assert exc_info.value.code == 2


def test_no_command_exits_two(workdir: Path) -> None:
    """A subcommand is required."""
    with pytest.raises(SystemExit) as exc_info:
        main([])
    assert exc_info.value.code == 2


def test_version_flag(workdir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """``--version`` prints the packaged version and exits successfully."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    assert "breezy-roleplay" in capsys.readouterr().out
