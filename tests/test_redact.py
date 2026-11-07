"""Tests for the redaction helpers.

The token fixtures are assembled at runtime rather than pasted as literals so the
repository never contains anything that looks like a live credential.
"""

from __future__ import annotations

import pytest

from breezy_roleplay.redact import redact

REDACTED = "[REDACTED]"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Contact me at test@example.com", f"Contact me at {REDACTED}"),
        ("a@b.com and c@d.org", f"{REDACTED} and {REDACTED}"),
        ("user+tag@sub.example.co.uk", REDACTED),
        ("not-an-email", "not-an-email"),
        ("hello@world", "hello@world"),
    ],
)
def test_redact_email(text: str, expected: str) -> None:
    """Email addresses are replaced, near-misses are left alone."""
    assert redact(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Authorization: Bearer abc123", f"Authorization: {REDACTED}"),
        ("Bearer abc123", REDACTED),
        ("Bearer   abc123", REDACTED),
        ("bearer abc123", REDACTED),
        ("Bearerabc123", "Bearerabc123"),
        ("Bearer_Token: xyz789", "Bearer_Token: xyz789"),
    ],
)
def test_redact_bearer_token(text: str, expected: str) -> None:
    """Bearer credentials are replaced; an underscored name is not a token."""
    assert redact(text) == expected


@pytest.mark.parametrize(
    "token",
    [
        "ghp_" + "Zq8" * 12,
        "github_pat_" + "Zq8" * 10,
        "AKIA" + "Zq8".upper() * 6,
        "sk-" + "zq8" * 7,
    ],
)
def test_redact_api_keys(token: str) -> None:
    """Known provider token prefixes are replaced."""
    assert redact(token) == REDACTED
    assert redact(f"Keys: {token} and {token}") == f"Keys: {REDACTED} and {REDACTED}"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Hash: " + "abcdef0123456789" * 2, f"Hash: {REDACTED}"),
        ("Hash: " + "abcdef0123456789" * 3, f"Hash: {REDACTED}"),
        ("ABCDEF0123456789" * 2, REDACTED),
        ("Short: abcdef01234567", "Short: abcdef01234567"),
    ],
)
def test_redact_long_hex(text: str, expected: str) -> None:
    """Hex digests of 32+ characters are replaced; shorter runs are kept."""
    assert redact(text) == expected


def test_redact_combined() -> None:
    """Every pattern is applied to the same string."""
    token = "sk-" + "zq8" * 7
    text = (
        f"Email: test@example.com, Token: Bearer abc123, "
        f"Key: {token}, Hash: {'abcdef0123456789' * 2}"
    )
    assert redact(text) == (
        f"Email: {REDACTED}, Token: {REDACTED}, Key: {REDACTED}, Hash: {REDACTED}"
    )


def test_redact_is_idempotent() -> None:
    """Redacting already-redacted text changes nothing."""
    once = redact("Contact test@example.com or Bearer abc123")
    assert redact(once) == once


def test_redact_no_false_positives() -> None:
    """Ordinary prose passes through untouched."""
    text = "Hello world! This is a normal sentence with numbers 123 and symbols @#$%^&*()."
    assert redact(text) == text
