#!/usr/bin/env bash
# Enforce complexity and function-length budgets for the Python package.
#
# Ruff already fails the build on cyclomatic complexity > 10 (C901). This gate
# adds two things ruff is not configured for here: a readable report of the
# worst offenders, and a hard cap on function length, which is the usual
# early warning sign that a function is doing too much.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

MAX_COMPLEXITY="${MAX_COMPLEXITY:-10}"
MAX_FUNCTION_LINES="${MAX_FUNCTION_LINES:-60}"

exec python3 - "$MAX_COMPLEXITY" "$MAX_FUNCTION_LINES" <<'PY'
"""Report cyclomatic complexity and function length for Python sources."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

DECISION_NODES = (
    ast.If,
    ast.For,
    ast.AsyncFor,
    ast.While,
    ast.IfExp,
    ast.ExceptHandler,
)


def cyclomatic_complexity(node: ast.AST) -> int:
    """Return the McCabe complexity of a function body (baseline of 1).

    Counted the same way the ``mccabe`` package does: ``if``/``for``/``while``/
    ``except``/ternaries, each boolean operator, each ``match`` case, and each
    comprehension ``if``. ``assert`` and ``with`` are not branches.
    """
    complexity = 1
    stack = list(ast.iter_child_nodes(node))
    while stack:
        child = stack.pop()
        if isinstance(child, DECISION_NODES):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
        elif isinstance(child, ast.Match):
            complexity += len(child.cases)
        elif isinstance(child, ast.comprehension):
            complexity += len(child.ifs)
        stack.extend(ast.iter_child_nodes(child))
    return complexity


def main() -> int:
    max_complexity = int(sys.argv[1])
    max_lines = int(sys.argv[2])

    files = (
        sorted(Path("src").rglob("*.py"))
        + sorted(Path("tests").rglob("*.py"))
        + sorted(Path("scripts").rglob("*.py"))
    )
    if not files:
        print("check_complexity: no Python sources found", file=sys.stderr)
        return 0

    offenders: list[str] = []
    ranked: list[tuple[int, str]] = []

    for path in files:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            complexity = cyclomatic_complexity(node)
            end = node.end_lineno or node.lineno
            length = end - node.lineno + 1
            label = f"{path}:{node.lineno} {node.name}"
            ranked.append((complexity, f"{complexity:>3}  {length:>3}  {label}"))
            if complexity > max_complexity:
                offenders.append(f"{label} has complexity {complexity} (max {max_complexity})")
            if length > max_lines:
                offenders.append(f"{label} spans {length} lines (max {max_lines})")

    ranked.sort(reverse=True)
    print("Most complex functions (complexity, lines, location):")
    for _, row in ranked[:10]:
        print(f"  {row}")

    if offenders:
        print("\ncheck_complexity: budget exceeded", file=sys.stderr)
        for offender in offenders:
            print(f"  - {offender}", file=sys.stderr)
        return 1

    print(
        f"\ncheck_complexity: {len(ranked)} functions within "
        f"complexity <= {max_complexity} and length <= {max_lines}"
    )
    return 0


sys.exit(main())
PY
