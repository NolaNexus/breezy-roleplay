"""Tests for :mod:`breezy_roleplay.metrics`."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from breezy_roleplay.metrics import (
    BREEZY_SESSION_ARCHIVE_SECONDS,
    BREEZY_SESSION_CREATED_TOTAL,
    MetricsWriter,
)


def test_write_metrics_json(tmp_path: Path) -> None:
    """Metrics are written as pretty-printed JSON inside the session directory."""
    writer = MetricsWriter()
    writer.write_metrics_json(tmp_path, {"steps": 3})

    assert json.loads((tmp_path / "metrics.json").read_text()) == {"steps": 3}


def test_prometheus_textfile_is_appended(metrics_file: Path) -> None:
    """The textfile collector format records one sample per event."""
    writer = MetricsWriter()

    writer.write_create_metrics("abc")
    writer.write_archive_metrics("abc")

    assert metrics_file.read_text().splitlines() == [
        f"{BREEZY_SESSION_CREATED_TOTAL} 1",
        f"{BREEZY_SESSION_ARCHIVE_SECONDS} 0",
    ]


def test_writer_creates_parent_directory(metrics_file: Path) -> None:
    """A nested ``BREEZY_METRICS_FILE`` path is created on demand."""
    assert not metrics_file.parent.exists()
    MetricsWriter()
    assert metrics_file.parent.is_dir()


def test_writer_without_metrics_file_is_a_noop(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Without ``BREEZY_METRICS_FILE`` no file is created anywhere."""
    monkeypatch.delenv("BREEZY_METRICS_FILE", raising=False)
    writer = MetricsWriter()

    writer.write_create_metrics("abc")
    writer.write_archive_metrics("abc")

    assert list(tmp_path.iterdir()) == []
