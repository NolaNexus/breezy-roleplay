"""Error handling for breezy-roleplay."""

from __future__ import annotations

import json
import traceback
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .logging import Logger, get_logger

logger: Logger = get_logger(__name__)


def record_error(
    session_id: str,
    exc: BaseException,
    context: dict[str, Any] | None = None,
) -> Path | None:
    """Record an error with context in ``sessions/<session_id>/errors.json``."""
    session_dir = Path.cwd() / "sessions" / session_id
    if not session_dir.is_dir():
        logger.warning(
            "Session directory not found for error recording",
            event="errors.record.warning",
            session_id=session_id,
        )
        return None

    error_info: dict[str, Any] = {
        "timestamp": datetime.now(UTC).isoformat(),
        "error": {
            "type": type(exc).__name__,
            "message": str(exc),
        },
        "traceback": traceback.format_exc(),
    }
    if context:
        error_info["context"] = context

    errors_path = session_dir / "errors.json"
    errors_path.write_text(json.dumps(error_info, indent=2))
    logger.info(
        "Error recorded",
        event="errors.record",
        session_id=session_id,
        error_type=type(exc).__name__,
    )
    return errors_path
