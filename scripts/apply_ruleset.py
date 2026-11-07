#!/usr/bin/env python3
"""Apply the branch ruleset checked in at .github/rulesets/main.json.

The ruleset is version controlled so the protection policy is reviewable and
reproducible instead of living only in the GitHub UI. This script is idempotent:
it creates the ruleset when it is missing and updates it in place otherwise.

Usage:
    python scripts/apply_ruleset.py [--repo owner/name] [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

RULESET_FILE = Path(__file__).resolve().parents[1] / ".github" / "rulesets" / "main.json"


def gh_api(method: str, endpoint: str, payload: dict[str, Any] | None = None) -> Any:
    """Call the GitHub REST API through the authenticated gh CLI."""
    command = ["gh", "api", "--method", method, endpoint]
    if payload is not None:
        command += ["--input", "-"]
    result = subprocess.run(
        command,
        input=json.dumps(payload) if payload is not None else None,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"{method} {endpoint} failed: {result.stderr.strip()}")
    return json.loads(result.stdout) if result.stdout.strip() else None


def resolve_repo(explicit: str | None) -> str:
    """Return ``owner/name`` from the flag or from the default gh repository."""
    if explicit:
        return explicit
    result = subprocess.run(
        ["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"cannot resolve repository: {result.stderr.strip()}")
    return result.stdout.strip()


def find_ruleset(repo: str, name: str) -> int | None:
    """Return the id of the ruleset with ``name``, or None when absent."""
    rulesets = gh_api("GET", f"repos/{repo}/rulesets") or []
    for ruleset in rulesets:
        if ruleset.get("name") == name:
            return int(ruleset["id"])
    return None


def main(argv: list[str]) -> int:
    """Create or update the ruleset and report what changed."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="owner/name; defaults to the current gh repository")
    parser.add_argument("--dry-run", action="store_true", help="print the payload only")
    args = parser.parse_args(argv[1:])

    payload = json.loads(RULESET_FILE.read_text(encoding="utf-8"))
    if args.dry_run:
        print(json.dumps(payload, indent=2))
        return 0

    repo = resolve_repo(args.repo)
    ruleset_id = find_ruleset(repo, payload["name"])

    if ruleset_id is None:
        created = gh_api("POST", f"repos/{repo}/rulesets", payload)
        ruleset_id = int(created["id"])
        print(f"created ruleset {payload['name']!r} (id {ruleset_id}) on {repo}")
    else:
        gh_api("PUT", f"repos/{repo}/rulesets/{ruleset_id}", payload)
        print(f"updated ruleset {payload['name']!r} (id {ruleset_id}) on {repo}")

    # Re-read by id: the list endpoint omits rule details on some plan tiers.
    applied = gh_api("GET", f"repos/{repo}/rulesets/{ruleset_id}")
    if applied.get("enforcement") != "active":
        print("ruleset is not active after apply", file=sys.stderr)
        return 1

    rule_types = ", ".join(rule["type"] for rule in applied["rules"])
    print(f"enforcement: {applied['enforcement']}; rules: {rule_types}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
