# Breezy Roleplay Session Repository

## Overview
This repository serves as a playground for running and documenting role‑play scenarios.  It is a lightweight, reproducible environment that lets you:

1. **Define** scenarios as Markdown files in `scenarios/`.
2. **Record** sessions in `sessions/` – transcript and summary are stored per run.
3. **Automate** session lifecycle with helper shell scripts.
4. **Collaborate** using Git – fork, issue‑track, and merge changes.

> The repo starts as a minimal scaffold – you can add more tooling, CI, or formatting plugins as your workflow evolves.

## Getting Started

```bash
# Clone the repo
git clone https://github.com/your-org/breezy-roleplay.git
cd breezy-roleplay
```

### 1. Create a scenario
Place a Markdown file in `scenarios/`.  An example is provided in `scenarios/example.md`.

### 2. Start a new session
```bash
# Create a unique session ID (recommended: date‑plus‑label)
SESSION=demo-$(date +%Y%m%d%H%M%S)
./scripts/create_session.sh $SESSION
```
You’ll see **sessions/$SESSION** created with `transcript.txt` and `summary.md` placeholders.

### 3. Run the role‑play
> The actual engine is outside the scope of this skeleton.  Insert your runner’s output into `sessions/$SESSION/transcript.txt`.  Once the session completes, write a human‑readable summary to `sessions/$SESSION/summary.md`.

### 4. Archive the session
```bash
./scripts/archive_session.sh $SESSION
```
The script will produce `sessions/$SESSION.zip`, which you can store or share.

## Development & CI

* A GitHub Actions workflow `.github/workflows/ci.yml` lints all Markdown files.
* It also validates that at least one scenario file exists when a PR is opened.

## Future Enhancements
- Automate transcript capture and auto‑summary generation.
- Integrate Factory‑droid to trigger CI or custom workflows.
- Add a lightweight web UI for scenario editing and live playback.
- Expand the README with detailed schema for scenario files.

Happy role‑playing!
