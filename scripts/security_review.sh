#!/usr/bin/env bash
# Run the same Semgrep security review used by CI and write a readable report.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v semgrep >/dev/null 2>&1; then
  echo "semgrep is required. Install it with:" >&2
  echo "  python3 -m pip install -r requirements-security.txt" >&2
  exit 1
fi

mkdir -p reports

semgrep scan \
  --config p/default \
  --config p/secrets \
  --metrics=off \
  --text > reports/security-review.txt

semgrep scan \
  --config p/default \
  --config p/secrets \
  --metrics=off \
  --sarif --output reports/security-review.sarif

echo "Security review written to reports/security-review.txt"
