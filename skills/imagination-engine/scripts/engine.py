#!/usr/bin/env python3
"""Shared helpers for the imagination-engine scripts.

Python 3 standard library only. Every random choice in this package is derived
from a hash of the caller's inputs, so a given (topic, salt, run) always yields
the same draw. That is deliberate: an idea pipeline that cannot be replayed
cannot be audited, and "the model picked something else this time" is not a
defence when a result turns out to be a cliche.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

VERSION = "0.4.0"

SKILL_DIR = Path(__file__).resolve().parent.parent
DECK_DIR = SKILL_DIR / "references" / "decks"

DECK_NAMES = ("domains", "constraints", "senses", "perspectives", "affects", "modes", "cliches")


class EngineError(Exception):
    """Fatal, user-facing error. Callers exit non-zero with the message."""



class UsageParser(argparse.ArgumentParser):
    """argparse exits 2 on a usage error, which collides with "gate failed".

    A typo in a flag name must never be reportable as a policy verdict, in
    either direction. Usage errors exit 1.
    """

    def error(self, message: str) -> None:  # type: ignore[override]
        die(f"usage: {message}", 1)


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

# Words that are stand-ins when the author is naming their own result and real
# titles when the author is citing someone else's. A great many catalogued works
# are called exactly "Untitled", so rejecting it in a citation field rejects
# honest work - and a gate that rejects honest work is the reason a user turns it
# off. See is_placeholder(titles_ok=...).
REAL_TITLE_WORDS = {"untitled", "unnamed"}


MARKS_PER_BASE = 2


def text_units(text: str) -> int:
    """Length in *content* units rather than code points.

    Every minimum in this skill is asking for an amount of argument, so only the
    characters that carry argument are counted: letters and digits. Spaces,
    punctuation and symbols count nothing at all. Counting them was the hole that
    voided the whole anti-padding rule - `text_units` counted a space while
    `distinct_ratio` tokenised it away, so `"Sound" + 200 spaces + "stays"` was
    210 units at a perfect distinctness score and cleared every floor in the
    gate. Fixing that per field would have left the next punctuation trick open;
    it is fixed here, once, at the measurement every floor shares.

    Counting code points also made a Korean, Japanese or Chinese section roughly
    twice as hard to satisfy as an English one carrying the same content, because
    one Han character or Hangul syllable does the work of about two Latin
    letters. So a wide letter or digit counts as two units. Wide punctuation, box
    drawing and emoji are not letters and count zero, so a row of decorative
    characters cannot clear a floor that plain prose has to earn.
    Compatibility-normalizing first stops fullwidth Latin from inflating the
    count.

    **Combining marks count, capped per base.** Discarding every `Mn`/`Mc`/`Me`
    mark - which is what "letters and digits only" did - destroyed the scripts
    that write their vowels as marks: a Devanagari sentence of 56 code points
    measured 27, Hebrew with niqqud 16 measured 9, Thai 29 measured 20. Those
    authors were held to a floor roughly twice as high as an English author
    writing the same argument, which is the same unfairness the wide-letter rule
    exists to remove, in the other direction. So a mark that attaches to a letter
    or digit counts one unit, up to two marks per base.

    The cap is per *base character* and **does not reset on punctuation or
    whitespace**. That ordering is the load-bearing detail: the sibling
    `imagination-brainstorming` repo reset its counter on any non-mark, which
    let `"Nurse" + 120x(dot + two accents) + "waits"` measure 251 units and
    clear a 250 floor from 370 code points of dots and accents. Here the run of
    dots creates no new base, so the same string measures 7 - stacking marks
    cannot buy units, and neither can stacking punctuation, because punctuation
    never counted in the first place.

    Neither half is sufficient alone, and neither this repo nor its sibling had
    both. This is the union, and both repos are being moved to it so they stop
    diverging. What it does not do is judge the marks: a mark on a base still
    counts even if it is meaningless there. The defence against repetition is
    `distinct_ratio`, which is unchanged and still applies to every field with a
    floor.
    """
    if not isinstance(text, str):
        return 0
    total = 0
    base_is_content = False
    marks_on_base = 0
    for ch in unicodedata.normalize("NFKC", text):
        category = unicodedata.category(ch)
        if category[0] in ("L", "N"):
            total += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
            base_is_content = True
            marks_on_base = 0
        elif category in ("Mn", "Mc", "Me"):
            if base_is_content and marks_on_base < MARKS_PER_BASE:
                total += 1
                marks_on_base += 1
        # Anything else - space, punctuation, symbol, emoji - contributes
        # nothing and, deliberately, does not open a new base for marks.
    return total


def distinct_ratio(text: str) -> float:
    """Share of distinct tokens in a text.

    Every minimum in this skill asks for an amount of argument, and a length
    floor cannot tell argument from filler: forty repeated letters is forty
    units. Padding scores near zero here, ordinary prose scores well above the
    floor the gate applies.
    """
    tokens = re.findall(r"[\w']+", normalize(text), flags=re.UNICODE)
    if not tokens:
        return 0.0
    if len(tokens) == 1:
        # One long token: measure repetition at character level, because
        # "abcabcabc..." has three distinct characters and is still padding.
        word = tokens[0]
        if len(word) < 4:
            return 1.0
        bigrams = [word[i:i + 2] for i in range(len(word) - 1)]
        return len(set(bigrams)) / len(bigrams)
    ratio = len(set(tokens)) / len(tokens)
    # A repeated multi-word phrase scores well on token variety; compare the
    # first half of the text with the second to catch it.
    if len(tokens) >= 8:
        half = len(tokens) // 2
        if normalize(" ".join(tokens[:half])) == normalize(" ".join(tokens[half:half * 2])):
            return 0.0
    return ratio


def is_placeholder(text: str, titles_ok: bool = False) -> bool:
    """Whether a field holds a stand-in rather than content.

    A length floor cannot answer this: it rejects a complete two-character name
    and accepts 'TBD - fill this in later'. So the check asks what it actually
    wants to know - is there anything here at all. Applied to every field where
    a stand-in would defeat the field's purpose, not only to the name: a
    `resembles[].work` of "-" used to satisfy the one requirement that carries
    this skill's honesty guarantee.

    `titles_ok` is for citation fields, where the author is naming a work that
    already exists rather than filling in their own. "Untitled" there is the
    actual title of a very large number of real works, and refusing it made the
    gate reject honest citations. "TBD" and "-" are refused in either mode.
    """
    stripped = normalize(text).strip(" .-_·")
    if not stripped:
        return True
    if not any(unicodedata.category(ch)[0] in ("L", "N") for ch in stripped):
        return True
    names = PLACEHOLDER_NAMES - REAL_TITLE_WORDS if titles_ok else PLACEHOLDER_NAMES
    return stripped in names


SEED_SEP = "\x1f"


def pack_fields(*fields: str) -> str:
    """Join fields so that no field can impersonate another field's contribution.

    Each field is prefixed with its own length, so the reader of the packed
    string - the hash - can only decompose it one way. This is what a bare
    separator could not do: `draw.py` used to build its seed as
    `salt + "\\x1f" + policy`, and because `--salt` is free text that may itself
    contain `\\x1f`, an anchor-1 request carrying the salt `"\\x1fanchor=3"`
    produced a byte-identical hand to a genuine anchor-3 request. The downgrade
    cost nothing at all - not even a redraw.

    **Each field is normalized before it is measured**, and that ordering is the
    whole fix. The first length-prefixed version measured the raw field and left
    normalization to `seed_int`, which collapses whitespace runs - so the prefix
    described a string that no longer existed by the time it was hashed. Two
    salts of equal *raw* length packed differently and normalized identically,
    and `--anchor 1 --salt "x" + 88 spaces + "|8:anchor=3"` reproduced the
    anchor-3 hand byte for byte, exactly as the separator bug had. Measuring the
    post-normalization field closes it: `normalize` is idempotent, so the
    prefixes still describe the string the hash sees.

    U+001F is refused here rather than normalized away, because `normalize`
    treats it as whitespace and would silently merge two different requests onto
    one hand - and because `seed_int` can no longer see it once this function has
    folded it into a space.

    Packing an empty set of fields to the empty string keeps the plain request
    seeding exactly as it did before any policy field existed. Normalization runs
    before that test too, so a salt of only spaces is the same request as no salt
    at all, which is what every other comparison in this package already assumes.
    """
    for field in fields:
        if SEED_SEP in field:
            raise EngineError(
                "seed material may not contain the U+001F unit separator: it delimits the seed "
                "fields, so a value carrying one could impersonate another field's contribution")
    packed = [normalize(f) for f in fields]
    if not any(packed):
        return ""
    return "|".join(f"{len(f)}:{f}" for f in packed)


def seed_int(*parts: Any) -> int:
    """Hash the seed material.

    Parts are joined with a separator, so a part that contains the separator
    could shift the boundary between two parts and make one request's material
    read as another's. It is refused rather than sanitised: stripping it would
    map two different requests onto one hand, which is the property being
    defended. The check reads the raw part, not the normalized one, because
    `normalize` treats U+001F as whitespace and would hide it.

    Every field that reaches the seed was audited, not only `--salt`:
    `--topic` is free text and arrives here as its own part, so the separator
    check below is what pins its extent; `--modes` cannot be free text at all,
    because `resolve_modes` refuses any id the bundled deck does not carry, so
    the only mode strings that ever reach the seed are `extremal` and
    `grounded`; `--anchor` is an int checked against the deck's anchor levels
    and `--domains` an int with its own floor. The one free-text field left
    inside the packed part is the salt, and `pack_fields` measures it after
    normalization so its extent is pinned too.
    """
    raw = [str(p) for p in parts]
    for value in raw:
        if SEED_SEP in value:
            raise EngineError(
                "seed material may not contain the U+001F unit separator: it delimits the seed "
                "fields, so a value carrying one could impersonate another field's contribution")
    digest = hashlib.blake2b(
        SEED_SEP.join(normalize(value) for value in raw).encode("utf-8"), digest_size=16).digest()
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
