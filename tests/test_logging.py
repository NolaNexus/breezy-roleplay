"""Tests for the structured logger."""

from __future__ import annotations

import json
import re

import pytest

from breezy_roleplay.logging import Logger, get_logger, get_trace_id

HEX32 = re.compile(r"^[0-9a-f]{32}$")


def parse_entries(raw: str) -> list[dict[str, object]]:
    """Parse each non-empty log line as a JSON object."""
    return [json.loads(line) for line in raw.splitlines() if line.strip()]


def test_get_trace_id_is_uuid_hex() -> None:
    """Without configuration a fresh UUID4 hex trace id is generated."""
    assert HEX32.match(get_trace_id()) is not None


def test_get_trace_id_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """``BREEZY_TRACE_ID`` is propagated so logs can be correlated."""
    monkeypatch.setenv("BREEZY_TRACE_ID", "abcdef1234567890")
    assert get_trace_id() == "abcdef1234567890"


def test_structured_log_entry_shape(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A structured entry carries level, logger, event, trace id, and message."""
    monkeypatch.setenv("BREEZY_FEATURE_STRUCTURED_LOGS", "true")
    monkeypatch.setenv("BREEZY_TRACE_ID", "trace-1")

    get_logger("test.module")("session started", event="session.create", session_id="abc")

    entries = parse_entries(capsys.readouterr().err)
    assert len(entries) == 1
    entry = entries[0]
    assert entry["level"] == "info"
    assert entry["logger"] == "test.module"
    assert entry["event"] == "session.create"
    assert entry["session_id"] == "abc"
    assert entry["message"] == "session started"
    assert entry["trace_id"] == "trace-1"
    assert isinstance(entry["timestamp"], str)


@pytest.mark.parametrize(
    ("method", "level"),
    [("debug", "debug"), ("info", "info"), ("warning", "warning"), ("error", "error")],
)
def test_levels_are_recorded(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    method: str,
    level: str,
) -> None:
    """Each convenience method records its own level."""
    monkeypatch.setenv("BREEZY_FEATURE_STRUCTURED_LOGS", "true")
    logger = get_logger("levels")
    getattr(logger, method)("message", event="level.test")

    entries = parse_entries(capsys.readouterr().err)
    assert [entry["level"] for entry in entries] == [level]


def test_message_and_sensitive_keys_are_redacted(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Secrets are stripped from the message and from sensitive keyword arguments."""
    monkeypatch.setenv("BREEZY_FEATURE_STRUCTURED_LOGS", "true")
    logger = get_logger("redaction")

    logger(
        "user test@example.com failed",
        event="auth.failure",
        token="Bearer abc123",
        detail="kept as-is",
    )

    entry = parse_entries(capsys.readouterr().err)[0]
    assert entry["message"] == "user [REDACTED] failed"
    assert entry["token"] == "[REDACTED]"
    assert entry["detail"] == "kept as-is"


def test_plain_text_fallback(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """With structured logs disabled the logger still emits a readable line."""
    monkeypatch.setenv("BREEZY_FEATURE_STRUCTURED_LOGS", "false")
    get_logger("plain").info("hello", event="ignored")

    output = capsys.readouterr().err
    assert output.strip() == "plain: hello"
    assert not output.lstrip().startswith("{")


def test_logger_is_callable() -> None:
    """``logger(...)`` is shorthand for ``logger.info(...)``."""
    assert callable(Logger("callable"))
