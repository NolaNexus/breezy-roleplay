"""Tests for the branch-ruleset helper.

The GitHub API is stubbed so the tests stay offline and assert on the exact
request sequence the script issues.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from apply_ruleset import RULESET_FILE, find_ruleset, main, resolve_repo


def test_ruleset_file_is_valid_json() -> None:
    """The checked-in policy parses and names the branch it protects."""
    payload = json.loads(RULESET_FILE.read_text(encoding="utf-8"))
    assert payload["name"]
    assert payload["enforcement"] == "active"
    assert payload["conditions"]["ref_name"]["include"] == ["refs/heads/main"]


def test_ruleset_requires_status_checks() -> None:
    """The policy gates merges on the aggregate CI job and the security review."""
    payload = json.loads(RULESET_FILE.read_text(encoding="utf-8"))
    checks = next(rule for rule in payload["rules"] if rule["type"] == "required_status_checks")
    contexts = {check["context"] for check in checks["parameters"]["required_status_checks"]}
    assert contexts == {"CI status", "Security Review"}
    assert checks["parameters"]["strict_required_status_checks_policy"] is True


def test_ruleset_blocks_deletion_and_force_push() -> None:
    """Destructive history operations stay blocked."""
    payload = json.loads(RULESET_FILE.read_text(encoding="utf-8"))
    types = {rule["type"] for rule in payload["rules"]}
    assert {"deletion", "non_fast_forward", "required_linear_history"} <= types


def test_ruleset_bypass_is_pull_request_scoped() -> None:
    """Admins may merge without a reviewer, but cannot bypass checks by pushing."""
    payload = json.loads(RULESET_FILE.read_text(encoding="utf-8"))
    assert payload["bypass_actors"]
    for actor in payload["bypass_actors"]:
        assert actor["bypass_mode"] == "pull_request"


def test_find_ruleset_matches_by_name(monkeypatch: pytest.MonkeyPatch) -> None:
    """Existing rulesets are found by name so apply updates instead of duplicating."""
    monkeypatch.setattr(
        "apply_ruleset.gh_api",
        lambda method, endpoint, payload=None: [
            {"id": 1, "name": "Other"},
            {"id": 42, "name": "Protect main"},
        ],
    )
    assert find_ruleset("owner/repo", "Protect main") == 42
    assert find_ruleset("owner/repo", "Missing") is None


def test_find_ruleset_handles_empty_response(monkeypatch: pytest.MonkeyPatch) -> None:
    """An empty list from the API means no ruleset exists yet."""
    monkeypatch.setattr("apply_ruleset.gh_api", lambda *_args, **_kwargs: None)
    assert find_ruleset("owner/repo", "Protect main") is None


def test_resolve_repo_prefers_explicit_value() -> None:
    """The --repo flag wins over repository discovery."""
    assert resolve_repo("someone/else") == "someone/else"


def test_dry_run_prints_payload_without_calling_the_api(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """--dry-run must not touch the API."""

    def explode(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("API must not be called during a dry run")

    monkeypatch.setattr("apply_ruleset.gh_api", explode)
    assert main(["apply_ruleset.py", "--dry-run"]) == 0

    printed = json.loads(capsys.readouterr().out)
    assert printed["name"] == json.loads(Path(RULESET_FILE).read_text())["name"]


def test_apply_creates_then_updates(monkeypatch: pytest.MonkeyPatch) -> None:
    """A missing ruleset is created; a present one is updated in place."""
    calls: list[tuple[str, str]] = []
    payload = json.loads(RULESET_FILE.read_text(encoding="utf-8"))

    def fake_api(method: str, endpoint: str, body: dict[str, Any] | None = None) -> object:
        calls.append((method, endpoint))
        if method == "GET" and endpoint.endswith("/rulesets"):
            return []
        if method == "POST":
            return {"id": 7}
        if method == "GET":
            return payload
        return {}

    monkeypatch.setattr("apply_ruleset.gh_api", fake_api)
    assert main(["apply_ruleset.py", "--repo", "owner/repo"]) == 0
    assert ("POST", "repos/owner/repo/rulesets") in calls

    calls.clear()

    def fake_api_existing(method: str, endpoint: str, body: dict[str, Any] | None = None) -> object:
        calls.append((method, endpoint))
        if method == "GET" and endpoint.endswith("/rulesets"):
            return [{"id": 7, "name": payload["name"]}]
        if method == "GET":
            return payload
        return {}

    monkeypatch.setattr("apply_ruleset.gh_api", fake_api_existing)
    assert main(["apply_ruleset.py", "--repo", "owner/repo"]) == 0
    assert ("PUT", "repos/owner/repo/rulesets/7") in calls
    assert ("POST", "repos/owner/repo/rulesets") not in calls


def test_apply_fails_when_ruleset_is_not_active(monkeypatch: pytest.MonkeyPatch) -> None:
    """A disabled ruleset is reported as a failure rather than a success."""
    payload = json.loads(RULESET_FILE.read_text(encoding="utf-8"))
    disabled = {**payload, "enforcement": "disabled"}

    def fake_api(method: str, endpoint: str, body: dict[str, Any] | None = None) -> object:
        if method == "GET" and endpoint.endswith("/rulesets"):
            return []
        if method == "POST":
            return {"id": 7}
        return disabled

    monkeypatch.setattr("apply_ruleset.gh_api", fake_api)
    assert main(["apply_ruleset.py", "--repo", "owner/repo"]) == 1
