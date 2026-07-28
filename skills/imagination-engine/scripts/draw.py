#!/usr/bin/env python3
"""draw.py - deal the constraint hand for one imagination-engine run.

Why a script instead of "pick three unrelated fields yourself": a model asked to
free-associate reaches for the same small set of favourites (fungi, deep sea,
funerals) every time, which is exactly the high-probability behaviour this skill
exists to block. The draw is hash-seeded from the topic, guarantees that the
drawn domains span disjoint top-level categories, and advances to fresh material
on every subsequent run of the same topic.

Usage:
  draw.py --topic "a machine that separates emotion from voice" \
          --modes baby,nonhuman,affect --run 1 --anchor 1 --out ./work

Exit codes: 0 ok, 1 usage or deck error.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from engine import (  # type: ignore
        VERSION, EngineError, UsageParser, csv_list, die, load_all_decks, pack_fields, round_robin,
        slice_by_run, stable_shuffle, write_json,
    )
except ImportError:  # executed from another cwd via absolute path
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from engine import (  # type: ignore
        VERSION, EngineError, UsageParser, csv_list, die, load_all_decks, pack_fields, round_robin,
        slice_by_run, stable_shuffle, write_json,
    )

DEFAULT_DOMAINS = 3
MIN_DOMAINS = 3
MAX_STACKED_MODES = 3
DRAW_SCHEMA_VERSION = 2

# The request fields the gate reads when it decides what it will require. See
# policy_seed below for why they have to reach the deal.
DEFAULT_ANCHOR = 1
POLICY_MODES = ("extremal", "grounded")


def policy_seed(mode_ids: list[str], anchor: int, domains: int) -> list[str]:
    """Fold everything the gate reads off the request into the seed.

    A request field the gate consults but the deal ignores can be rewritten
    afterwards and still replay clean, because the hand never depended on it.
    --anchor was exactly that: editing 3 to 1 in draw.json deleted the
    operational_path requirement and the replay saw nothing, which is a
    threshold set at verdict time by the party the verdict is about. Same
    property for `grounded`, which substitutes a rubric axis and requires a
    section, and for the requested domain count, which the extremal cap can
    swallow. So those fields seed the shuffle: an edit no longer relaxes the
    verdict, it deals a different hand, and the work already written stops
    belonging to the request.

    A field at its documented default contributes nothing, so the plain request
    deals the baseline hand. Each field carries its own prefix, so two requests
    that differ anywhere here get different seeds - including a change away from
    a default. The parts are returned separately and packed with `pack_fields`
    alongside the salt, because joining them into one string with a separator was
    itself the hole: see `compose_seed` below.

    What this still cannot do is distinguish a downgraded run from an honest one
    that was dealt at the lower setting from the start. Redealing is always
    available; what it costs is the hand, and therefore the work.
    """
    parts: list[str] = []
    if anchor != DEFAULT_ANCHOR:
        parts.append(f"anchor={anchor}")
    for mode in POLICY_MODES:
        if mode in mode_ids:
            parts.append(f"mode={mode}")
    if domains != DEFAULT_DOMAINS:
        parts.append(f"domains={domains}")
    return parts


def compose_seed(salt: str, policy_parts: list[str]) -> str:
    """Combine the caller's salt with the policy fields, unambiguously.

    The first version of this was `f"{salt}\\x1f{policy}"`, which meant the salt
    could simply *be* the policy: `--anchor 1 --salt $'\\x1fanchor=3'` dealt the
    identical hand to `--anchor 3 --salt ""`, and the gate then accepted a run
    that owed no operational path. `pack_fields` length-prefixes each field, so
    the salt's extent is pinned and no value of it can spell another field.

    Honest limit, unchanged by this: none of it proves the run was not redealt
    until the hand suited. It costs a redraw and the work already written against
    the old hand - it is not a forgery barrier.
    """
    return pack_fields(salt, *policy_parts)

# grounded substitutes the axis that nonhuman mode exists to enforce. Allowing
# the pair means one mode silently cancels the other, so it is refused here
# rather than at the gate - the draw is where the run is defined.
INCOMPATIBLE_MODES = [("grounded", "nonhuman")]


def build_parser() -> argparse.ArgumentParser:
    p = UsageParser(description="Deal the constraint hand for an imagination-engine run.")
    p.add_argument("--topic", help="the subject to be re-imagined")
    p.add_argument("--modes", default=None, help="comma-separated mode ids (see --list-modes)")
    p.add_argument("--run", type=int, default=1, help="run index; higher runs draw fresh material (default 1)")
    p.add_argument("--anchor", type=int, default=1, help="anchor level 0-3 (default 1)")
    p.add_argument("--domains", type=int, default=DEFAULT_DOMAINS, help="how many distant domains to draw (default 3)")
    p.add_argument("--salt", default="", help="extra seed material; change it to redeal the same run")
    p.add_argument("--out", default=None, help="directory to write draw.json into")
    p.add_argument("--json", action="store_true", help="print the draw as JSON only")
    p.add_argument("--list-modes", action="store_true", help="list available modes and anchors, then exit")
    return p


def list_modes(decks: dict[str, Any]) -> None:
    modes = decks["modes"]
    print("modes:")
    for m in modes["modes"]:
        print(f"  {m['id']:<14} {m['label']}")
    print("\nanchors:")
    for a in modes["anchors"]:
        print(f"  {a['level']}  {a['label']:<12} {a['rule']}")
    print(f"\ndefault modes: {', '.join(modes['default_modes'])}")


def resolve_modes(decks: dict[str, Any], requested: list[str]) -> list[dict[str, Any]]:
    table = {m["id"]: m for m in decks["modes"]["modes"]}
    if not requested:
        requested = list(decks["modes"]["default_modes"])
    unknown = [m for m in requested if m not in table]
    if unknown:
        raise EngineError(
            f"unknown mode(s): {', '.join(unknown)}; available: {', '.join(table)}"
        )
    seen: list[str] = []
    for m in requested:
        if m not in seen:
            seen.append(m)
    return [table[m] for m in seen]


def draw_domains(
    decks: dict[str, Any], topic: str, salt: str, run: int, count: int, forced_categories: list[str]
) -> tuple[list[dict[str, Any]], bool]:
    deck = decks["domains"]
    categories = [c["id"] for c in deck["categories"]]
    if count > len(categories):
        raise EngineError(
            f"--domains {count} exceeds the {len(categories)} available top-level categories; "
            "disjointness could not be guaranteed"
        )
    by_cat: dict[str, list[dict[str, Any]]] = {c: [] for c in categories}
    for d in deck["domains"]:
        if d["category"] not in by_cat:
            raise EngineError(f"domain {d['id']} has unknown category {d['category']}")
        by_cat[d["category"]].append(d)
    for cat in categories:
        if not by_cat[cat]:
            raise EngineError(f"category {cat} has no domains")

    ordered_cats = stable_shuffle(categories, topic, salt, "categories")
    groups = [stable_shuffle(by_cat[c], topic, salt, "domain", c) for c in ordered_cats]
    picked, wrapped = slice_by_run(round_robin(groups), run, count)

    for forced in forced_categories:
        if forced not in by_cat:
            raise EngineError(f"a mode forces unknown domain category '{forced}'")
        if any(d["category"] == forced for d in picked):
            continue
        pool = stable_shuffle(by_cat[forced], topic, salt, "forced", forced)
        replacement = pool[(run - 1) % len(pool)]
        picked[-1] = replacement
    return picked, wrapped


def draw_one(decks: dict[str, Any], deck_name: str, key: str, topic: str, salt: str, run: int, count: int = 1):
    items = decks[deck_name][key]
    ordered = stable_shuffle(items, topic, salt, deck_name)
    picked, wrapped = slice_by_run(ordered, run, count)
    return picked, wrapped


def build_draw(args: argparse.Namespace, decks: dict[str, Any]) -> dict[str, Any]:
    modes = resolve_modes(decks, csv_list(args.modes))
    mode_ids = [m["id"] for m in modes]
    extremal = "extremal" in mode_ids

    anchors = {a["level"]: a for a in decks["modes"]["anchors"]}
    if args.anchor not in anchors:
        raise EngineError(f"--anchor must be one of {sorted(anchors)}")
    if args.run < 1:
        raise EngineError("--run must be 1 or greater")
    if args.domains < MIN_DOMAINS:
        raise EngineError(
            f"--domains must be at least {MIN_DOMAINS}; below that the hand stops being a spread "
            "and the candidate contract cannot require every drawn domain to do work")
    if len(modes) > MAX_STACKED_MODES:
        raise EngineError(
            f"{len(modes)} modes stacked; the limit is {MAX_STACKED_MODES}. Above that the removals "
            "overlap and the result is noisy rather than strange - pick the three that matter")
    for a, b in INCOMPATIBLE_MODES:
        if a in mode_ids and b in mode_ids:
            raise EngineError(
                f"modes {a} and {b} cannot be stacked: {a} substitutes the rubric axis that {b} "
                "exists to enforce, so one of them would have no effect. Pick one")

    forced_categories = []
    forced_decks = set()
    for m in modes:
        for force in m.get("forces", []):
            if ":" in force:
                deck_name, cat = force.split(":", 1)
                if deck_name == "domains":
                    forced_categories.append(cat)
                forced_decks.add(deck_name)
            else:
                forced_decks.add(force)

    category_count = len(decks["domains"]["categories"])
    if args.domains > category_count:
        raise EngineError(
            f"--domains {args.domains} exceeds the {category_count} available top-level categories; "
            "disjointness could not be guaranteed"
        )
    # Extremal doubles the draw, but never past the point where two domains would
    # have to share a category - the distance guarantee outranks the width.
    domain_count = min(args.domains * 2, category_count) if extremal else args.domains
    # Not args.salt: the seed carries the policy-bearing request fields too, so
    # that none of them can be rewritten afterwards without changing the hand.
    seed = compose_seed(args.salt or "", policy_seed(mode_ids, args.anchor, args.domains))
    domains, wrapped_d = draw_domains(decks, args.topic, seed, args.run, domain_count, forced_categories)

    constraint_count = 2 if extremal else 1
    constraints, wrapped_c = draw_one(decks, "constraints", "constraints", args.topic, seed, args.run, constraint_count)
    perspectives, wrapped_p = draw_one(decks, "perspectives", "perspectives", args.topic, seed, args.run)
    senses, wrapped_s = draw_one(decks, "senses", "senses", args.topic, seed, args.run)
    affects, wrapped_a = draw_one(decks, "affects", "pairs", args.topic, seed, args.run)

    cliches = decks["cliches"]
    banned_phrases = [p for p in cliches["phrases"] if p["tier"] == "ban"]

    thresholds = {"min_mean": 9.0, "min_axis": 8} if extremal else {"min_mean": 8.0, "min_axis": 6}

    required = ["domains", "constraints", "perspectives", "senses", "affects"]
    checklist = [
        f"Every drawn domain must answer its probe inside the result; a domain that is only mentioned is a decoration - cut it or replace it.",
        f"The drawn constraint must be broken AND replaced by a new law that makes something newly impossible.",
        f"The drawn perspective governs the whole result; if the result survives its removal, it was never applied.",
        f"Both affects in the pair must be produced by the same feature.",
        f"No phrase from the ban list, no hollow adjective, no 'X meets Y' pitch.",
        f"Before writing, list the {12} most probable answers to this topic and forbid all of them (banlist.py).",
        f"Score the result with score_gate.py; mean below {thresholds['min_mean']} does not ship.",
    ]

    payload: dict[str, Any] = {
        "engine_version": VERSION,
        "draw_schema_version": DRAW_SCHEMA_VERSION,
        # The request is what the gate replays. Everything below it is derived,
        # so a card swapped after the fact no longer matches its own recipe.
        "request": {
            "topic": args.topic,
            "run": args.run,
            "salt": args.salt,
            "mode_ids": mode_ids,
            "anchor": args.anchor,
            "requested_domains": args.domains,
        },
        "topic": args.topic,
        "run": args.run,
        "salt": args.salt,
        "modes": [
            {"id": m["id"], "label": m["label"], "directives": m["directives"], "guard": m["guard"]}
            for m in modes
        ],
        "anchor": anchors[args.anchor],
        "draw": {
            "domains": domains,
            "constraints": constraints,
            "perspective": perspectives[0],
            "sense": {**senses[0], "required_fields": decks["senses"]["required_fields"]},
            "affect_pair": affects[0],
        },
        "requirements": {
            "required_by_modes": sorted(forced_decks),
            "all_drawn_components_are_binding": required,
            "thresholds": thresholds,
            "domain_categories": sorted({d["category"] for d in domains}),
        },
        "forbidden_moves": cliches["moves"],
        "banned_phrase_count": len(banned_phrases),
        "deck_wrapped": any([wrapped_d, wrapped_c, wrapped_p, wrapped_s, wrapped_a]),
        "notes": [],
    }

    if payload["deck_wrapped"]:
        payload["notes"].append(
            "A deck wrapped around to material already used at this run depth. Change --salt for genuinely fresh cards."
        )
    if len({d["category"] for d in domains}) != len(domains):
        payload["notes"].append(
            "Forced-category substitution produced a repeated category; distance between domains is reduced."
        )
    return payload


def render_human(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"IMAGINATION ENGINE - draw for: {payload['topic']}")
    lines.append(f"run {payload['run']}  |  modes: {', '.join(m['id'] for m in payload['modes'])}  "
                 f"|  anchor {payload['anchor']['level']} ({payload['anchor']['label']})")
    lines.append("")
    lines.append("DISTANT DOMAINS (each must answer its probe):")
    for d in payload["draw"]["domains"]:
        lines.append(f"  - [{d['category']}] {d['label']}")
        lines.append(f"      probe: {d['probe']}")
    lines.append("")
    lines.append("RULE TO BREAK:")
    for c in payload["draw"]["constraints"]:
        lines.append(f"  - {c['statement']}")
        lines.append(f"      invert: {c['inversion_prompt']}")
        lines.append(f"      then:   {c['replacement_requirement']}")
    p = payload["draw"]["perspective"]
    lines.append("")
    lines.append(f"PERSPECTIVE: {p['stance']}")
    lines.append(f"      test:   {p['test']}")
    s = payload["draw"]["sense"]
    lines.append("")
    lines.append(f"SENSE SEED: {s['seed']}")
    for field in s["required_fields"]:
        lines.append(f"      must define - {field}")
    a = payload["draw"]["affect_pair"]
    lines.append("")
    lines.append(f"AFFECT PAIR: {a['a']} + {a['b']}")
    lines.append(f"      test:   {a['test']}")
    lines.append("")
    lines.append(f"THRESHOLDS: mean >= {payload['requirements']['thresholds']['min_mean']}, "
                 f"no axis < {payload['requirements']['thresholds']['min_axis']}")
    lines.append("")
    lines.append("MODE DIRECTIVES:")
    for m in payload["modes"]:
        lines.append(f"  [{m['id']}] {m['label']}")
        for d in m["directives"]:
            lines.append(f"      - {d}")
        lines.append(f"      guard: {m['guard']}")
    if payload["notes"]:
        lines.append("")
        lines.append("NOTES:")
        for n in payload["notes"]:
            lines.append(f"  ! {n}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        decks = load_all_decks()
        if args.list_modes:
            list_modes(decks)
            return 0
        if not args.topic or not args.topic.strip():
            raise EngineError("--topic is required")
        payload = build_draw(args, decks)
    except EngineError as exc:
        die(str(exc), 1)
        return 1
    if args.out:
        out_path = Path(args.out) / "draw.json"
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
