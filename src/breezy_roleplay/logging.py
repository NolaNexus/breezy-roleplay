"""Structured logging for breezy-roleplay."""

from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import UTC, datetime
from typing import Any

from .redact import redact

_SENSITIVE_KEYS = {"email", "token", "api_key", "authorization", "password", "secret"}


def get_trace_id() -> str:
    """Return the trace ID from the environment or generate a new one."""
    trace_id = os.getenv("BREEZY_TRACE_ID")
    return trace_id or uuid.uuid4().hex


def _structured_logs_enabled() -> bool:
    value = os.getenv("BREEZY_FEATURE_STRUCTURED_LOGS", "true").strip().lower()
    return value in ("1", "true", "yes", "on")


class Logger:
    """Small JSON logger used by the CLI and library code."""

    def __init__(self, name: str) -> None:
        self.name = name

    def __call__(self, message: str, **kwargs: Any) -> None:
        """Allow ``logger("message")`` as a shorthand for ``logger.info``."""
        self.info(message, **kwargs)

    def _emit(self, level: str, message: str, **kwargs: Any) -> None:
        if not _structured_logs_enabled():
            print(f"{self.name}: {message}", file=sys.stderr)
            return

        event = kwargs.pop("event", "log")
        session_id = kwargs.pop("session_id", None)
        entry: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": level,
            "logger": self.name,
            "event": event,
            "trace_id": get_trace_id(),
            "message": redact(message),
        }
        if session_id is not None:
            entry["session_id"] = session_id
        for key, value in kwargs.items():
            entry[key] = redact(str(value)) if key in _SENSITIVE_KEYS else value
        print(json.dumps(entry, sort_keys=True), file=sys.stderr)

    def debug(self, message: str, **kwargs: Any) -> None:
        self._emit("debug", message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        self._emit("info", message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        self._emit("warning", message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        self._emit("error", message, **kwargs)


def get_logger(name: str) -> Logger:
    """Return a logger bound to ``name``."""
    return Logger(name)
