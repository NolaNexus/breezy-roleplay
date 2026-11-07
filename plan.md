# Project Plan - Breezy Roleplay Sessions

## Goal

Keep a lightweight, reproducible repository structure that makes creating,
running, recording, and sharing role-play scenarios straightforward, with the
same quality gates a production service would have.

## Current State

The scaffolding described in the original plan is complete. What exists today:

```text
├── README.md                     # Overview and quick start
├── AGENTS.md                     # Contributor and agent workflow
├── plan.md                       # This file
├── roadmap.md                    # Planned work
├── CHANGELOG.md                  # Release history
├── scenarios/                    # Source files for each scenario
│   └── example.md                # Sample scenario
├── sessions/                     # Result artifacts for executed sessions (git-ignored)
│   └── <session-id>/             # transcript.txt, summary.md, metadata.json, metrics.json
├── src/breezy_roleplay/          # Typed Python package that owns the session layout
│   ├── cli.py                    # create / archive / list / demo
│   ├── session.py                # SessionStore
│   ├── logging.py                # Structured JSON logging with redaction
│   ├── metrics.py                # Prometheus textfile metrics
│   ├── errors.py                 # errors.json capture per session
│   ├── features.py               # Environment-driven feature flags
│   └── redact.py                 # Secret redaction helpers
├── tests/                        # Unit tests and subprocess integration tests
├── scripts/                      # Quality gates and thin CLI wrappers
├── docs/                         # Architecture, observability, runbooks, scenario index
└── .github/                      # CI, security review, release, templates, labels
```

## Status Against the Original Deliverables

1. **Directory layout** - Done.
2. **Scenario files** - Done: `scenarios/example.md`, indexed in `docs/scenarios.md`.
3. **Automation scripts** - Done: `scripts/create_session.sh` and
   `scripts/archive_session.sh` are thin wrappers around
   `python -m breezy_roleplay create|archive`, so the layout lives in one place.
4. **Documentation** - Done: `README.md`, `AGENTS.md`, `docs/`, and runbooks.
5. **CI** - Done: `.github/workflows/ci.yml` runs lint, type, test, coverage,
   quality, docs, and pre-commit jobs; `security-review.yml` runs Semgrep.

## Next Actions

Open work is tracked in [`roadmap.md`](roadmap.md) and in GitHub issues rather
than in this file, so there is a single backlog.
