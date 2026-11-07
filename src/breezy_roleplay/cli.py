"""Command-line interface for breezy-roleplay."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .errors import record_error
from .session import SessionStore

EXIT_OK = 0
EXIT_FAILURE = 1


def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the ``breezy-roleplay`` command."""
    parser = argparse.ArgumentParser(
        prog="breezy-roleplay",
        description="Create, list, and archive roleplay session directories.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True, metavar="command")

    create_parser = subparsers.add_parser(
        "create",
        help="Create a new session directory",
        description="Create sessions/<id>/ with a transcript, summary, and metadata.",
    )
    create_parser.add_argument("session_id", help="Unique identifier for the session")

    archive_parser = subparsers.add_parser(
        "archive",
        help="Archive an existing session",
        description="Zip sessions/<id>/ into sessions/<id>.zip using relative paths.",
    )
    archive_parser.add_argument("session_id", help="Identifier of the session to archive")

    subparsers.add_parser("list", help="List all sessions")
    subparsers.add_parser(
        "demo",
        help="Create and archive a demonstration session",
        description="End-to-end smoke test of the create and archive paths.",
    )
    return parser


def _print_sessions(sessions: Sequence[Path]) -> None:
    """Print one session directory name per line, or a friendly empty message."""
    if not sessions:
        print("No sessions found")
        return
    for session in sessions:
        print(session.name)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    session_id: str | None = getattr(args, "session_id", None)

    try:
        store = SessionStore()
        if args.command == "create":
            store.create(session_id or "")
            print(f"Created session: {session_id}")
        elif args.command == "archive":
            store.archive(session_id or "")
            print(f"Archived session: {session_id}")
        elif args.command == "list":
            _print_sessions(store.list_sessions())
        elif args.command == "demo":
            print(f"Demo session created and archived at: {store.demo()}")
        else:  # pragma: no cover - argparse rejects unknown commands first
            parser.error(f"unknown command: {args.command}")
    except Exception as exc:
        if session_id:
            record_error(session_id, exc, {"command": args.command})
        print(f"Error: {exc}", file=sys.stderr)
        return EXIT_FAILURE
    return EXIT_OK
