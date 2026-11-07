# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-11-07

### Added

- Typed `breezy_roleplay` package with a `create`, `archive`, `list`, and `demo`
  CLI, `SessionStore` owning the on-disk layout, and exit codes `0`/`1`/`2`.
- Structured JSON logging on stderr with trace IDs, secret redaction, and a
  plain-text fallback controlled by `BREEZY_FEATURE_STRUCTURED_LOGS`.
- Per-session `metrics.json` plus optional Prometheus textfile metrics via
  `BREEZY_METRICS_FILE`.
- `errors.json` capture for failed commands, and an `error-to-issue` workflow
  that turns nightly smoke-test failures into GitHub issues.
- Session archives with flat relative member names, idempotent re-archiving, and
  a manifest toggle via `BREEZY_FEATURE_ARCHIVE_MANIFEST`.
- Test suite covering the unit surface plus subprocess integration tests for the
  real CLI, with an 85% branch coverage gate.
- `Makefile` with `setup`, `lint`, `format`, `format-check`, `type`, `test`,
  `coverage`, `quality`, `docs`, `security`, `smoke`, `changelog`, `workflows`,
  and `check` targets.
- Ruff, MyPy (strict), pytest, coverage, vulture, deptry, ShellCheck, yamllint,
  Markdownlint, Prettier, jscpd, actionlint, and pre-commit configuration.
- CI workflow with lint, type, test matrix (3.11-3.13), quality, workflow
  syntax, docs drift, pre-commit, and aggregate status jobs.
- Semgrep security review with SARIF upload to code scanning, PR comments, and
  report artifacts.
- Release workflow that verifies the tag against `pyproject.toml`, builds the
  distribution, and publishes git-cliff release notes.
- Pull request hygiene review and size labelling workflow.
- Documentation: `AGENTS.md`, architecture, observability, session-recovery
  runbook, generated scenario index, and an environment template.
- Collaboration setup: CODEOWNERS, issue templates, PR template, label sync,
  Dependabot, and a devcontainer.
