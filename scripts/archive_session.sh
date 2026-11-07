#!/usr/bin/env bash

# Archive an existing session directory into a zip file
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <session-id>" >&2
  echo "Example: $0 session-20261107-demo" >&2
  exit 1
fi

SESSION_DIR="$PWD/sessions/$1"
if [[ ! -d "$SESSION_DIR" ]]; then
  echo "Session directory not found: $SESSION_DIR" >&2
  exit 1
fi

ZIP_FILE="${SESSION_DIR}.zip"

echo "Zipping $SESSION_DIR into $ZIP_FILE"
# Simple zip; adjust if tools unavailable
zip -r "$ZIP_FILE" "$SESSION_DIR"

echo "Archive created: $ZIP_FILE"
""
