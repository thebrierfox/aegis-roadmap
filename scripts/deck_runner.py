#!/usr/bin/env python3
"""Aegis Roadmap — card deck runner.

Reads a deck JSON from roadmap_registry/, executes each card in sequence using
Aegis (Claude Code) as the runtime, and chains card outputs to the next card.

Cards are typed: TASK, DECISION, RESOURCE, ACTION, FEEDBACK.
Each card has a trigger, key_question, core_actions, success_criteria, and a
next pointer (card_id or 'END').

Usage:
  python3 scripts/deck_runner.py                              # run default deck
  python3 scripts/deck_runner.py roadmap_registry/deck.json  # run specific deck
  python3 scripts/deck_runner.py --list                       # list available decks

Environment:
  INTUITEK_DIR    path to ~/intuitek/ for run_task.sh (default: ~/intuitek)
  CLAUDE_BIN      path to claude binary (default: claude)
"""

from __future__ import annotations
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
REGISTRY_DIR = REPO_ROOT / "roadmap_registry"
METRICS_DIR = REPO_ROOT / "metrics"
SCHEMA_DIR = REPO_ROOT / "schemas"
CARD_SCHEMA = SCHEMA_DIR / "card_schema.json"

INTUITEK = Path(os.environ.get("INTUITEK_DIR", Path.home() / "intuitek"))
RUN_TASK = INTUITEK / "run_task.sh"
CLAUDE_BIN = os.environ.get("CLAUDE_BIN", "claude")

METRICS_DB = METRICS_DIR / "roadmap_usage.db"


def ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg: str) -> None:
    print(f"[{ts()}] {msg}", flush=True)


def record_metric(deck_id: str, card_id: str, outcome: str, duration_ms: int) -> None:
    try:
        import sqlite3
        METRICS_DIR.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(str(METRICS_DB))
        con.execute("""
            CREATE TABLE IF NOT EXISTS card_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT, deck_id TEXT, card_id TEXT, outcome TEXT, duration_ms INTEGER
            )
        """)
        con.execute(
            "INSERT INTO card_runs (ts, deck_id, card_id, outcome, duration_ms) VALUES (?,?,?,?,?)",
            (ts(), deck_id, card_id, outcome, duration_ms)
        )
        con.commit()
        con.close()
    except Exception as e:
        log(f"metric write failed (non-fatal): {e}")


def build_card_prompt(card: dict, ctx: dict) -> str:
    parts = [
        f"Aegis Roadmap — executing card: {card['card_id']}",
        f"Type: {card['type']}",
        f"Header: {card['header']}",
        f"Trigger: {card['trigger']}",
        f"Key question: {card['key_question']}",
        "",
        "Core actions to complete:",
    ]
    for action in card.get("core_actions", []):
        parts.append(f"  • {action}")

    if card.get("resource_links"):
        parts.append("\nResources:")
        for link in card["resource_links"]:
            parts.append(f"  {link}")

    parts.append("\nSuccess criteria:")
    for criterion in card.get("success_criteria", []):
        parts.append(f"  ✓ {criterion}")

    if ctx:
        parts.append(f"\nContext from prior cards: {json.dumps(ctx)}")

    parts.append(
        "\nExecute this card now. Complete each core action autonomously "
        "within your approval boundary. Report results clearly. If a decision "
        "card, state your decision and the reasoning."
    )
    return "\n".join(parts)


def execute_card(card: dict, deck_id: str, ctx: dict) -> tuple[str, dict]:
    card_id = card["card_id"]
    card_type = card.get("type", "TASK")
    log(f"card {card_id} ({card_type}): {card['header']}")

    prompt = build_card_prompt(card, ctx)
    start = datetime.now(timezone.utc)

    output = ""
    exit_code = 1

    if RUN_TASK.exists():
        result = subprocess.run(
            ["bash", str(RUN_TASK), prompt],
            capture_output=True, text=True, timeout=600
        )
        output = result.stdout
        exit_code = result.returncode
    elif subprocess.run(["which", CLAUDE_BIN], capture_output=True).returncode == 0:
        result = subprocess.run(
            [CLAUDE_BIN, "-p", prompt, "--output-format", "text"],
            capture_output=True, text=True, timeout=600
        )
        output = result.stdout
        exit_code = result.returncode
    else:
        log(f"no runtime available for card {card_id} — recording as DEFERRED")
        duration = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
        record_metric(deck_id, card_id, "DEFERRED", duration)
        return "DEFERRED", ctx

    duration = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
    outcome = "PASS" if exit_code == 0 else "FAIL"
    record_metric(deck_id, card_id, outcome, duration)

    if output.strip():
        log(f"card {card_id} output ({len(output)} chars):\n{output.strip()[:800]}")

    # Carry forward output as context for the next card
    ctx[card_id] = {"outcome": outcome, "summary": output.strip()[:500]}
    return outcome, ctx


def run_deck(deck_path: Path) -> int:
    log(f"loading deck: {deck_path.name}")
    deck = json.loads(deck_path.read_text())
    meta = deck.get("deck_meta", {})
    deck_id = meta.get("deck_id", deck_path.stem)
    title = meta.get("title", deck_id)
    cards = {c["card_id"]: c for c in deck.get("cards", [])}

    if not cards:
        log("deck has no cards — nothing to run")
        return 0

    log(f"deck: {title} ({len(cards)} cards)")
    ctx: dict = {}
    current_id = next(iter(cards))  # start with first card
    visited = set()
    failures = 0

    while current_id and current_id != "END":
        if current_id not in cards:
            log(f"card not found: {current_id} — stopping")
            break
        if current_id in visited:
            log(f"cycle detected at {current_id} — stopping")
            break
        visited.add(current_id)
        card = cards[current_id]
        outcome, ctx = execute_card(card, deck_id, ctx)
        if outcome == "FAIL":
            failures += 1
        current_id = card.get("next", "END")

    log(f"deck complete: {title} | {len(visited)} cards | {failures} failures")
    return failures


def list_decks() -> None:
    decks = sorted(REGISTRY_DIR.glob("*.json"))
    if not decks:
        print("no decks in roadmap_registry/")
        return
    for p in decks:
        try:
            d = json.loads(p.read_text())
            meta = d.get("deck_meta", {})
            print(f"  {p.name}: {meta.get('title', '?')} ({len(d.get('cards',[]))} cards)")
        except Exception:
            print(f"  {p.name}: (unreadable)")


def main() -> int:
    if "--list" in sys.argv:
        list_decks()
        return 0

    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        path = Path(sys.argv[1])
        if not path.exists():
            path = REGISTRY_DIR / sys.argv[1]
    else:
        decks = sorted(REGISTRY_DIR.glob("*.json"))
        decks = [d for d in decks if "template" not in d.name]
        if not decks:
            log("no decks found in roadmap_registry/ — run with a deck path")
            return 1
        path = decks[0]

    failures = run_deck(path)
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
