"""Tests for the feature-flag helpers."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

from breezy_roleplay import features
from breezy_roleplay.features import parse_bool

FEATURES_PATH = Path(features.__file__)
FLAG_ENV_VARS = (
    "BREEZY_FEATURE_ARCHIVE_MANIFEST",
    "BREEZY_FEATURE_STRUCTURED_LOGS",
)


@pytest.mark.parametrize(
    ("value", "default", "expected"),
    [
        (None, False, False),
        (None, True, True),
        ("true", False, True),
        ("TRUE", False, True),
        ("True", False, True),
        ("1", False, True),
        ("yes", False, True),
        ("on", False, True),
        ("false", True, False),
        ("FALSE", True, False),
        ("0", True, False),
        ("no", True, False),
        ("off", True, False),
        ("  true  ", False, True),
        ("something", False, False),
        ("something", True, True),
        ("", False, False),
    ],
)
def test_parse_bool(value: str | None, default: bool, expected: bool) -> None:
    """Accepted spellings are parsed; anything else falls back to the default."""
    assert parse_bool(value, default=default) is expected


def load_features(monkeypatch: pytest.MonkeyPatch, **env: str) -> ModuleType:
    """Import ``features`` fresh so module-level flags re-read the environment."""
    for name in FLAG_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    for name, value in env.items():
        monkeypatch.setenv(name, value)

    spec = importlib.util.spec_from_file_location("features_under_test", FEATURES_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_flags_default_to_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Both flags ship enabled when nothing is configured."""
    module = load_features(monkeypatch)
    assert module.ARCHIVE_MANIFEST is True
    assert module.STRUCTURED_LOGS is True


def test_flags_can_be_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Each flag honours its environment variable."""
    module = load_features(
        monkeypatch,
        BREEZY_FEATURE_ARCHIVE_MANIFEST="false",
        BREEZY_FEATURE_STRUCTURED_LOGS="0",
    )
    assert module.ARCHIVE_MANIFEST is False
    assert module.STRUCTURED_LOGS is False


def test_flags_can_be_enabled_explicitly(monkeypatch: pytest.MonkeyPatch) -> None:
    """Explicit truthy values keep the flags on."""
    module = load_features(
        monkeypatch,
        BREEZY_FEATURE_ARCHIVE_MANIFEST="yes",
        BREEZY_FEATURE_STRUCTURED_LOGS="on",
    )
    assert module.ARCHIVE_MANIFEST is True
    assert module.STRUCTURED_LOGS is True


def test_unknown_flag_value_uses_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """A typo does not silently disable a flag that defaults to on."""
    module = load_features(monkeypatch, BREEZY_FEATURE_ARCHIVE_MANIFEST="maybe")
    assert module.ARCHIVE_MANIFEST is True
