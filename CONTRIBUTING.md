# Contributing

Thank you for your interest in contributing to the **aegis‑roadmap** repository. This project serves as a living knowledge base and workflow engine for AI agents executing Task‑Expertise Roadmap directives.

## Adding new decks

- Place deck JSON files in the `roadmap_registry/` directory.
- Follow the naming convention `deck_<short_description>_v<version>.json`.
- Ensure decks conform to the card/deck schemas (`schemas/card_schema.json` and `schemas/deck_schema.json`).
- Include a corresponding directive or supporting document in `roadmap_resources/` when appropriate.
- Update `CHANGELOG.md` with a summary of the new deck and version.

## Adding resources

- Save documents that support cards in the `roadmap_resources/` directory.
- Use descriptive, lowercase file names with hyphens or underscores.
- Link to resources from cards using the `resource_links` field (e.g., `"res://openai_policy_summary"` refers to `roadmap_resources/openai_policy_summary.md`).

## Updating metrics

- Metrics files reside in the `metrics/` directory.
- When adding new metrics tables or fields, document them in `metrics/README.md`.
- Maintain the SQLite database schema version as needed.

## Versioning

- Increment the version in a deck’s `deck_meta.version` when making substantive changes.
- Use semantic versioning where appropriate (e.g., 0.2 for minor updates, 1.0 for major releases).
- Preserve previous versions rather than overwriting files to maintain historical context.

## Commit messages

- Use clear, descriptive commit messages (e.g., `Add new deck for user onboarding v0.2`).
- Group related changes into a single commit when possible.

## Code of Conduct

- This repository follows the guidelines set in `CODE_OF_CONDUCT.md`.
- Be respectful in all interactions; report unacceptable behaviour to the maintainers.

For questions or proposals, open an issue or contact the repository maintainer.
