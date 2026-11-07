"""Session management for breezy-roleplay."""

from __future__ import annotations

import json
import re
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from .features import ARCHIVE_MANIFEST
from .logging import Logger, get_logger
from .metrics import MetricsWriter

logger: Logger = get_logger(__name__)

_SAFE_ID = re.compile(r"[A-Za-z0-9._-]+")
_ARCHIVE_FILES = ("transcript.txt", "summary.md")


class SessionStore:
    """Manage session directories and archives."""

    def __init__(self, root: Path | None = None) -> None:
        if root is None:
            root = Path.cwd() / "sessions"
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.metrics_writer = MetricsWriter()

    def _validate_session_id(self, session_id: str) -> None:
        """Reject empty, absolute, traversing, or unsafe session IDs."""
        if not session_id:
            raise ValueError("Session ID must not be empty")
        if Path(session_id).is_absolute():
            raise ValueError("Session ID must not be an absolute path")
        if ".." in session_id or session_id.startswith("/") or "\\" in session_id:
            raise ValueError("Session ID must not contain path traversal")
        if _SAFE_ID.fullmatch(session_id) is None:
            raise ValueError(
                "Session ID may only contain alphanumeric, hyphen, underscore, and dot"
            )

    def create(self, session_id: str) -> Path:
        """Create a session directory with transcript, summary, and metadata."""
        self._validate_session_id(session_id)
        session_dir = self.root / session_id
        if session_dir.exists():
            raise FileExistsError(f"Session directory already exists: {session_dir}")

        session_dir.mkdir(parents=True)
        (session_dir / "transcript.txt").touch()
        (session_dir / "summary.md").touch()

        now = datetime.now(UTC).isoformat()
        metadata = {
            "id": session_id,
            "created_at": now,
            "schema_version": "1.0",
        }
        (session_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

        metrics = {"created_at": now, "duration_ms": 0, "steps": 0}
        self.metrics_writer.write_metrics_json(session_dir, metrics)
        self.metrics_writer.write_create_metrics(session_id)

        logger.info(
            "Session created",
            event="session.create",
            session_id=session_id,
            session_dir=str(session_dir),
        )
        return session_dir

    def archive(self, session_id: str) -> Path:
        """Archive a session directory into a zip file with relative members."""
        self._validate_session_id(session_id)
        session_dir = self.root / session_id
        if not session_dir.is_dir():
            raise FileNotFoundError(f"Session directory not found: {session_dir}")

        zip_path = self.root / f"{session_id}.zip"
        if zip_path.exists():
            zip_path.unlink()

        files_to_include = list(_ARCHIVE_FILES)
        if ARCHIVE_MANIFEST:
            files_to_include.extend(["metadata.json", "metrics.json"])

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for file_name in files_to_include:
                file_path = session_dir / file_name
                if file_path.is_file():
                    zip_file.write(file_path, arcname=file_name)
                else:
                    logger.warning(
                        "Expected file not found in session",
                        event="session.archive.warning",
                        session_id=session_id,
                        missing_file=file_name,
                    )

        self.metrics_writer.write_archive_metrics(session_id)
        logger.info(
            "Session archived",
            event="session.archive",
            session_id=session_id,
            zip_path=str(zip_path),
        )
        return zip_path

    def list_sessions(self) -> list[Path]:
        """List all session directories, sorted by name."""
        if not self.root.exists():
            return []
        return sorted(path for path in self.root.iterdir() if path.is_dir())

    def demo(self) -> Path:
        """Create, populate, and archive a demonstration session."""
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S%f")
        session_id = f"demo-{timestamp}"
        session_dir = self.create(session_id)

        (session_dir / "transcript.txt").write_text(
            "User: Hello!\nAssistant: Greetings! How can I assist you today?\n"
        )
        (session_dir / "summary.md").write_text(
            "# Demo Session Summary\n\n"
            "This is a demonstration session created by the breezy-roleplay CLI.\n"
        )

        metrics_file = session_dir / "metrics.json"
        metrics = json.loads(metrics_file.read_text())
        metrics["duration_ms"] = 1234
        metrics["steps"] = 2
        metrics_file.write_text(json.dumps(metrics, indent=2))

        return self.archive(session_id)
