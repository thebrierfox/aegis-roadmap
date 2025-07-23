# Storage Conventions

- **Decks**: Store deck JSON files in the `roadmap_registry/` directory. Use descriptive names: `deck_<domain>-<intent>_v<version>.json`. Increment the version when schemas change.
- **Resources**: Store supporting documents and specifications in the `roadmap_resources/` directory. Keep files in Markdown when possible for readability.
- **Metrics**: Store usage metrics (e.g., latencies, quality scores) in the `metrics/` directory. Use a SQLite database file (e.g., `roadmap_usage.db`) to record metrics; include a README to describe the schema.
- **Change Log**: Document major changes across versions in `CHANGELOG.md` at the repository root.

Following these conventions keeps the project organised and facilitates programmatic access to assets.
