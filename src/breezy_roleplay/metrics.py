"""Metrics collection for breezy-roleplay."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

from .logging import Logger, get_logger

logger: Logger = get_logger(__name__)

BREEZY_SESSION_CREATED_TOTAL: Final = "breezy_session_created_total"
BREEZY_SESSION_ARCHIVE_SECONDS: Final = "breezy_session_archive_seconds"


class MetricsWriter:
    """Write session metrics JSON and optional Prometheus textfile metrics."""

    def __init__(self) -> None:
        self.metrics_file = os.getenv("BREEZY_METRICS_FILE")
        if self.metrics_file:
            Path(self.metrics_file).parent.mkdir(parents=True, exist_ok=True)

    def write_metrics_json(self, session_dir: Path, metrics: dict[str, Any]) -> None:
        """Write metrics JSON to the session directory."""
        metrics_path = session_dir / "metrics.json"
        metrics_path.write_text(json.dumps(metrics, indent=2))
        logger.debug(
            "Metrics written",
            event="metrics.write",
            session_dir=str(session_dir),
            metrics_path=str(metrics_path),
        )

    def write_create_metrics(self, session_id: str) -> None:
        """Record that a session was created."""
        if self.metrics_file:
            with open(self.metrics_file, "a", encoding="utf-8") as handle:
                handle.write(f"{BREEZY_SESSION_CREATED_TOTAL} 1\n")
        logger.debug(
            "Session created metrics recorded",
            event="metrics.create",
            session_id=session_id,
        )

    def write_archive_metrics(self, session_id: str) -> None:
        """Record archive metrics for a session."""
        if self.metrics_file:
            with open(self.metrics_file, "a", encoding="utf-8") as handle:
                handle.write(f"{BREEZY_SESSION_ARCHIVE_SECONDS} 0\n")
        logger.debug(
            "Session archive metrics recorded",
            event="metrics.archive",
            session_id=session_id,
            recorded_at=datetime.now(UTC).isoformat(),
        )
