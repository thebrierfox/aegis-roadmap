"""
log_metrics_example.py

This script demonstrates how to record metrics for an AEGIS Task‑Expertise roadmap deck.
It uses the SQLite database described in metrics/README.md to store a single metrics record.

Usage: python log_metrics_example.py
"""
import sqlite3
from datetime import datetime

DB_PATH = "metrics/roadmap_usage.db"
DECK_ID = "example_deck_id"

# Sample metrics values
default_metrics = {
    "latency_ms": 1500,
    "quality_score": 0.9,
    "confidence_float": 0.95,
    "improvement_note": "Consider parallelising resource downloads to reduce latency."
}

def ensure_table_exists(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS roadmap_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            deck_id TEXT NOT NULL,
            latency_ms INTEGER NOT NULL,
            quality_score REAL NOT NULL,
            confidence_float REAL NOT NULL,
            improvement_note TEXT
        );
        """
    )


def log_metrics(db_path: str, deck_id: str, metrics: dict):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    ensure_table_exists(cursor)
    cursor.execute(
        """
        INSERT INTO roadmap_usage (timestamp, deck_id, latency_ms, quality_score, confidence_float, improvement_note)
        VALUES (?, ?, ?, ?, ?, ?);
        """,
        (
            datetime.utcnow().isoformat(),
            deck_id,
            metrics["latency_ms"],
            metrics["quality_score"],
            metrics["confidence_float"],
            metrics.get("improvement_note", "")
        )
    )
    conn.commit()
    conn.close()
    print(f"Logged metrics for deck '{deck_id}' to {db_path}")


def main():
    log_metrics(DB_PATH, DECK_ID, default_metrics)


if __name__ == "__main__":
    main()
