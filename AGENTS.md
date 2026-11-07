# AGENTS.md

Guidance for humans and coding agents working in this repository. If something
here disagrees with the code, the code wins: fix this file.

## Purpose

A small, typed Python CLI that creates and archives role-play session
directories, with structured logging, metrics, and error capture attached. There
is no server, database, or network dependency.

## Layout

- `src/breezy_roleplay/`: the package. All session behaviour lives here.
  - `cli.py`: `create`, `archive`, `list`, `demo` subcommands and exit codes.
  - `session.py`: `SessionStore`, the single owner of the on-disk layout.
  - `logging.py`: JSON logs on stderr with redaction.
  - `metrics.py`: session `metrics.json` and an optional Prometheus textfile.
  - `errors.py`: `sessions/<id>/errors.json` capture for failed commands.
  - `features.py`: environment-driven feature flags.
  - `redact.py`: email, bearer-token, API-key, and hex-digest redaction.
- `tests/`: unit tests plus `tests/integration/` subprocess tests that drive the
  real `python -m breezy_roleplay` entry point.
- `scenarios/`: Markdown scenario definitions.
- `sessions/`: runtime output, git-ignored except for the directory itself.
- `docs/`: architecture, observability, runbooks, generated scenario index.
- `scripts/`: quality gates and thin CLI wrappers.
- `.github/`: CI, security review, release, templates, labels, CODEOWNERS.
- `.factory/skills/roleplay-session/`: agent skill for the session lifecycle.

## Prerequisites

Python 3.11+, Node 20+, `bash`, and `git`.

## Setup

```bash
make setup
```

This creates `.venv`, installs `requirements-dev.txt`, installs the package in
editable mode, and installs the pre-commit hooks. Activate the environment with
`source .venv/bin/activate` or call `.venv/bin/<tool>` directly.

## Commands

Run `make help` for the full list. The ones that matter:

- `make lint`: Ruff
- `make format` / `make format-check`: Ruff formatting
- `make type`: MyPy, strict mode
- `make test`: pytest with `-n auto`
- `make coverage`: pytest with branch coverage and the 85% gate
- `make quality`: large files, complexity, TODO ownership, vulture, jscpd
- `make docs`: regenerate `docs/scenarios.md`
- `make security`: local Semgrep review
- `make check`: lint, format-check, type, coverage, quality, docs, then verify
  `docs/scenarios.md` is unchanged

## CLI

```bash
python -m breezy_roleplay create <session-id>
python -m breezy_roleplay archive <session-id>
python -m breezy_roleplay list
python -m breezy_roleplay demo
```

Exit codes: `0` success, `1` rejected operation, `2` usage error. Session IDs
must match `[A-Za-z0-9._-]+`; anything else is rejected before the filesystem is
touched.

`scripts/create_session.sh` and `scripts/archive_session.sh` forward to these
commands. Do not reimplement the layout in Bash.

## Session Lifecycle

1. `create` writes `sessions/<id>/` with empty `transcript.txt` and
   `summary.md`, plus `metadata.json` (`id`, `created_at`, `schema_version`) and
   `metrics.json` (`created_at`, `duration_ms`, `steps`).
2. The scenario runner appends to `transcript.txt` and writes `summary.md`.
3. `archive` writes `sessions/<id>.zip` containing `transcript.txt`,
   `summary.md`, `metadata.json`, and `metrics.json` as flat relative members.
   Set `BREEZY_FEATURE_ARCHIVE_MANIFEST=false` to omit the last two.
4. A failed command appends a traceback to `sessions/<id>/errors.json` when the
   session directory exists.

## Scenario Format

Markdown with three fields `scripts/generate_scenario_index.sh` reads:

```markdown
# Scenario Title

**Title:** A short, human-readable title

**Participants:**

- First participant
- Second participant

**Setting:** Where the scene takes place
```

Add the file to `scenarios/` and run `make docs`.

## Conventions

- Python: `snake_case` functions and variables, `PascalCase` classes,
  `UPPER_SNAKE` constants, full type annotations (MyPy strict covers `src` and
  `tests`).
- Keep functions under complexity 10 and 60 lines; `make quality` enforces it.
- Bash: `snake_case` variables, `set -euo pipefail`, quote expansions,
  lowercase-and-braces style enforced by ShellCheck.
- Markdown: kebab-case filenames, Prettier-formatted, Markdownlint-clean.
- Commit messages follow Conventional Commits (`feat:`, `fix:`, `docs:`,
  `test:`, `ci:`, `chore:`); `cliff.toml` groups them for release notes.

## Dependencies

- Runtime dependencies are declared in `pyproject.toml` (`dependencies`, empty
  today) and pinned in `requirements*.txt`.
- Dev tooling is a PEP 735 `dev` dependency group, mirrored in
  `requirements-dev.txt` with exact pins. `deptry` fails the build on drift.
- Dependabot opens grouped weekly updates for pip, npm, and GitHub Actions.
- Pin GitHub Actions by commit SHA with a trailing `# vX` comment.

## Secrets

- Never commit `.env` or credentials. `.env.example` is the template.
- `BREEZY_TRACE_ID` carries a trace identifier value, not a path. Never put a
  real token in it: logs are redacted, but the value is echoed in every entry.
- CI secrets go through GitHub Actions secrets, never workflow files.

## Testing

- pytest, files named `test_*.py` under `tests/`.
- `tests/integration/` drives the CLI as a subprocess; mark new end-to-end tests
  with `@pytest.mark.integration`.
- Coverage gate is 85% with branch coverage; do not lower it to pass.
- Every bug fix gets a regression test that fails before the fix.

## Pull Requests

1. Branch from `main`.
2. Run `make check` before pushing.
3. Describe the change, the motivation, and how it was verified. Link the issue.
4. All CI jobs and the Semgrep review must pass; squash merge is preferred.

## Where to Look

- Runbooks: `docs/runbooks/`
- Observability: `docs/observability.md`
- Architecture: `docs/architecture.md`
- Backlog: `roadmap.md` and GitHub issues
