# Project Plan – Breezy Roleplay Sessions

## Goal
Establish a lightweight, reproducible repository structure that makes creating, executing, recording, and sharing role‑play scenarios straightforward.

## High‑level Architecture

```
├── README.md                     # Overview
├── plan.md                       # This plan file
├── .gitignore                    # Common ignore patterns
├── scenarios/                    # Source files for each scenario
│   └── example.md                # Sample scenario
├── sessions/                     # Result artifacts for executed sessions
│   ├── session-YYYYMMDD/         # Timeline‑based output folder
│   │   ├── transcript.txt        # Raw role‑play transcript
│   │   └── summary.md            # Human‑readable summary
├── scripts/                      # Utility scripts (bash/python)
│   ├── create_session.sh         # Initialize a new session directory
│   └── archive_session.sh        # Zip or upload session
└── .factory/                     # Optional Factory configuration (if used)
```

## Deliverables
1. **Directory layout** – Already created.
2. **Scenario files** – Create a living example in `scenarios/example.md`.
3. **Automation scripts** – Basic Bash helpers for:
   * Starting a session (`create_session.sh`).
   * Recording a transcript.
   * Archiving or publishing the session.
4. **Documentation** – Update `README.md` to describe local workflow.
5. **Optional CI** – GitHub Actions to lint Markdown & ensure the repo has at least one scenario.

## Next Actions
- Draft the sample scenario file.
- Write the `create_session.sh` script template.
- Write the `archive_session.sh` script template.
- Add basic Markdown linting workflow.
- Commit all changes.

---

Timestamp: `2026‑11‑07` | Author: @droid

---
