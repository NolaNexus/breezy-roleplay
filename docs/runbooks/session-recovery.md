# Session Recovery Runbook

Concrete steps for recovering from session-related failures. Every command
below is runnable from the repository root and matches the layout created by
`src/breezy_roleplay/session.py`.

## 1. Missing or Corrupt Session Directory

### Symptoms

- `sessions/<session_id>/` is missing, or is present but missing
  `transcript.txt`, `summary.md`, `metadata.json`, or `metrics.json`.
- `python -m breezy_roleplay archive <session_id>` reports
  `Session directory not found`.

### Recovery Steps

1. Confirm the session ID from earlier commands or from the structured logs
   (the `session_id` field on `session.create` events).
2. Check whether an archive survived: `ls sessions/<session_id>.zip`
3. If the archive exists, extract it into a fresh directory and compare:

   ```bash
   mkdir -p sessions/recovered
   unzip -o sessions/<session_id>.zip -d sessions/recovered/
   ls sessions/recovered
   ```

4. If the archive does not exist, the session data is unrecoverable from this
   checkout. Check CI artifacts and backups before telling participants.
5. A recovered archive contains only `transcript.txt`, `summary.md`,
   `metadata.json`, and `metrics.json`. Re-create any other files by hand and
   re-run `archive`.

## 2. Failed Archive Creation

### Symptoms

- `python -m breezy_roleplay archive <session_id>` exits non-zero.
- `sessions/<session_id>.zip` is absent or older than the session directory.

### Recovery Steps

1. Read the error on stderr. The CLI prints the exception message and records
   the full traceback in `sessions/<session_id>/errors.json`.
2. Check free space and permissions:

   ```bash
   df -h .
   ls -ld sessions
   ```

3. Re-run the archive. The command replaces an existing zip atomically, so it is
   safe to retry:

   ```bash
   PYTHONPATH=src python3 -m breezy_roleplay archive <session_id>
   ```

4. If the archive still fails, verify the session directory is intact
   (`metadata.json` parses, `transcript.txt` is readable) before escalating.

## 3. Partially Written Metadata

### Symptoms

- `metadata.json` is empty or is not valid JSON.
- `archive` succeeds but downstream tooling cannot read the session.

### Recovery Steps

1. Back up the current file:

   ```bash
   cp sessions/<session_id>/metadata.json sessions/<session_id>/metadata.json.bak
   ```

2. Validate it:

   ```bash
   python3 -m json.tool sessions/<session_id>/metadata.json
   ```

3. If it is invalid, rewrite it with the schema the CLI actually writes. Only
   `id`, `created_at`, and `schema_version` are required:

   ```json
   {
     "id": "<session_id>",
     "created_at": "<ISO-8601 timestamp with timezone>",
     "schema_version": "1.0"
   }
   ```

4. Keep `created_at` in the same value as `metrics.json["created_at"]` when
   possible; tests and tooling assume they match.
5. Re-run `archive` and confirm the zip contains all four members.

## 4. CI Failure Triage

### Symptoms

- A workflow in the Actions tab fails for a pull request or push.

### Recovery Steps

1. Reproduce the failing job locally with the same commands CI runs:

   ```bash
   make check
   ```

2. Map the failing job to a target:

   | Job        | Local command                    |
   | ---------- | -------------------------------- |
   | lint       | `make lint`, `make format-check` |
   | type       | `make type`                      |
   | test       | `make coverage`                  |
   | quality    | `make quality`                   |
   | docs       | `make docs`                      |
   | pre-commit | `pre-commit run --all-files`     |

3. Fix the cause rather than the threshold. Lowering `fail_under` or deleting a
   check hides the regression.
4. Push a new commit to re-run the workflow. For infrastructure flakes, re-run
   the job from the Actions UI instead of pushing an empty commit.

## 5. Security Alert Triage

### Symptoms

- A code scanning alert from Semgrep appears under Security, or the
  `Security Review` workflow fails.

### Recovery Steps

1. Open Security, then Code scanning alerts, and read the rule and data flow.
2. Decide whether it is a true or false positive.
3. If it is a true positive, fix the code and run `make check` and
   `make security` before pushing.
4. If it is a false positive, dismiss the alert with a reason and, when the
   pattern is expected in this repository, add a narrowly scoped
   `# nosemgrep: <rule-id>` with a comment explaining why.
5. Re-run the workflow to confirm the alert clears.

## Useful Links

- [Actions](https://github.com/NolaNexus/breezy-roleplay/actions)
- [Code scanning alerts](https://github.com/NolaNexus/breezy-roleplay/security/code-scanning)
- [Structured logging reference](../observability.md)
