## Metrics Overview

This README explains the metrics logging conventions for the AEGIS Task-Expertise Roadmap repository. Metrics help evaluate the performance and usage of roadmap decks.

### Directory

Metrics-related files live in the `metrics/` directory at the root of this repository.

### Schema and Logging

- **roadmap_usage.db**: a SQLite database (or similar) storing usage metrics such as `latency_ms`, `quality_score`, `confidence_float`, and `improvement_note`. Each row corresponds to an invocation of a roadmap deck.

- **README.md** (this file): describes metrics fields and logging practices.

- Additional metrics scripts or dashboards can be added here in the future.

### Usage Guidelines

- Agents should record metrics after executing roadmap actions, capturing latency and quality scores along with optional improvement notes.

- Maintain privacy by not storing personally identifiable information (PII) in metrics.

- To access metrics programmatically, use SQLite or another database interface to read `roadmap_usage.db`.
