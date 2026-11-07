#!/usr/bin/env bash
# Thin wrapper around `python -m breezy_roleplay archive`.
#
# Archive layout is owned by the Python package so the shell helpers and the CLI
# cannot drift apart. This script only resolves the repository root and forwards
# its arguments.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${ROOT_DIR}/src${PYTHONPATH:+:${PYTHONPATH}}"

exec python3 -m breezy_roleplay archive "$@"
