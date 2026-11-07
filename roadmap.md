# Project Road‑Map & Architecture

> This document outlines the high‑level architecture, foundational layers, and a phased roadmap to turn **Breezy Role‑Play Sessions** into a smooth, user‑friendly experience.

## 1. Core Foundations (Phase 0 – Immediately)
| # | Deliverable | Why it matters |
|---|-------------|----------------|
| 0.1 | **Standardized Scenario Schema** | Define a clear Markdown‑based structure (metadata block + narrative steps) so tools can parse it consistently. |
| 0.2 | **Session Lifecycle Scripts** | `create_session.sh` / `archive_session.sh` + a helper to reset a session. |
| 0.3 | **Folder Layout** | `scenarios/`, `sessions/`, `scripts/`, `.factory/`. Keeps artifacts isolated. |
| 0.4 | **CI Pipeline** | Lint Markdown and validate scenario presence. Protects against accidental breakage. |
| 0.5 | **Repository README** | Detailed usage instructions, getting‑started guide, and a FAQ. |

## 2. Rich Interaction Layer (Phase 1 – 1 month)
| # | Deliverable | Technical Stack | Notes |
|---|-------------|-----------------|-------|
| 1.1 | **Role‑Play Engine API** | Lightweight Python server (FastAPI) or Node.js (Express) exposing `/run` endpoint. | Or integrate an existing chatbot (OpenAI, Anthropic) via wrapper. |
| 1.2 | **Automated Transcript Capture** | Script injects chat API responses to `transcript.txt` in real‑time. | Could use a simple wrapper script or event‑driven hook. |
| 1.3 | **Automated Summary Generator** | Small Python helper that runs a summarization model (OpenAI `gpt-4o-mini`). | Feed whole transcript -> write `summary.md`. |
| 1.4 | **Engine‑Triggered CI** | Factory‑droid workflow that runs tests after `archive_session.sh`. | Fail fast if output deviates from schema. |
| 1.5 | **Preview CLI** | `./scripts/preview_session.sh <id>` that opens `summary.md` in your browser. | Quick sanity check. |

## 3. Collaboration & Discovery (Phase 2 – 2 months)
| # | Deliverable | Stack | Notes |
|---|-------------|-------|-------|
| 2.1 | **Web UI** | React (Vite) + Tailwind + `@factory/lab` for deployment on Factory IID. | UI lets users edit scenario, start session, view transcripts, export. |
| 2.2 | **Scenario Registry** | JSON manifest in `scenarios/manifest.json` that indexes all scenarios (title, tags, author). | Enables search and filtering in UI. |
| 2.3 | **Collaborative Editing** | Real‑time CRDT via Yjs + Socket.io backend (or use `liveblocks`). | Multiple users can edit `example.md` simultaneously. |
| 2.4 | **Versioned Sessions** | Git LFS for large transcript files, automatically commit to a `sessions/` branch. | Keeps history of role‑play sessions. |
| 2.5 | **Discussion & Review** | GitHub PR templates + Factory‑droid review automation (code‑review skill). | Pull requests for new scenarios get an AI‑written review. |

## 4. Analytics & Insight (Phase 3 – 3 months)
| # | Deliverable | Tech | Notes |
|---|-------------|--------|-------|
| 3.1 | **Metric Engine** | Python script that parses `transcript.txt` for turn‑count, response time, sentiment. | Write to `metrics.json`. |
| 3.2 | **Dashboard** | Grafana + Prometheus (scrape metrics endpoint). | Visualise average session time, sentiment heatmaps. |
| 3.3 | **Export Toolkit** | CLI that packages a session into a `.zip` + `.html` summary and metrics. | Easy to share with stakeholders. |
| 3.4 | **Notification System** | Factory‑bot to post session summaries or analytics to Slack. | Keeps the team informed. |

## 5. Scalability & Enterprise Readiness (Phase 4 – 4 months and beyond)
| # | Deliverable | Stack | Notes |
|---|-------------|--------|-------|
| 4.1 | **Distributed Engine** | Kubernetes + Helm chart; the role‑play API runs as a scalable service. | Handles many concurrent sessions. |
| 4.2 | **Auth & Access Control** | Factory‑Auth integration (Roles, Teams). | Restrict who can run, edit, or view scenarios. |
| 4.3 | **Compliance & Logging** | ISO‑27001‑ready logging, data retention policies. | Especially relevant for regulated industries. |
| 4.4 | **Marketplace Integration** | Publish scenario bundles as artifacts in Factory‑Marketplace. | Reuse & monetise high‑quality role‑plays. |

## 6. Maintenance & Sustainability
- **Automated Tests** – unit tests for scripts, integration tests for the engine.
- **Continuous Delivery** – Docker images for the engine, automated release on tag.
- **Documentation** – Sphinx/Markdown docs + GitHub Wiki.
- **Community** – Contributing guidelines, issue templates.

---

### Suggested Timeline
| Phase | Duration | Key Milestones |
|-------|----------|-----------------|
| 0 | 1 week | Repo scaffold + CI |
| 1 | 4 weeks | Engine + automation scripts |
| 2 | 8 weeks | Web UI + collaborative editing |
| 3 | 12 weeks | Analytics stack |
| 4 | 16 weeks | Enterprise extensions |

Feel free to adjust the schedule based on team capacity.  Each phase builds on the previous one, ensuring incremental value and quick feedback loops.

Happy building!
