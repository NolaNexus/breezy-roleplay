#!/usr/bin/env bash
# Require every TODO/FIXME/XXX comment marker to name an owner or an issue.
#
# An unowned TODO rots forever. Writing "TODO(#42)" or "TODO(nola)" makes the
# follow-up traceable, so this gate rejects bare markers. Only comment markers
# are inspected, so documentation prose that merely mentions the word is fine.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# A marker is acceptable when followed by "(owner)" or "(#123)".
marker='(^|[[:space:]])(#|//|/\*|\*|--|;)[[:space:]]*(TODO|FIXME|XXX)\b'
owned='(TODO|FIXME|XXX)\(#[0-9]+\)'
owned+='|(TODO|FIXME|XXX)\([A-Za-z0-9._@-]+\)'

mapfile -t files < <(
  git ls-files -z 2>/dev/null \
    | xargs -0 -r printf '%s\n' \
    | grep -Ev '(^|/)(node_modules|reports|\.venv)/' \
    | grep -E '\.(py|sh|ya?ml|toml|js|ts|tsx|jsx|cfg|ini|mk)$|(^|/)Makefile$' \
    || true
)

if (( ${#files[@]} == 0 )); then
  echo "check_todos: no tracked source files to scan"
  exit 0
fi

failed=0
while IFS= read -r match; do
  [[ -n "$match" ]] || continue
  printf 'check_todos: unowned marker -> %s\n' "$match" >&2
  failed=1
done < <(
  grep -nHE "$marker" -- "${files[@]}" 2>/dev/null \
    | grep -Ev "$owned" \
    || true
)

if (( failed )); then
  echo "check_todos: write 'TODO(owner)' or 'TODO(#issue)' so the follow-up is traceable." >&2
  exit 1
fi

echo "check_todos: every TODO/FIXME/XXX comment marker names an owner or issue"
