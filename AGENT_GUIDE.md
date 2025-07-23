# Agent Guide

This guide explains how an AI agent should interact with the **aegis‑roadmap** repository to execute Task‑Expertise directives effectively.

## Workflow overview

1. **Capture directive**: Load the directive text (e.g., `AegisAgentCards.txt`) into the agent’s working memory and assign a unique task ID.
2. **Validate & compliance check**: Parse the corresponding deck file from `roadmap_registry/` and ensure the tasks align with OpenAI policy and platform terms. Reference `roadmap_resources/openai_policy_summary.md` for guidance.
3. **Gather resources**: Use the `resource_links` in each card to open supporting documents located in `roadmap_resources/`.
4. **Execute cards**: Follow the sequence of cards as defined by each card’s `next` field. Each card includes its `key_question`, list of actions, and success criteria.
5. **Record feedback**: After completing a deck run, log performance metrics (`latency_ms`, `quality_score`, `confidence_float`, `improvement_note`) in `metrics/roadmap_usage.db`. Follow the instructions in `metrics/README.md`.
6. **Iterate and improve**: Use logged metrics and the feedback stage of cards to refine future iterations. When creating improved decks, increment the version and update the changelog.

## Key files and directories

- **roadmap_registry/**: Contains JSON decks to be executed.
- **roadmap_resources/**: Holds supporting markdown documents and specifications.
- **schemas/**: JSON Schema definitions for decks and cards.
- **metrics/**: Metrics database and logging instructions.
- **USAGE.md**: Quick start steps and a high‑level overview.
- **CONTRIBUTING.md**: Contribution guidelines for extending the repository.

## Safety and compliance

- Abide by the policies outlined in `openai_policy_summary.md`. Summarise reasoning without exposing raw chain‑of‑thought details.
- Always ask for user confirmation before performing actions with external side effects (e.g., creating or deleting repositories).
- Do not store personal data or proprietary information in public decks or resources.

This guide should help new agents understand and execute the Aegis roadmaps responsibly and effectively.
