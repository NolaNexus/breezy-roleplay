#!/usr/bin/env bash
# End-to-end smoke test of the CLI in a scratch directory.
#
# Exercises create, metrics, structured logging, archive, and the zip layout the
# same way a user would. Writes a readable report and exits non-zero on the first
# failure so `error-to-issue.yml` can open an actionable issue.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT="${SMOKE_REPORT:-smoke-report.txt}"
WORK_DIR="$(mktemp -d)"
: >"$REPORT"

cleanup() {
  case "$WORK_DIR" in
    /tmp/* | /var/folders/*) rm -rf -- "$WORK_DIR" ;;
  esac
}
trap cleanup EXIT

log() {
  printf '%s\n' "$*" | tee -a "$REPORT"
}

fail() {
  log "FAIL: $*"
  log ""
  log "--- stderr ---"
  sed -n '1,200p' "$WORK_DIR/stderr.log" 2>/dev/null | tee -a "$REPORT" || true
  exit 1
}

log "smoke test: workdir=$WORK_DIR"
log "smoke test: python=$(python3 --version 2>&1)"
log ""

export PYTHONPATH="$ROOT_DIR/src"
export BREEZY_TRACE_ID="smoke-test"
unset BREEZY_METRICS_FILE

cd "$WORK_DIR"

log "step 1/5: create"
python3 -m breezy_roleplay create smoke-session 2>>"$WORK_DIR/stderr.log" || fail "create failed"
[[ -d sessions/smoke-session ]] || fail "session directory missing"

log "step 2/5: required files"
for name in transcript.txt summary.md metadata.json metrics.json; do
  [[ -f "sessions/smoke-session/$name" ]] || fail "missing $name"
  log "  ok $name"
done

log "step 3/5: metadata and metrics parse"
python3 - <<'PY' || fail "metadata/metrics are not valid JSON with the expected keys"
import json
from pathlib import Path

metadata = json.loads(Path("sessions/smoke-session/metadata.json").read_text())
metrics = json.loads(Path("sessions/smoke-session/metrics.json").read_text())
assert metadata["id"] == "smoke-session", metadata
assert metadata["schema_version"] == "1.0", metadata
assert metrics["created_at"] == metadata["created_at"], (metadata, metrics)
assert metrics["steps"] == 0 and metrics["duration_ms"] == 0, metrics
print("  ok metadata.json and metrics.json")
PY

log "step 4/5: duplicate create is rejected with exit 1"
set +e
python3 -m breezy_roleplay create smoke-session >/dev/null 2>>"$WORK_DIR/stderr.log"
status=$?
set -e
[[ "$status" -eq 1 ]] || fail "expected exit 1 for duplicate create, got $status"
[[ -f sessions/smoke-session/errors.json ]] || fail "errors.json was not written"
log "  ok exit 1 and errors.json present"

log "step 5/5: demo archives four flat members"
python3 -m breezy_roleplay demo >/dev/null 2>>"$WORK_DIR/stderr.log" || fail "demo failed"
zip_path="$(find sessions -maxdepth 1 -name 'demo-*.zip' -print -quit)"
[[ -n "$zip_path" ]] || fail "demo did not produce an archive"

members="$(unzip -Z1 "$zip_path" | sort)"
expected="$(printf '%s\n' metadata.json metrics.json summary.md transcript.txt)"
[[ "$members" == "$expected" ]] || fail "unexpected archive members: $members"

log "  ok $zip_path contains the four expected members"
log ""
log "smoke test: PASS"
