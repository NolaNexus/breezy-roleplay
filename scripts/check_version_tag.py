#!/usr/bin/env python3
"""Fail when the pushed tag does not match the version in pyproject.toml."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

PROJECT_FILE = Path("pyproject.toml")


def main(argv: list[str]) -> int:
    """Compare ``vX.Y.Z`` against ``project.version``."""
    if len(argv) != 2:
        print("usage: check_version_tag.py <tag>", file=sys.stderr)
        return 2

    tag = argv[1]
    tag_version = tag[1:] if tag.startswith("v") else tag
    project_version = tomllib.loads(PROJECT_FILE.read_text(encoding="utf-8"))["project"]["version"]

    if tag_version != project_version:
        print(
            f"tag {tag!r} resolves to {tag_version!r} but pyproject.toml declares "
            f"{project_version!r}",
            file=sys.stderr,
        )
        return 1

    print(f"tag and project version agree: {project_version}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
