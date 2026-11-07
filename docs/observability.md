# Observability

Where every signal this repository produces lives, and how to read it.

## Structured Logs (stderr)

The CLI writes one JSON object per line to **stderr**. stdout stays reserved for
command output, so `python -m breezy_roleplay list | wc -l` works.

```json
{
  "event": "session.create",
  "level": "info",
  "logger": "breezy_roleplay.session",
  "message": "Session created",
  "session_dir": "/repo/sessions/demo",
  "session_id": "demo",
  "timestamp": "2026-01-01T12:00:00+00:00",
  "trace_id": "9fcf6ca2a2e24284a2dbd1b00f99babc"
}
```

| Field       | Meaning                                                      |
| ----------- | ------------------------------------------------------------ |
| `timestamp` | ISO-8601 with timezone, UTC                                  |
| `level`     | `debug`, `info`, `warning`, or `error`                       |
| `logger`    | Module name, for example `breezy_roleplay.session`           |
| `event`     | Stable dotted event name (`session.create`, `metrics.write`) |
| `message`   | Human-readable text, already redacted                        |
| `trace_id`  | `BREEZY_TRACE_ID` or a generated UUID4 hex                   |
| other keys  | Event-specific context (`session_id`, `zip_path`, ...)       |

Sensitive keys (`email`, `token`, `api_key`, `authorization`, `password`,
`secret`) are redacted in keyword arguments, and every message passes through
`redact()`.

Set `BREEZY_FEATURE_STRUCTURED_LOGS=false` to fall back to
`<logger>: <message>` plain text, which is easier to read interactively but
loses the structured fields.

### Reading logs

```bash
python -m breezy_roleplay demo 2>&1 >/dev/null | jq -c 'select(.level=="warning")'
python -m breezy_roleplay list 2>&1 >/dev/null | jq -r '.event' | sort | uniq -c
```

## Trace IDs

`BREEZY_TRACE_ID` is a **value**, not a path. Set it to correlate one CLI
invocation across log lines:

```bash
export BREEZY_TRACE_ID="$(uuidgen | tr -d -)"
python -m breezy_roleplay create demo
```

Unset, each log entry gets a fresh UUID4 hex value, which is enough to group the
lines of a single operation.

## Per-Session Metrics

Every session gets `sessions/<id>/metrics.json`:

```json
{ "created_at": "2026-01-01T12:00:00+00:00", "duration_ms": 1234, "steps": 2 }
```

`duration_ms` and `steps` are `0` until the scenario runner updates them.

## Prometheus Textfile

Set `BREEZY_METRICS_FILE` to a path and the CLI appends samples in the
node-exporter textfile format:

```text
breezy_session_created_total 1
breezy_session_archive_seconds 0
```

The parent directory is created on demand. Point a node-exporter
`--collector.textfile.directory` at that directory to scrape them, or tail the
file in a dashboard. This is a textfile, **not** JSON Lines.

## Error Records

When a command fails and `sessions/<id>/` exists, `errors.json` captures the
failure for later triage:

```json
{
  "timestamp": "2026-01-01T12:00:00+00:00",
  "error": { "type": "FileExistsError", "message": "Session directory already exists: ..." },
  "traceback": "Traceback (most recent call last): ...",
  "context": { "command": "create" }
}
```

`error-to-issue.yml` turns nightly smoke-test failures into GitHub issues using
this same shape.

## CI Signals

| Signal             | Where                                                           |
| ------------------ | --------------------------------------------------------------- |
| Job results        | Actions tab, one run per push or pull request                   |
| Coverage           | `coverage-report` artifact (`coverage.xml`) and the job summary |
| Test results       | `junit-report` artifact (`junit.xml`)                           |
| Lint and type      | Job logs; failures annotate the pull request                    |
| Duplication        | `reports/jscpd/jscpd-report.json` artifact                      |
| Security findings  | Security, then Code scanning alerts (SARIF, `semgrep` category) |
| Security report    | `semgrep-security-report` artifact and the PR comment           |
| Workflow validity  | The `actionlint` job                                            |
| Dependency updates | Dependabot pull requests                                        |

## Merge Gate

`main` is protected by the ruleset in `.github/rulesets/main.json`, applied with
`python scripts/apply_ruleset.py`. Two checks gate every merge:

- `CI status` is the aggregate job at the end of `ci.yml`. It fails when any of
  lint, type, test, quality, workflows, docs, or pre-commit fails, and it prints
  a per-job table to the run summary. Gating on the aggregate keeps the
  protection stable when the test matrix changes.
- `Security Review` is the Semgrep job. A new finding blocks the merge and
  appears in the code scanning alerts list at the same time.

Direct pushes and force-pushes to `main` are rejected, so the CI result on a
commit is always the result that was merged.

## Health Checks

`error-to-issue.yml` runs `python -m breezy_roleplay demo` in a scratch
directory every night. That exercises create, metrics, logging, archive, and zip
layout in one shot. A failure opens (or updates) an issue labelled `type:bug`
and `priority:P1` with the captured stderr and `errors.json`.

Run the same check locally:

```bash
make demo && unzip -l sessions/demo-*.zip
```

## Correlating With External Systems

- Ship `BREEZY_METRICS_FILE` with node-exporter's textfile collector, then graph
  `breezy_session_created_total` in Prometheus/Grafana.
- Forward stderr to any JSON-aware collector (Loki, Elasticsearch, CloudWatch)
  and key dashboards on `event` and `trace_id`.
- Consume code scanning alerts through the GitHub Code Scanning API or the SARIF
  artifact to feed an external security dashboard.
