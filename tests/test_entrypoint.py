"""Tests for the ``python -m breezy_roleplay`` entry point."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

import pytest


def test_module_entrypoint_forwards_exit_code(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Running the package as a module delegates to the CLI and exits with its code."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["breezy-roleplay", "list"])

    with pytest.raises(SystemExit) as exc_info:
        runpy.run_module("breezy_roleplay", run_name="__main__")

    assert exc_info.value.code == 0
    assert (tmp_path / "sessions").is_dir()


def test_module_entrypoint_propagates_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A failing command makes the module entry point exit non-zero."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["breezy-roleplay", "archive", "missing"])

    with pytest.raises(SystemExit) as exc_info:
        runpy.run_module("breezy_roleplay", run_name="__main__")

    assert exc_info.value.code == 1
