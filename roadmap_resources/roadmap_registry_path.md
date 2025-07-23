## Roadmap Registry Path

This note describes where to store and reference deck files within the AEGIS roadmap repository. Decks contain serialized JSON objects representing task-expertise roadmaps (cards), and they are stored in a central registry directory for discoverability.

### Location

Deck files are stored under the `roadmap_registry/` directory at the root of this repository. Each deck file uses a consistent naming convention: `deck_<topic>_v<version>.json`. For example, the directive deck for system‑ops integration is stored at:

```
roadmap_registry/deck_system-ops_integrate_v0.1.json
```

### Usage

When referencing a deck in other files or workflows:

- Use relative paths prefaced with `roadmap_registry/` to access the JSON.
- Ensure that updates to decks are versioned by incrementing the file version number and updating the corresponding `deck_meta` object.
- Keep the registry directory organized by topic; avoid mixing unrelated decks.

The registry path structure supports programmatic discovery and loading of decks by automation scripts and ensures compatibility with the AEGIS Master Task-Expertise Roadmap Directive.
