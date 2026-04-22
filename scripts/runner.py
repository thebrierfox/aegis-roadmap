#!/usr/bin/env python3
"""
scripts/runner.py — Aegis Task-Expertise Roadmap Generation CLI

Usage:
    python3 scripts/runner.py "describe my task here"
    python3 scripts/runner.py "describe my task here" --deck roadmap_registry/deck_foo.json
    python3 scripts/runner.py --list
"""

import argparse
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths — resolved relative to repo root regardless of cwd
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
DIRECTIVE_FILE = REPO_ROOT / "AegisAgentCards.txt"
REGISTRY_DIR = REPO_ROOT / "roadmap_registry"
METRICS_DB = REPO_ROOT / "metrics" / "roadmap_usage.db"
MODEL = "claude-haiku-4-5-20251001"


# ---------------------------------------------------------------------------
# Credential loader
# ---------------------------------------------------------------------------
def load_api_key() -> str:
    """
    Read ANTHROPIC_API_KEY from ~/intuitek/.env via bash source.
    Returns empty string if not found.
    """
    result = subprocess.run(
        ["bash", "-c", "source ~/intuitek/.env && echo $ANTHROPIC_API_KEY"],
        capture_output=True,
        text=True,
    )
    key = result.stdout.strip()
    if not key:
        key = os.environ.get("ANTHROPIC_API_KEY", "")
    return key


# ---------------------------------------------------------------------------
# Metrics DB
# ---------------------------------------------------------------------------
def ensure_runs_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS runs (
            id            INTEGER PRIMARY KEY,
            timestamp     TEXT NOT NULL,
            task_description TEXT NOT NULL,
            deck_file     TEXT NOT NULL,
            cards_count   INTEGER NOT NULL,
            latency_ms    INTEGER NOT NULL,
            model         TEXT NOT NULL
        )
        """
    )
    conn.commit()


def log_run(task_description: str, deck_file: str, cards_count: int, latency_ms: int) -> None:
    conn = sqlite3.connect(METRICS_DB)
    ensure_runs_table(conn)
    conn.execute(
        """
        INSERT INTO runs (timestamp, task_description, deck_file, cards_count, latency_ms, model)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now(timezone.utc).isoformat(),
            task_description,
            deck_file,
            cards_count,
            latency_ms,
            MODEL,
        ),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Deck file naming
# ---------------------------------------------------------------------------
def sanitize(text: str) -> str:
    """Convert a task description to a filesystem-safe slug."""
    slug = text.lower()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    slug = slug.strip("_")
    return slug[:60]


def deck_filename(task_description: str) -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    slug = sanitize(task_description)
    return REGISTRY_DIR / f"deck_{slug}_{ts}.json"


# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------
DECK_PROMPT_TEMPLATE = """\
Task description: {task}

Generate a Task-Expertise Roadmap Deck for this task following the directive above.
Return ONLY a valid JSON object — no markdown fences, no prose outside the JSON.

The JSON object must have exactly this structure:
{{
  "deck_meta": {{
    "title": "<descriptive title>",
    "deck_id": "deck_<discipline>_<intent>_v0.1",
    "version": "0.1",
    "parent": null,
    "changelog": []
  }},
  "cards": [ ... ]
}}

Each card must have ALL of these fields:
  card_id        STRING (unique, deterministic)
  type           one of: TASK | DECISION | RESOURCE | ACTION | FEEDBACK
  header         STRING (friendly title)
  trigger        STRING (boolean expression or ALWAYS)
  key_question   STRING
  core_actions   ARRAY of strings
  resource_links ARRAY of strings (may be empty)
  success_criteria ARRAY of strings
  next           card_id or END

Include at least 5 cards covering the universal funnel:
  TASK card -> DECISION card(s) -> RESOURCE card -> ACTION card(s) -> FEEDBACK card
"""


# ---------------------------------------------------------------------------
# JSON extraction helper
# ---------------------------------------------------------------------------
def _extract_json(raw: str) -> str:
    """Strip markdown fences and extract the first JSON object from raw text."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-z]*\n?", "", raw)
        raw = re.sub(r"\n?```\s*$", "", raw.rstrip())
        raw = raw.strip()
    # If there's leading prose before the JSON, find the first {
    brace = raw.find("{")
    if brace > 0:
        raw = raw[brace:]
    return raw


# ---------------------------------------------------------------------------
# Generation — claude CLI path (Max OAuth, no API credit cost)
# ---------------------------------------------------------------------------
def generate_via_claude_cli(task_description: str, system_prompt: str) -> tuple:
    """
    Use `claude -p` (Max OAuth) to generate the deck.
    Returns (raw_text, latency_ms).
    """
    combined_prompt = (
        system_prompt.strip()
        + "\n\n---\n\n"
        + DECK_PROMPT_TEMPLATE.format(task=task_description)
    )

    env = {**os.environ}
    env.pop("ANTHROPIC_API_KEY", None)   # force Max OAuth, not API key billing

    t0 = time.monotonic()
    result = subprocess.run(
        [
            "claude",
            "-p",
            combined_prompt,
            "--output-format",
            "text",
            "--model",
            MODEL,
        ],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(REPO_ROOT),
    )
    latency_ms = int((time.monotonic() - t0) * 1000)

    if result.returncode != 0:
        err = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"claude -p exited {result.returncode}: {err[:500]}")

    return result.stdout.strip(), latency_ms


# ---------------------------------------------------------------------------
# Generation — Anthropic SDK fallback (requires funded API key)
# ---------------------------------------------------------------------------
def generate_via_sdk(task_description: str, system_prompt: str) -> tuple:
    """
    Use the Anthropic Python SDK with API key from .env.
    Fallback only — the API key may have depleted credits.
    """
    import anthropic

    api_key = load_api_key()
    if not api_key:
        raise RuntimeError("No ANTHROPIC_API_KEY available for SDK fallback.")

    client = anthropic.Anthropic(api_key=api_key)
    user_prompt = DECK_PROMPT_TEMPLATE.format(task=task_description)

    t0 = time.monotonic()
    message = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    latency_ms = int((time.monotonic() - t0) * 1000)
    return message.content[0].text.strip(), latency_ms


# ---------------------------------------------------------------------------
# Unified deck generator
# ---------------------------------------------------------------------------
def generate_deck(task_description: str, system_prompt: str) -> tuple:
    """
    Attempt generation via claude CLI first (Max OAuth, zero credit cost).
    Falls back to SDK if CLI fails.
    Returns (deck_dict, latency_ms).
    """
    cli_available = subprocess.run(["which", "claude"], capture_output=True).returncode == 0
    errors = []

    if cli_available:
        try:
            raw, latency_ms = generate_via_claude_cli(task_description, system_prompt)
            deck = json.loads(_extract_json(raw))
            return deck, latency_ms
        except Exception as exc:
            errors.append(f"claude CLI: {exc}")
            print(f"  CLI path failed: {exc}", file=sys.stderr)
            print("  Trying SDK fallback...", file=sys.stderr)

    try:
        raw, latency_ms = generate_via_sdk(task_description, system_prompt)
        deck = json.loads(_extract_json(raw))
        return deck, latency_ms
    except Exception as exc:
        errors.append(f"SDK: {exc}")

    print("ERROR: All generation paths failed:", file=sys.stderr)
    for e in errors:
        print(f"  {e}", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Human-readable printer
# ---------------------------------------------------------------------------
def print_deck(deck: dict) -> None:
    meta = deck.get("deck_meta", {})
    print()
    print("=" * 70)
    print(f"  DECK: {meta.get('title', '(no title)')}")
    print(f"  ID:   {meta.get('deck_id', '?')}  |  version {meta.get('version', '?')}")
    print("=" * 70)

    cards = deck.get("cards", [])
    for i, card in enumerate(cards, 1):
        ctype = card.get("type", "?")
        print(f"\n[{i}/{len(cards)}] [{ctype}] {card.get('header', '?')}  (id: {card.get('card_id', '?')})")
        print(f"  Trigger      : {card.get('trigger', '')}")
        print(f"  Key question : {card.get('key_question', '')}")

        actions = card.get("core_actions", [])
        if actions:
            print("  Actions:")
            for a in actions:
                print(f"    - {a}")

        criteria = card.get("success_criteria", [])
        if criteria:
            print("  Success criteria:")
            for c in criteria:
                print(f"    + {c}")

        links = card.get("resource_links", [])
        if links:
            print(f"  Resources    : {', '.join(links)}")

        print(f"  Next         : {card.get('next', '?')}")

    print("\n" + "=" * 70)
    print(f"  {len(cards)} cards total")
    print("=" * 70)
    print()


# ---------------------------------------------------------------------------
# --list command
# ---------------------------------------------------------------------------
def list_decks() -> None:
    decks = sorted(REGISTRY_DIR.glob("deck_*.json"))
    if not decks:
        print("No decks found in roadmap_registry/")
        return
    print(f"\nDecks in roadmap_registry/:\n")
    for d in decks:
        try:
            with open(d) as f:
                meta = json.load(f).get("deck_meta", {})
            title = meta.get("title", "(no title)")
            version = meta.get("version", "?")
            print(f"  {d.name}  [v{version}]  {title}")
        except Exception:
            print(f"  {d.name}  (unreadable)")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aegis Task-Expertise Roadmap CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            '  python3 scripts/runner.py "Build a content distribution pipeline for dev.to"\n'
            '  python3 scripts/runner.py "Automate ClawMart listing updates" '
            "--deck roadmap_registry/deck_existing.json\n"
            "  python3 scripts/runner.py --list"
        ),
    )
    parser.add_argument("task", nargs="?", help="Task description to generate a roadmap for")
    parser.add_argument(
        "--deck",
        metavar="DECK_FILE",
        help="Path to an existing deck file to display instead of generating",
    )
    parser.add_argument("--list", action="store_true", help="List all decks in roadmap_registry/")
    args = parser.parse_args()

    if args.list:
        list_decks()
        return

    if not args.task:
        parser.print_help()
        sys.exit(1)

    # --deck mode: load and display an existing deck
    if args.deck:
        deck_path = Path(args.deck)
        if not deck_path.is_absolute():
            deck_path = REPO_ROOT / deck_path
        if not deck_path.exists():
            print(f"ERROR: Deck file not found: {deck_path}", file=sys.stderr)
            sys.exit(1)
        with open(deck_path) as f:
            deck = json.load(f)
        print(f"\nLoaded existing deck: {deck_path.name}")
        print_deck(deck)
        return

    # Generation mode
    print(f"\nTask: {args.task}")
    print(f"Model: {MODEL}")
    print("Reading directive from AegisAgentCards.txt ...")

    if not DIRECTIVE_FILE.exists():
        print(f"ERROR: Directive file not found: {DIRECTIVE_FILE}", file=sys.stderr)
        sys.exit(1)

    system_prompt = DIRECTIVE_FILE.read_text(encoding="utf-8")

    print("Calling Claude (claude -p / Max OAuth) ... ", end="", flush=True)
    deck, latency_ms = generate_deck(args.task, system_prompt)
    print(f"done ({latency_ms} ms)\n")

    # Validate minimal structure
    if "deck_meta" not in deck or "cards" not in deck:
        print("ERROR: Generated deck is missing required top-level keys.", file=sys.stderr)
        print(json.dumps(deck, indent=2)[:800], file=sys.stderr)
        sys.exit(1)

    # Save deck
    out_path = deck_filename(args.task)
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(deck, f, indent=2, ensure_ascii=False)
    print(f"Deck saved  : {out_path.relative_to(REPO_ROOT)}")

    # Log metrics
    cards_count = len(deck.get("cards", []))
    METRICS_DB.parent.mkdir(parents=True, exist_ok=True)
    log_run(args.task, str(out_path.relative_to(REPO_ROOT)), cards_count, latency_ms)
    print(f"Metrics     : metrics/roadmap_usage.db  ({cards_count} cards, {latency_ms} ms)")

    # Print deck
    print_deck(deck)


if __name__ == "__main__":
    main()
