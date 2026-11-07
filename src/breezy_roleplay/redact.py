"""Redaction of sensitive information for breezy-roleplay."""

from __future__ import annotations

import re

EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
BEARER_PATTERN = re.compile(r"\bBearer\s+[A-Za-z0-9._\-+/=]+", re.IGNORECASE)
API_KEY_PATTERN = re.compile(r"\b(?:ghp_|github_pat_|AKIA|sk-)[A-Za-z0-9_]{10,}\b")
LONG_HEX_PATTERN = re.compile(r"\b[0-9a-fA-F]{32,}\b")


def redact(text: str) -> str:
    """Replace emails, bearer tokens, API keys, and long hex strings."""
    text = EMAIL_PATTERN.sub("[REDACTED]", text)
    text = BEARER_PATTERN.sub("[REDACTED]", text)
    text = API_KEY_PATTERN.sub("[REDACTED]", text)
    return LONG_HEX_PATTERN.sub("[REDACTED]", text)
