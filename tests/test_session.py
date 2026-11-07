"""Tests for :class:`breezy_roleplay.session.SessionStore`."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from breezy_roleplay.session import SessionStore

ALL_MEMBERS = {"transcript.txt", "summary.md", "metadata.json", "metrics.json"}
CORE_MEMBERS = {"transcript.txt", "summary.md"}


def test_create_writes_expected_layout(store: SessionStore, session_root: Path) -> None:
    """Creating a session produces the transcript, summary, metadata and metrics."""
    session_dir = store.create("test-session")

    assert session_dir == session_root / "test-session"
    for name in ALL_MEMBERS:
        assert (session_dir / name).is_file()

    metadata = json.loads((session_dir / "metadata.json").read_text())
    assert metadata["id"] == "test-session"
    assert metadata["schema_version"] == "1.0"
    assert metadata["created_at"].endswith("+00:00")

    metrics = json.loads((session_dir / "metrics.json").read_text())
    assert metrics == {"created_at": metadata["created_at"], "duration_ms": 0, "steps": 0}


def test_create_rejects_duplicates(store: SessionStore) -> None:
    """A second create for the same ID fails instead of clobbering the session."""
    store.create("dup")
    with pytest.raises(FileExistsError, match="already exists"):
        store.create("dup")


@pytest.mark.parametrize(
    ("session_id", "message"),
    [
        ("", "must not be empty"),
        ("/absolute/path", "must not be an absolute path"),
        ("..", "path traversal"),
        ("../escape", "path traversal"),
        ("nested/../escape", "path traversal"),
        ("back\\slash", "path traversal"),
        ("with space", "may only contain"),
        ("semi;colon", "may only contain"),
        ("unicode-é", "may only contain"),
    ],
)
def test_create_rejects_unsafe_ids(store: SessionStore, session_id: str, message: str) -> None:
    """IDs that could escape the sessions directory are refused."""
    with pytest.raises(ValueError, match=message):
        store.create(session_id)


def test_archive_uses_relative_members(store: SessionStore, session_root: Path) -> None:
    """Archive members are flat and relative so extraction is portable."""
    session_dir = store.create("archivable")
    (session_dir / "transcript.txt").write_text("User: hi\n")
    (session_dir / "summary.md").write_text("# Summary\n")

    zip_path = store.archive("archivable")

    assert zip_path == session_root / "archivable.zip"
    with zipfile.ZipFile(zip_path) as archive:
        assert set(archive.namelist()) == ALL_MEMBERS
        assert archive.read("transcript.txt").decode() == "User: hi\n"
        assert archive.read("summary.md").decode() == "# Summary\n"


def test_archive_honours_manifest_flag(
    store: SessionStore, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Disabling the manifest flag drops metadata and metrics from the archive."""
    monkeypatch.setattr("breezy_roleplay.session.ARCHIVE_MANIFEST", False)
    store.create("lean")

    zip_path = store.archive("lean")

    with zipfile.ZipFile(zip_path) as archive:
        assert set(archive.namelist()) == CORE_MEMBERS


def test_archive_replaces_stale_zip(store: SessionStore) -> None:
    """Re-archiving overwrites the previous archive rather than appending to it."""
    session_dir = store.create("rerun")
    (session_dir / "transcript.txt").write_text("first")
    first = store.archive("rerun")

    (session_dir / "transcript.txt").write_text("second")
    second = store.archive("rerun")

    assert first == second
    with zipfile.ZipFile(second) as archive:
        assert archive.read("transcript.txt").decode() == "second"


def test_archive_warns_about_missing_files(
    store: SessionStore, capsys: pytest.CaptureFixture[str]
) -> None:
    """A session missing an expected file is still archived, with a warning."""
    session_dir = store.create("partial")
    (session_dir / "summary.md").unlink()

    zip_path = store.archive("partial")

    with zipfile.ZipFile(zip_path) as archive:
        assert set(archive.namelist()) == {"transcript.txt", "metadata.json", "metrics.json"}
    assert "Expected file not found" in capsys.readouterr().err


def test_archive_missing_session_raises(store: SessionStore) -> None:
    """Archiving an unknown session reports a clear error."""
    with pytest.raises(FileNotFoundError, match="Session directory not found"):
        store.archive("nope")


def test_archive_rejects_unsafe_ids(store: SessionStore) -> None:
    """Archive validates the ID before touching the filesystem."""
    with pytest.raises(ValueError, match="path traversal"):
        store.archive("../escape")


def test_list_sessions_is_sorted(store: SessionStore) -> None:
    """Only directories are listed, in name order."""
    assert store.list_sessions() == []

    store.create("b-session")
    store.create("a-session")
    store.archive("a-session")

    names = [path.name for path in store.list_sessions()]
    assert names == ["a-session", "b-session"]


def test_demo_produces_a_populated_archive(store: SessionStore, session_root: Path) -> None:
    """``demo`` creates content, updates metrics, and archives the result."""
    zip_path = store.demo()

    assert zip_path.parent == session_root
    assert zip_path.name.startswith("demo-")
    assert zip_path.suffix == ".zip"

    with zipfile.ZipFile(zip_path) as archive:
        assert set(archive.namelist()) == ALL_MEMBERS
        assert archive.read("transcript.txt").strip()
        assert archive.read("summary.md").strip()
        metrics = json.loads(archive.read("metrics.json"))
        assert metrics["steps"] == 2
        assert metrics["duration_ms"] == 1234


def test_root_is_created_on_demand(tmp_path: Path) -> None:
    """The sessions root is created even when it does not exist yet."""
    root = tmp_path / "deeply" / "nested" / "sessions"
    SessionStore(root=root)
    assert root.is_dir()
