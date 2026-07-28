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
        VERSION, EngineError, UsageParser, csv_list, die, load_deck, normalize, read_text_arg, write_json,
    )
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from engine import (  # type: ignore
        VERSION, EngineError, UsageParser, csv_list, die, load_deck, normalize, read_text_arg, write_json,
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


def parse_obvious(raw: str) -> list[str]:
    lines: list[str] = []
    seen: set[str] = set()
    for line in raw.splitlines():
        cleaned = BULLET.sub("", line).strip().strip('"').strip()
        if len(cleaned) < 3:
            continue
        if cleaned.startswith("#"):
            continue
        key = normalize(cleaned)
        if key in seen:
            continue
        seen.add(key)
        lines.append(cleaned)
    return lines


def build_banlist(args: argparse.Namespace, cliches: dict[str, Any]) -> dict[str, Any]:
    obvious = parse_obvious(read_text_arg(args.obvious))
    if len(obvious) < MIN_OBVIOUS:
        raise EngineError(
            f"the obvious dump has {len(obvious)} usable entries but {MIN_OBVIOUS} are required. "
            "Stage 1 exists to burn your high-probability answers before you write; a short dump means "
            "the familiar answers are still available to you.",
        )

    allow = set(csv_list(args.allow))
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

    for i, item in enumerate(csv_list(args.extra), start=1):
        entries.append({
            "id": f"extra-{i:02d}",
            "phrase": item,
            "tier": "ban",
            "group": "user-specified",
            "source": "--extra",
        })

    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for e in entries:
        key = normalize(e["phrase"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(e)

    return {
        "engine_version": VERSION,
        "topic": args.topic,
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
