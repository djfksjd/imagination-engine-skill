#!/usr/bin/env python3
"""Shared helpers for the imagination-engine scripts.

Python 3 standard library only. Every random choice in this package is derived
from a hash of the caller's inputs, so a given (topic, salt, run) always yields
the same draw. That is deliberate: an idea pipeline that cannot be replayed
cannot be audited, and "the model picked something else this time" is not a
defence when a result turns out to be a cliche.
"""

from __future__ import annotations

import hashlib
import json
import random
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

VERSION = "0.3.0"

SKILL_DIR = Path(__file__).resolve().parent.parent
DECK_DIR = SKILL_DIR / "references" / "decks"

DECK_NAMES = ("domains", "constraints", "senses", "perspectives", "affects", "modes", "cliches")


class EngineError(Exception):
    """Fatal, user-facing error. Callers exit non-zero with the message."""


def die(message: str, code: int = 1) -> "None":
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


def load_deck(name: str, deck_dir: Path | None = None) -> dict[str, Any]:
    if name not in DECK_NAMES:
        raise EngineError(f"unknown deck '{name}' (known: {', '.join(DECK_NAMES)})")
    path = (deck_dir or DECK_DIR) / f"{name}.json"
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise EngineError(f"cannot read deck {path}: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise EngineError(f"deck {path} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict) or data.get("deck") != name:
        raise EngineError(f"deck {path} is missing or has a mismatched 'deck' field")
    return data


def load_all_decks(deck_dir: Path | None = None) -> dict[str, dict[str, Any]]:
    return {name: load_deck(name, deck_dir) for name in DECK_NAMES}


def normalize(text: str) -> str:
    """Lowercase, NFKC-fold, collapse whitespace and dash variants.

    Used for both seeding and phrase matching so that "Neon-Lit", "neon lit"
    and "neon  lit" are one thing.
    """
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("‐", "-").replace("‑", "-").replace("–", "-").replace("—", "-")
    text = text.replace("‘", "'").replace("’", "'")
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()



PLACEHOLDER_NAMES = {
    "tbd", "todo", "tba", "n/a", "na", "none", "null", "untitled", "unnamed",
    "placeholder", "name", "?", "??", "???", "xxx", "test", "foo", "bar",
}


def text_units(text: str) -> int:
    """Length in units rather than code points.

    Every minimum in this skill is asking for an amount of *argument*, not an
    amount of Unicode. Counting code points makes a Korean, Japanese or Chinese
    section roughly twice as hard to satisfy as an English one carrying the same
    content, because one Han character or Hangul syllable does the work of about
    two Latin letters. So a wide letter or digit counts as two units.

    Only letters and digits are widened. Wide punctuation, box drawing and emoji
    stay at one, otherwise a row of decorative characters would clear a floor
    that plain prose has to earn. Compatibility-normalizing first stops fullwidth
    Latin from being used to inflate the count.
    """
    if not isinstance(text, str):
        return 0
    total = 0
    for ch in unicodedata.normalize("NFKC", text):
        category = unicodedata.category(ch)
        if category in ("Cc", "Cf", "Mn", "Me"):
            continue
        if category[0] in ("L", "N") and unicodedata.east_asian_width(ch) in ("W", "F"):
            total += 2
        else:
            total += 1
    return total


def is_placeholder(text: str) -> bool:
    """Whether a name is a stand-in rather than a name.

    A length floor cannot answer this: it rejects a complete two-character name
    and accepts 'TBD - fill this in later'. So the check asks what it actually
    wants to know - is there a name here at all.
    """
    stripped = normalize(text).strip(" .-_·")
    if not stripped:
        return True
    if not any(unicodedata.category(ch)[0] in ("L", "N") for ch in stripped):
        return True
    return stripped in PLACEHOLDER_NAMES


def seed_int(*parts: Any) -> int:
    joined = "\x1f".join(normalize(str(p)) for p in parts)
    digest = hashlib.blake2b(joined.encode("utf-8"), digest_size=16).digest()
    return int.from_bytes(digest, "big")


def rng_for(*parts: Any) -> random.Random:
    return random.Random(seed_int(*parts))


def stable_shuffle(items: list[Any], *seed_parts: Any) -> list[Any]:
    out = list(items)
    rng_for(*seed_parts).shuffle(out)
    return out


def round_robin(groups: list[list[Any]]) -> list[Any]:
    """Interleave groups so that any k consecutive items come from k distinct
    groups whenever k <= len(groups). This is what lets successive runs draw
    fresh, still-disjoint material instead of re-rolling the same favourites."""
    out: list[Any] = []
    if not groups:
        return out
    depth = max(len(g) for g in groups)
    for i in range(depth):
        for g in groups:
            if i < len(g):
                out.append(g[i])
    return out


def slice_by_run(ordered: list[Any], run: int, count: int) -> tuple[list[Any], bool]:
    """Take `count` items starting at (run-1)*count, wrapping if the deck runs
    out. Returns (items, wrapped)."""
    if count <= 0:
        raise EngineError("count must be positive")
    if not ordered:
        raise EngineError("empty deck")
    start = (run - 1) * count
    wrapped = start + count > len(ordered)
    picked = [ordered[(start + i) % len(ordered)] for i in range(count)]
    return picked, wrapped


def read_text_arg(value: str) -> str:
    """Read a file path, or stdin when the value is '-'."""
    if value == "-":
        return sys.stdin.read()
    try:
        return Path(value).read_text(encoding="utf-8")
    except OSError as exc:
        raise EngineError(f"cannot read {value}: {exc}") from exc


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def csv_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def phrase_regex(phrase: str) -> re.Pattern[str]:
    """Match a phrase tolerantly: spaces and hyphens interchange, an optional
    plural suffix is allowed on the final word, and matches must fall on word
    boundaries so that 'aura' does not fire inside 'restaurant'."""
    words = [w for w in re.split(r"[\s\-_]+", normalize(phrase)) if w]
    if not words:
        raise EngineError(f"empty phrase: {phrase!r}")
    escaped = [re.escape(w) for w in words]
    escaped[-1] = escaped[-1] + r"(?:e?s)?"
    body = r"[\s\-_]+".join(escaped)
    return re.compile(rf"(?<![\w]){body}(?![\w])", re.IGNORECASE)
