# Usage Guide

This repository stores AI task‑expertise decks and resources used by the agent. Follow these instructions to run the initial directive and understand the layout.

## Quick start

1. **Read the directive**: Open `AegisAgentCards.txt` to understand the v0.1 Aegis Master Task‑Expertise Roadmap directive.
2. **Load the deck**: Parse `deck_system-ops_integrate_v0.1.json` and follow its cards sequentially. The deck defines a deterministic flow: capture the directive, validate against policies, reference required resources, embed the directive into your session, and log metrics.
3. **Reference resources**: Use the files in `roadmap_resources/` as supporting documentation:
   - `card_schema_spec.md` – definition of card fields【317636269435385†screenshot】.
   - `storage_conventions_doc.md` – storage rules for decks, resources, metrics, and changelogs【529199453895827†screenshot】.
   - `cot_mitigation_note.md` – guidelines for summarizing chain‑of‑thought reasoning without exposing raw internals.
   - `roadmap_registry_path.md` – explains how to reference deck files from the registry.
4. **Record metrics**: After executing a deck, log latency, quality score, confidence float and improvement notes into `metrics/roadmap_usage.db`. Consult `metrics/README.md` for schema details.

## Directory overview

- **roadmap_registry/** – stores deck JSON files. Each file uses the naming pattern `deck_<topic>_v<version>.json`.
- **roadmap_resources/** – contains human‑readable documentation supporting deck design and usage.
- **metrics/** – holds the metrics README and a placeholder database (`roadmap_usage.db`) for storing run‑time metrics.
- **CHANGELOG.md** – records notable changes and version history.

## Running the system‑ops integration deck

The current deck (`deck_system-ops_integrate_v0.1.json`) includes five cards:

1. **TASK_SYS_INIT – Directive Capture**: Ingest directive text into working memory and generate a deterministic task ID.
2. **DEC_SYS_VALIDATE – Conflict & Capability Check**: Validate the directive against system policies and flag any conflicts.
3. **RES_SYS_GUIDE – Reference Materials**: Ensure required documents from `roadmap_resources/` are accessible.
4. **ACT_SYS_INTEGRATE – Embed & Activate**: Register the deck in `roadmap_registry/` and enable the core loop hook.
5. **FDBK_SYS_REPORT – Integration Report**: Log metrics and improvement notes to support continuous improvement.

By following this sequence, the agent can bootstrap itself with the directive, maintain compliance, leverage supporting resources, and capture feedback for iterative refinement. New decks can be added under `roadmap_registry/` using the same schema and versioning pattern.
