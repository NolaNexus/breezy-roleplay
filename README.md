# Breezy Roleplay

A small, typed Python CLI for running and documenting role-play scenarios. It
owns one job well: creating, populating, and archiving session directories with
structured logs, metrics, and error capture attached.

- **Define** scenarios as Markdown files in `scenarios/`.
- **Run** a session directory in `sessions/<session-id>/` with a transcript,
  summary, metadata, and metrics.
- **Archive** it to `sessions/<session-id>.zip` with relative member paths.

## Prerequisites

- Python 3.11 or newer
- Node 20 or newer (for Markdown, duplication, and YAML tooling)
- `bash`, `git`, and `zip`/`unzip`

## Quick Start

```bash
git clone https://github.com/NolaNexus/breezy-roleplay.git
cd breezy-roleplay

make setup   # virtualenv, dev dependencies, editable install, pre-commit hooks
make demo    # create and archive a demonstration session
make check   # everything CI runs
```

## Commands

| Command             | Description                                                     |
| ------------------- | --------------------------------------------------------------- |
| `make setup`        | Create `.venv`, install dev dependencies, install pre-commit    |
| `make lint`         | Run Ruff                                                        |
| `make format`       | Apply Ruff formatting                                           |
| `make format-check` | Verify formatting without writing                               |
| `make type`         | Run MyPy in strict mode                                         |
| `make test`         | Run the test suite in parallel                                  |
| `make coverage`     | Run tests with branch coverage and the 85% gate                 |
| `make quality`      | Large files, complexity, TODO ownership, dead code, duplication |
| `make docs`         | Regenerate `docs/scenarios.md`                                  |
| `make security`     | Run the local Semgrep review                                    |
| `make demo`         | Create and archive a demonstration session                      |
| `make check`        | Everything above that CI runs                                   |

## CLI

```bash
python -m breezy_roleplay create <session-id>
python -m breezy_roleplay archive <session-id>
python -m breezy_roleplay list
python -m breezy_roleplay demo
```

Exit codes are `0` for success, `1` for a rejected operation (with the reason on
stderr and a traceback recorded in `sessions/<session-id>/errors.json`), and `2`
for a usage error.

The shell helpers `scripts/create_session.sh` and `scripts/archive_session.sh`
are thin wrappers around the same commands, so the on-disk layout is defined in
exactly one place.

## Session Layout

```text
sessions/<session-id>/
├── transcript.txt   # written by whatever runs the scenario
├── summary.md       # human-readable summary
├── metadata.json    # id, created_at, schema_version
├── metrics.json     # created_at, duration_ms, steps
└── errors.json      # only present after a failed command
sessions/<session-id>.zip
```

Archiving never deletes the session directory and always writes flat, relative
member names so the archive extracts safely anywhere.

## Documentation

- [AGENTS.md](AGENTS.md): contributor and agent workflow, conventions, policies
- [docs/architecture.md](docs/architecture.md): components and session flow
- [docs/observability.md](docs/observability.md): logs, metrics, trace IDs, CI data
- [docs/runbooks/session-recovery.md](docs/runbooks/session-recovery.md): failure recovery
- [docs/scenarios.md](docs/scenarios.md): generated scenario index
- [roadmap.md](roadmap.md): planned work

## Continuous Integration

`.github/workflows/ci.yml` runs seven jobs on every push and pull request: lint,
type, test (with coverage and JUnit artifacts), quality, docs drift, workflow
syntax (`actionlint`), and `pre-commit`. `.github/workflows/security-review.yml`
runs Semgrep on every push to `main`, on pull requests, and weekly, uploading
SARIF to code scanning.

`actionlint` and `yamllint` validate workflow files, and `git-cliff` generates
release notes from Conventional Commits on tag pushes.

## Security

The security review runs automatically. To reproduce it locally:

```bash
python3 -m pip install -r requirements-security.txt
make security
```

The readable report is written to `reports/security-review.txt`. Never commit a
real token; `.env.example` lists the variables the CLI understands.

## License

MIT
