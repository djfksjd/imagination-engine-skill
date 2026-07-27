#!/usr/bin/env python3
"""cliche_lint.py - refuse to ship a draft that contains its own first instincts.

Reads a draft and the ban list produced by banlist.py, reports every banned
phrase, hollow adjective, and pitch-shaped sentence with a line number, and
fails the run if any 'ban' tier hit survives.

This catches the mechanical half of the problem only. A draft can pass the lint
and still be ordinary; that is what score_gate.py and the self-interrogation
checklist are for. The lint never certifies a result as strange - it only proves
that specific known-familiar moves are absent.

Usage:
  cliche_lint.py --banlist ./work/banlist.json --draft ./work/draft.md
  cliche_lint.py --draft - --deck-only        # no ban list yet, deck defaults

Exit codes: 0 clean, 1 usage error, 3 banned material present.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

try:
    from engine import (  # type: ignore
        VERSION, EngineError, csv_list, die, load_deck, normalize, phrase_regex, read_text_arg,
    )
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from engine import (  # type: ignore
        VERSION, EngineError, csv_list, die, load_deck, normalize, phrase_regex, read_text_arg,
    )

FAIL_CODE = 3


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Lint a draft against the ban list and the cliche deck.")
    p.add_argument("--draft", required=True, help="draft file, or '-' for stdin")
    p.add_argument("--banlist", default=None, help="banlist.json from banlist.py")
    p.add_argument("--deck-only", action="store_true", help="lint against deck defaults without a ban list")
    p.add_argument("--allow", default=None, help="comma-separated entry ids to ignore for this run")
    p.add_argument("--strict", action="store_true", help="treat warnings as failures too")
    p.add_argument("--json", action="store_true", help="emit findings as JSON")
    return p


def deck_entries(cliches: dict[str, Any]) -> list[dict[str, Any]]:
    entries = [
        {"id": p["id"], "phrase": p["phrase"], "tier": p["tier"], "group": p["group"], "source": "deck"}
        for p in cliches["phrases"]
    ]
    for tier in ("ban", "warn"):
        for word in cliches["hollow_adjectives"][tier]:
            entries.append({
                "id": f"hollow-{normalize(word).replace(' ', '-')}",
                "phrase": word,
                "tier": tier,
                "group": "hollow-adjective",
                "source": "deck",
            })
    return entries


def lint(draft: str, entries: list[dict[str, Any]], patterns: list[dict[str, Any]],
         allow: set[str]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    lines = draft.splitlines()
    compiled = []
    for e in entries:
        if e["id"] in allow or e.get("tier") == "manual":
            continue
        try:
            compiled.append((e, phrase_regex(e["phrase"])))
        except EngineError:
            continue
    compiled_patterns = []
    for p in patterns:
        if p["id"] in allow:
            continue
        try:
            compiled_patterns.append((p, re.compile(p["regex"], re.IGNORECASE)))
        except re.error as exc:
            raise EngineError(f"pattern {p['id']} is not a valid regex: {exc}") from exc

    for lineno, line in enumerate(lines, start=1):
        norm = normalize(line)
        if not norm:
            continue
        for e, rx in compiled:
            m = rx.search(norm)
            if m:
                findings.append({
                    "id": e["id"],
                    "kind": "phrase",
                    "tier": e["tier"],
                    "group": e.get("group", ""),
                    "source": e.get("source", ""),
                    "line": lineno,
                    "match": m.group(0),
                    "excerpt": line.strip()[:160],
                })
        for p, rx in compiled_patterns:
            m = rx.search(line)
            if m:
                findings.append({
                    "id": p["id"],
                    "kind": "pattern",
                    "tier": p["tier"],
                    "group": "structural",
                    "source": "deck",
                    "line": lineno,
                    "match": m.group(0),
                    "excerpt": line.strip()[:160],
                    "why": p.get("why", ""),
                })
    return findings


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if not args.banlist and not args.deck_only:
            raise EngineError("pass --banlist, or --deck-only to lint against deck defaults")
        cliches = load_deck("cliches")
        patterns = cliches["structural_patterns"]
        manual: list[dict[str, Any]] = []
        if args.banlist:
            try:
                payload = json.loads(Path(args.banlist).read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise EngineError(f"cannot read ban list {args.banlist}: {exc}") from exc
            entries = payload.get("entries", [])
            patterns = payload.get("structural_patterns", patterns)
            manual = payload.get("manual_checks", [])
            if not entries:
                raise EngineError("ban list contains no entries")
        else:
            entries = deck_entries(cliches)
        draft = read_text_arg(args.draft)
        findings = lint(draft, entries, patterns, set(csv_list(args.allow)))
    except EngineError as exc:
        die(str(exc), 1)
        return 1

    bans = [f for f in findings if f["tier"] == "ban"]
    warns = [f for f in findings if f["tier"] == "warn"]
    failed = bool(bans) or (args.strict and bool(warns))

    if args.json:
        print(json.dumps({
            "engine_version": VERSION,
            "failed": failed,
            "counts": {"ban": len(bans), "warn": len(warns), "manual": len(manual)},
            "findings": findings,
            "manual_checks": manual,
        }, ensure_ascii=False, indent=2))
    else:
        for f in bans:
            print(f"BAN   line {f['line']}: {f['match']!r} [{f['id']}] - {f['excerpt']}")
        for f in warns:
            print(f"WARN  line {f['line']}: {f['match']!r} [{f['id']}] - {f['excerpt']}")
        if manual:
            print("\nMANUAL CHECKS (not machine-checkable - reread the draft against these):")
            for m in manual:
                print(f"  - {m.get('statement', '')}")
        print(f"\n{len(bans)} banned, {len(warns)} warnings, {len(manual)} manual checks.")
        if failed:
            print("FAILED: rewrite the flagged lines. Deleting the word is not a fix - "
                  "the idea underneath it has to change.")
        else:
            print("PASSED the mechanical check. This says nothing about whether the idea is actually strange.")
    return FAIL_CODE if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
