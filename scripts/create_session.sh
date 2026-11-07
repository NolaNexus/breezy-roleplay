#!/usr/bin/env bash

# Simple helper to create a new session folder with required sub‑files
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <session-id>" >&2
  echo "Example: $0 session-20261107-demo" >&2
  exit 1
fi

SESSION_DIR="$PWD/sessions/$1"
mkdir -p "$SESSION_DIR"

touch "$SESSION_DIR/transcript.txt"
touch "$SESSION_DIR/summary.md"

echo "Created session directory: $SESSION_DIR"
""
