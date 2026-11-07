---
name: roleplay-session
description: Step-by-step instructions for an agent to create a scenario, run a session, capture a transcript, summarize, archive, and verify it with the breezy-roleplay CLI.
---

# Role-Play Session Skill

Drives one full session lifecycle with the commands that actually exist in this
repository. Run everything from the repository root with `.venv` on `PATH`
(`source .venv/bin/activate` after `make setup`).

## 1. Define a Scenario (optional)

Create `scenarios/<kebab-case-name>.md`:

```markdown
# Scenario Title

**Title:** A short, human-readable title

**Participants:**

- First participant
- Second participant

**Setting:** Where the scene takes place

**Scenario Outline:**

1. First beat
2. Second beat
```

Then refresh the index, which CI checks for drift:

```bash
make docs
```

## 2. Create the Session

```bash
python -m breezy_roleplay create session-20260101-demo
```

Session IDs must match `[A-Za-z0-9._-]+`. The command writes
`sessions/<id>/` with `transcript.txt`, `summary.md`, `metadata.json`, and
`metrics.json`, and prints `Created session: <id>`.

## 3. Capture the Transcript

Append turns to `sessions/<id>/transcript.txt` as plain text. Nothing else reads
this file; its format is up to the scenario.

## 4. Summarize

Write `sessions/<id>/summary.md`. Optionally update
`sessions/<id>/metrics.json` with the real `duration_ms` and `steps` before
archiving; the archive carries whatever is on disk.

## 5. Archive

```bash
python -m breezy_roleplay archive session-20260101-demo
```

Produces `sessions/<id>.zip` with flat relative members
(`transcript.txt`, `summary.md`, `metadata.json`, `metrics.json`). The session
directory is left in place and an existing zip is replaced.

## 6. Verify

```bash
unzip -l sessions/<id>.zip     # expect four members, no directory prefix
unzip -t sessions/<id>.zip     # integrity check
```

For an end-to-end check of the tool itself, run `make demo` and confirm exactly
one `sessions/demo-*.zip` exists with those four members.

## 7. List Sessions

```bash
python -m breezy_roleplay list   # prints "No sessions found" or one name per line
```

## Reference

- `python -m breezy_roleplay --help` for all subcommands and `--version`.
- `make help` for every developer target.
- `docs/architecture.md` for the exact file schemas.
- `docs/observability.md` for log fields, metrics, and trace IDs.
- `.env.example` for the supported environment variables.

## Troubleshooting

- Exit code `1` means the operation was rejected; the message on stderr says
  why, and `sessions/<id>/errors.json` holds the traceback.
- Exit code `2` is a usage error from argparse.
- `Session directory not found` on archive means the session was never created
  or the ID is wrong.
- See `docs/runbooks/session-recovery.md` for recovery procedures.
