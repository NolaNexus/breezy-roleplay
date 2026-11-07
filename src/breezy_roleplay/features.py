"""Feature flags for breezy-roleplay."""

from __future__ import annotations

import os


def parse_bool(value: str | None, default: bool = False) -> bool:
    """Parse a string as a boolean, with a default if the value is None or empty."""
    if value is None:
        return default
    value = value.strip().lower()
    if value in ("1", "true", "yes", "on"):
        return True
    if value in ("0", "false", "no", "off"):
        return False
    # If the value is not recognized, return the default
    return default


# Feature flags
ARCHIVE_MANIFEST = parse_bool(os.getenv("BREEZY_FEATURE_ARCHIVE_MANIFEST"), default=True)
STRUCTURED_LOGS = parse_bool(os.getenv("BREEZY_FEATURE_STRUCTURED_LOGS"), default=True)
