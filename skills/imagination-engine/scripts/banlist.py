#!/usr/bin/env python3
"""banlist.py - turn the model's own first instincts into forbidden moves.

The single most effective creativity instruction is not "be more free", it is
"these particular answers are now unavailable". This script takes the obvious-
answer dump produced in stage 1 of the skill, merges it with the default cliche
deck, and emits a machine-checkable ban list for cliche_lint.py.

Short entries (<= 6 words) become matchable bans. Longer entries are kept as
'manual' reminders, because matching a fifteen-word sentence literally would
catch nothing while pretending to protect something.

Usage:
  banlist.py --topic "..." --obvious obvious.txt --out ./work
  ... | banlist.py --topic "..." --obvious - --out ./work

Exit codes: 0 ok, 1 usage or deck error, 2 the obvious dump is too short.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

try:
    from engine import (  # type: ignore
        VERSION, EngineError, UsageParser, csv_list, die, is_placeholder, load_deck, normalize,
        read_text_arg, write_json,
    )
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from engine import (  # type: ignore
        VERSION, EngineError, UsageParser, csv_list, die, is_placeholder, load_deck, normalize,
        read_text_arg, write_json,
    )

# SKILL.md asks for twelve. A caller-supplied floor made the requirement
# advisory: --min-obvious 0 with an empty file exited 0, which is the whole
# stage skipped with a passing status.
MIN_OBVIOUS = 12
MATCHABLE_MAX_WORDS = 6
BULLET = re.compile(r"^\s*(?:[-*+•]|\d+[.)])\s*")


def build_parser() -> argparse.ArgumentParser:
    p = UsageParser(description="Build a ban list from the obvious-answer dump plus the cliche deck.")
    p.add_argument("--topic", required=True, help="the subject being re-imagined")
    p.add_argument("--obvious", required=True, help="file with one obvious answer per line, or '-' for stdin")
    p.add_argument("--extra", default=None, help="comma-separated extra phrases to ban")
    p.add_argument("--allow", default=None, help="comma-separated cliche ids to release (the user asked for that genre)")
    p.add_argument("--out", default=None, help="directory to write banlist.json into")
    p.add_argument("--json", action="store_true", help="print the ban list as JSON only")
    return p


def parse_obvious(raw: str, strip_bullets: bool = True) -> list[str]:
    """Read the stage-1 dump into the twelve instincts it claims to carry.

    This is the *only* definition of what a line of the dump becomes, and it has
    to be, because `score_gate.py` re-reads the same lines back out of the built
    file and recomputes. Every normalisation that happens on one side has to
    happen on the other, or the builder produces a file its own sibling rejects
    with a message telling the user to build it with the builder. That happened
    twice:

    - `is_placeholder` was applied at the gate and not here, so a dump whose
      first line was `Untitled` built cleanly at twelve entries and replayed as
      eleven. The filter belongs here, where the user still has the dump open:
      the run now exits 2 with "the dump is too short", which is true and
      actionable, instead of exiting 0 and failing an hour later.
    - The bullet prefix was stripped here and then stripped *again* at the gate,
      so a legitimate nested bullet - `- - nested instinct` - was stored as
      `- nested instinct` by the builder and read as `nested instinct` by the
      gate. Bullet stripping is not idempotent, so the gate passes
      `strip_bullets=False`: the phrases it recovers have already been through
      this function once.
    """
    lines: list[str] = []
    seen: set[str] = set()
    for line in raw.splitlines():
        cleaned = BULLET.sub("", line) if strip_bullets else line
        cleaned = cleaned.strip().strip('"').strip()
        if len(cleaned) < 3:
            continue
        if cleaned.startswith("#"):
            continue
        if is_placeholder(cleaned):
            continue
        key = normalize(cleaned)
        if key in seen:
            continue
        seen.add(key)
        lines.append(cleaned)
    return lines


def build_banlist(args: argparse.Namespace, cliches: dict[str, Any]) -> dict[str, Any]:
    return compose_banlist(
        topic=args.topic,
        obvious=parse_obvious(read_text_arg(args.obvious)),
        extra=csv_list(args.extra),
        allow=set(csv_list(args.allow)),
        cliches=cliches,
    )


def compose_banlist(topic: str, obvious: list[str], extra: list[str], allow: set[str],
                    cliches: dict[str, Any]) -> dict[str, Any]:
    """Build the contract from already-parsed inputs.

    Split out from `build_banlist` so that score_gate.py can recompute the ban
    list this run's inputs imply and compare it with the file it was handed,
    rather than checking that some expected string appears somewhere in it.
    """
    if len(obvious) < MIN_OBVIOUS:
        raise EngineError(
            f"the obvious dump has {len(obvious)} usable entries but {MIN_OBVIOUS} are required. "
            "Stage 1 exists to burn your high-probability answers before you write; a short dump means "
            "the familiar answers are still available to you.",
        )

    known_ids = {p["id"] for p in cliches["phrases"]}
    unknown_allow = allow - known_ids
    if unknown_allow:
        raise EngineError(f"--allow references unknown cliche id(s): {', '.join(sorted(unknown_allow))}")

    entries: list[dict[str, Any]] = []
    for p in cliches["phrases"]:
        if p["id"] in allow:
            continue
        entries.append({
            "id": p["id"],
            "phrase": p["phrase"],
            "tier": p["tier"],
            "group": p["group"],
            "source": "deck",
        })
    for word in cliches["hollow_adjectives"]["ban"]:
        entries.append({
            "id": f"hollow-{normalize(word).replace(' ', '-')}",
            "phrase": word,
            "tier": "ban",
            "group": "hollow-adjective",
            "source": "deck",
        })
    for word in cliches["hollow_adjectives"]["warn"]:
        entries.append({
            "id": f"hollow-{normalize(word).replace(' ', '-')}",
            "phrase": word,
            "tier": "warn",
            "group": "hollow-adjective",
            "source": "deck",
        })

    manual: list[dict[str, str]] = []
    for i, item in enumerate(obvious, start=1):
        words = [w for w in re.split(r"\s+", item.strip()) if w]
        if len(words) <= MATCHABLE_MAX_WORDS:
            entries.append({
                "id": f"obvious-{i:02d}",
                "phrase": item,
                "tier": "ban",
                "group": "first-instinct",
                "source": "obvious-dump",
            })
        else:
            manual.append({
                "id": f"obvious-{i:02d}",
                "statement": item,
                "note": "too long to match literally - check this one by reading, not by grep",
            })

    for i, item in enumerate(extra, start=1):
        entries.append({
            "id": f"extra-{i:02d}",
            "phrase": item,
            "tier": "ban",
            "group": "user-specified",
            "source": "--extra",
        })

    # Deduplicate by phrase, but never let a deck entry displace a first
    # instinct: an instinct that happens to already be a cliche is still one of
    # the twelve, and the gate counts them to check that stage 1 happened.
    deduped: list[dict[str, Any]] = []
    seen: dict[str, int] = {}
    for e in entries:
        key = normalize(e["phrase"])
        if key in seen:
            existing = deduped[seen[key]]
            if existing["source"] == "deck" and e["source"] != "deck":
                deduped[seen[key]] = e
            continue
        seen[key] = len(deduped)
        deduped.append(e)

    return {
        "engine_version": VERSION,
        "topic": topic,
        "counts": {
            "obvious_supplied": len(obvious),
            "matchable": sum(1 for e in deduped if e["tier"] == "ban"),
            "warn": sum(1 for e in deduped if e["tier"] == "warn"),
            "manual": len(manual),
        },
        "allowed": sorted(allow),
        "entries": deduped,
        "manual_checks": manual,
        "structural_patterns": cliches["structural_patterns"],
        "forbidden_moves": cliches["moves"],
    }


def render_human(payload: dict[str, Any]) -> str:
    c = payload["counts"]
    lines = [
        f"BAN LIST for: {payload['topic']}",
        f"  {c['obvious_supplied']} first instincts burned, {c['matchable']} matchable bans, "
        f"{c['warn']} warnings, {c['manual']} manual checks",
    ]
    if payload["allowed"]:
        lines.append(f"  released on request: {', '.join(payload['allowed'])}")
    if payload["manual_checks"]:
        lines.append("")
        lines.append("MANUAL CHECKS (grep cannot help you here - reread the draft against these):")
        for m in payload["manual_checks"]:
            lines.append(f"  - {m['statement']}")
    lines.append("")
    lines.append("FORBIDDEN MOVES:")
    for m in payload["forbidden_moves"]:
        lines.append(f"  - {m}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        cliches = load_deck("cliches")
        payload = build_banlist(args, cliches)
    except EngineError as exc:
        code = 2 if "obvious dump" in str(exc) else 1
        die(str(exc), code)
        return code
    if args.out:
        out_path = Path(args.out) / "banlist.json"
        write_json(out_path, payload)
        if not args.json:
            print(f"wrote {out_path}")
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_human(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
