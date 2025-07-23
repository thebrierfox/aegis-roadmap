## Metrics Overview

This README explains the metrics logging conventions for the AEGIS Task‑Expertise Roadmap repository. Metrics help evaluate the performance and usage of roadmap decks and inform future improvements.

### Directory

Metrics‑related files live in the `metrics/` directory at the root of this repository.

- **roadmap_usage.db**: A SQLite database storing usage metrics such as `latency_ms`, `quality_score`, `confidence_float`, and `improvement_note`. Each row corresponds to an invocation of a roadmap deck.
- **README.md** (this file): Describes metrics fields and logging practices.
- Additional scripts or dashboards can be added here in the future.

### Schema

The `roadmap_usage` table captures the following fields:

| Field | Type | Description |
|---|---|---|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT | Unique identifier for each record. |
| `timestamp` | TEXT | ISO‑8601 timestamp when the deck execution completed (UTC). |
| `deck_id` | TEXT | Identifier of the deck being run (e.g., `deck_system-ops_integrate_v0.1`). |
| `latency_ms` | INTEGER | Total latency (in milliseconds) for the deck execution. |
| `quality_score` | REAL | A subjective quality score (0–1) reflecting agent output quality. |
| `confidence_float` | REAL | An estimated confidence level (0–1) in the agent’s execution. |
| `improvement_note` | TEXT | Freeform notes on what could be improved. |

A sample SQL table creation statement:

```sql
CREATE TABLE IF NOT EXISTS roadmap_usage (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT NOT NULL,
  deck_id TEXT NOT NULL,
  latency_ms INTEGER NOT NULL,
  quality_score REAL NOT NULL,
  confidence_float REAL NOT NULL,
  improvement_note TEXT
);
```

### Logging Example

Below is a simple Python snippet demonstrating how an agent might record metrics at the end of a deck execution:

```python
import sqlite3
from datetime import datetime

def log_metrics(db_path: str, deck_id: str, latency_ms: int, quality_score: float, confidence_float: float, improvement_note: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roadmap_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            deck_id TEXT NOT NULL,
            latency_ms INTEGER NOT NULL,
            quality_score REAL NOT NULL,
            confidence_float REAL NOT NULL,
            improvement_note TEXT
        );
    """)
    cursor.execute("""
        INSERT INTO roadmap_usage (timestamp, deck_id, latency_ms, quality_score, confidence_float, improvement_note)
        VALUES (?, ?, ?, ?, ?, ?);
    """, (
        datetime.utcnow().isoformat(),
        deck_id,
        latency_ms,
        quality_score,
        confidence_float,
        improvement_note
    ))
    conn.commit()
    conn.close()

# Example usage
log_metrics(
    db_path="metrics/roadmap_usage.db",
    deck_id="deck_system-ops_integrate_v0.1",
    latency_ms=1200,
    quality_score=0.95,
    confidence_float=0.90,
    improvement_note="Consider caching resource downloads for speed."
)
```

### Usage Guidelines

- Agents should record metrics after executing roadmap actions, capturing latency and quality scores along with optional improvement notes.
- Maintain privacy by not storing personally identifiable information (PII) in metrics.
- To access metrics programmatically, use SQLite or another database interface to read `metrics/roadmap_usage.db`.
- When analyzing metrics, look for patterns that can help improve deck design, reduce execution time, and raise overall quality.
