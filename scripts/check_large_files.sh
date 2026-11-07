#!/usr/bin/env bash
# Fail when a tracked text file grows past the size budget.
#
# Large files are hard to review, slow to clone, and usually a sign that
# generated output or a binary blob was committed by accident.

set -euo pipefail

MAX_BYTES="${MAX_FILE_BYTES:-262144}" # 256 KiB
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -d .git ]]; then
  echo "check_large_files: not a git repository, skipping" >&2
  exit 0
fi

failed=0
while IFS= read -r -d '' path; do
  # Skip anything that is not a regular file (submodule pointers, symlinks).
  [[ -f "$path" ]] || continue
  size="$(wc -c <"$path" | tr -d ' ')"
  if (( size > MAX_BYTES )); then
    printf 'check_large_files: %s is %s bytes (limit %s)\n' "$path" "$size" "$MAX_BYTES" >&2
    failed=1
  fi
done < <(git ls-files -z)

if (( failed )); then
  echo "check_large_files: commit smaller files, or store large assets elsewhere." >&2
  exit 1
fi

echo "check_large_files: all tracked files are within ${MAX_BYTES} bytes"
