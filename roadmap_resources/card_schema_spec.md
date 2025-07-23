# Card Schema Specification

Each card in a Task–Expertise Roadmap deck follows a consistent schema:

- `card_id` (string): Unique identifier for the card.
- `type` (enum): One of `TASK`, `DECISION`, `RESOURCE`, `ACTION`, `FEEDBACK`.
- `header` (string): Short label summarising the card.
- `trigger` (enum): Conditions that activate the card (e.g., `ALWAYS`).
- `key_question` (string): The central question or decision point.
- `core_actions` (array of strings): Steps or actions to take.
- `resource_links` (array of strings): Pointers to supporting documentation or resources.
- `success_criteria` (array of strings): Conditions for considering the card successfully executed.
- `next` (string): ID of the next card in the sequence (or `END`).

This schema ensures decks remain machine-readable and extensible.
