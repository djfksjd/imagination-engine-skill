#!/usr/bin/env python3
"""score_gate.py - the only path to "passed".

Everything that decides whether a result may be shown happens here, in one
call, against artefacts that must belong to each other:

  the draw      - replayed from its own request against the bundled decks, so a
                  card swapped after the fact no longer matches its own recipe
  the candidate - bound to that draw, and scored on the rubric profile the draw
                  implies rather than one asserted at the command line
  the ban list  - the model's own burnt instincts, with its manual entries
                  answered rather than printed
  the markdown  - the artefact that will actually be shown, bound to the
                  candidate that was scored and linted against the ban list

Two gates that never meet are one gate. Before this, score_gate validated
candidate.json while cliche_lint validated draft.md, and nothing tied the
passing candidate to the shown draft.

Usage:
  score_gate.py --candidate work/candidate.json --draw work/draw.json \
                --banlist work/banlist.json --markdown work/draft.md

Exit codes: 0 pass, 1 usage or parse error, 2 gate failed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from types import SimpleNamespace
from typing import Any

try:
    from engine import (  # type: ignore
        VERSION, EngineError, SKILL_DIR, UsageParser, die, is_placeholder, load_all_decks, text_units,
    )
    from cliche_lint import deck_entries, lint  # type: ignore
    from draw import DRAW_SCHEMA_VERSION, build_draw  # type: ignore
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from engine import (  # type: ignore
        VERSION, EngineError, SKILL_DIR, UsageParser, die, is_placeholder, load_all_decks, text_units,
    )
    from cliche_lint import deck_entries, lint  # type: ignore
    from draw import DRAW_SCHEMA_VERSION, build_draw  # type: ignore

GATE_FAIL = 2
MIN_JUSTIFICATION = 40
MIN_PROBE_ANSWER = 30
MIN_DIFFERENCE = 40
MIN_IMPOSSIBLE = 30
MIN_FIX = 40
MIN_MANUAL_ANSWER = 30

BIND = re.compile(r"<!--\s*bind:\s*([A-Za-z0-9_.\[\]]+)\s*-->(.*?)<!--\s*/bind\s*-->", re.S)


def build_parser() -> argparse.ArgumentParser:
    p = UsageParser(description="The single gate between a candidate and the user.")
    p.add_argument("--candidate", required=True, help="candidate.json (see references/candidate.schema.json)")
    p.add_argument("--draw", required=True, help="draw.json from draw.py - the run this candidate came from")
    p.add_argument("--banlist", required=True, help="banlist.json from banlist.py")
    p.add_argument("--markdown", required=True, help="the draft that will actually be shown")
    p.add_argument("--json", action="store_true", help="emit the verdict as JSON")
    return p


# ---------------------------------------------------------------- loading


def read_json(path: str, label: str) -> dict[str, Any]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EngineError(f"cannot read {label} {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise EngineError(f"{label} must be a JSON object")
    return data


def load_rubric() -> dict[str, Any]:
    """The bundled rubric is the policy. There is no --rubric.

    A rubric supplied at verdict time is a threshold override wearing a
    different name: the same caller who writes the candidate would write the
    policy it is judged by. A fork edits the bundled file and ships a different
    engine, which is a distribution decision rather than a per-run one.
    """
    target = SKILL_DIR / "references" / "rubric.json"
    try:
        raw = target.read_bytes()
        data = json.loads(raw.decode("utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EngineError(f"cannot read bundled rubric {target}: {exc}") from exc
    if "axes" not in data or "required_sections" not in data:
        raise EngineError(f"bundled rubric {target} is missing 'axes' or 'required_sections'")
    data["_sha256"] = hashlib.sha256(raw).hexdigest()
    return data


def text_of(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def section_minimum(spec: dict[str, Any]) -> int:
    return int(spec.get("min_units", spec.get("min_chars", 0)))


def canonical(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).split())


def _ids(items: Any) -> set[str]:
    return {i["id"] for i in items if isinstance(i, dict) and "id" in i} if isinstance(items, list) else set()


# ------------------------------------------------------- the draw, replayed


def replay_draw(draw: dict[str, Any], decks: dict[str, Any]) -> list[str]:
    """Deal the hand again from the draw's own request and compare.

    A hash of the submitted file proves nothing - whoever edited a card can
    recompute it. Redealing from the bundled decks is weaker than a signature
    and stronger than trust: it catches a card replaced after the fact, because
    the replacement no longer follows from the request that produced it.

    What this cannot show: that the topic came from the user, that this was the
    first draw, or that a salt was not chosen until the hand was agreeable.
    It is a consistency boundary, not an authenticity one.
    """
    failures: list[str] = []
    version = draw.get("draw_schema_version")
    if version != DRAW_SCHEMA_VERSION:
        raise EngineError(
            f"draw.json is schema version {version!r}, this gate reads {DRAW_SCHEMA_VERSION}. "
            "Redeal with the current draw.py")
    request = draw.get("request")
    if not isinstance(request, dict):
        raise EngineError("draw.json has no request block; redeal with the current draw.py")
    dealt = draw.get("draw")
    if not isinstance(dealt, dict):
        raise EngineError("draw.json has no draw block")

    try:
        expected = build_draw(SimpleNamespace(
            topic=request["topic"], modes=",".join(request["mode_ids"]), run=request["run"],
            anchor=request["anchor"], domains=request["requested_domains"],
            salt=request.get("salt", ""),
        ), decks)
    except (KeyError, TypeError) as exc:
        raise EngineError(f"draw.json request block is malformed: {exc}") from exc

    def one(node: Any) -> set[str]:
        return {node["id"]} if isinstance(node, dict) and "id" in node else set()

    for label, got, want in (
        ("domains", _ids(dealt.get("domains")), _ids(expected["draw"]["domains"])),
        ("constraints", _ids(dealt.get("constraints")), _ids(expected["draw"]["constraints"])),
        ("perspective", one(dealt.get("perspective")), one(expected["draw"]["perspective"])),
        ("sense", one(dealt.get("sense")), one(expected["draw"]["sense"])),
        ("affect_pair", one(dealt.get("affect_pair")), one(expected["draw"]["affect_pair"])),
    ):
        if got != want:
            failures.append(
                f"draw.{label}: does not follow from its own request - the file says {sorted(got)} "
                f"but that request deals {sorted(want)}. The hand was edited after it was dealt")
    return failures


def bind_candidate_to_draw(candidate: dict[str, Any], draw: dict[str, Any]) -> list[str]:
    """Every drawn component is binding, so every one of them is checked."""
    failures: list[str] = []
    request = draw["request"]
    dealt = draw["draw"]

    if canonical(text_of(candidate.get("topic"))) != canonical(str(request["topic"])):
        failures.append("topic: the candidate is not about the topic that was drawn")
    if candidate.get("run") != request["run"]:
        failures.append(f"run: candidate says {candidate.get('run')!r}, the draw was run {request['run']}")
    if candidate.get("anchor") != request["anchor"]:
        failures.append(f"anchor: candidate says {candidate.get('anchor')!r}, the draw was anchor {request['anchor']}")

    declared = candidate.get("modes")
    declared = {m for m in declared if isinstance(m, str)} if isinstance(declared, list) else set()
    if declared != set(request["mode_ids"]):
        failures.append(
            f"modes: candidate declares {sorted(declared)}, the draw was {sorted(request['mode_ids'])} - "
            "the profile the gate applies comes from the run, not from a claim")

    drawn_domains = _ids(dealt.get("domains"))
    used_ids = _ids(candidate.get("domains_used"))
    if used_ids != drawn_domains:
        failures.append(
            f"domains_used: {sorted(used_ids)} but the hand was {sorted(drawn_domains)}. Every drawn "
            "domain is binding - a domain that does no work is not dropped, it is replaced by redealing")

    broken = candidate.get("broken_rule") if isinstance(candidate.get("broken_rule"), dict) else {}
    claimed = broken.get("constraint_ids")
    claimed = set(claimed) if isinstance(claimed, list) else set()
    drawn_constraints = _ids(dealt.get("constraints"))
    if claimed != drawn_constraints:
        failures.append(
            f"broken_rule.constraint_ids: {sorted(claimed)} but the hand was {sorted(drawn_constraints)}")
    explained = broken.get("how_each_is_broken")
    explained_ids = (
        {e.get("constraint_id") for e in explained if isinstance(e, dict)}
        if isinstance(explained, list) else set()
    )
    if explained_ids != drawn_constraints:
        failures.append(
            "broken_rule.how_each_is_broken: must account for every drawn constraint by id - one "
            "replacement law may cover both, but neither may be silently dropped")
    elif isinstance(explained, list):
        for entry in explained:
            if text_units(text_of(entry.get("explanation"))) < MIN_IMPOSSIBLE:
                failures.append(
                    f"broken_rule.how_each_is_broken[{entry.get('constraint_id')}]: needs at least "
                    f"{MIN_IMPOSSIBLE} units")

    for field, node in (("perspective_id", dealt.get("perspective")),
                        ("sense_seed_id", dealt.get("sense")),
                        ("affect_pair_id", dealt.get("affect_pair"))):
        drawn = node.get("id") if isinstance(node, dict) else None
        if text_of(candidate.get(field)) != drawn:
            failures.append(f"{field}: candidate says {candidate.get(field)!r}, the draw was {drawn!r}")
    return failures


# ------------------------------------------------------------ the candidate


def check_candidate(candidate: dict[str, Any], rubric: dict[str, Any], min_mean: float, min_axis: int,
                    grounded: bool, needs_path: bool) -> tuple[list[str], list[str], dict[str, int], float]:
    failures: list[str] = []
    warnings: list[str] = []
    substitution = rubric.get("grounded_substitution", {})
    grounded_section = substitution.get("requires_section")

    sections = candidate.get("sections")
    if not isinstance(sections, dict):
        failures.append("sections: missing or not an object")
        sections = {}
    for spec in rubric["required_sections"]:
        if spec["id"] == grounded_section and not needs_path:
            continue
        body = text_of(sections.get(spec["id"]))
        if not body:
            failures.append(f"sections.{spec['id']}: missing - {spec['note']}")
        elif spec["id"] == "name":
            if is_placeholder(body):
                failures.append(f"sections.name: '{body}' is a placeholder, not a name - {spec['note']}")
        elif text_units(body) < section_minimum(spec):
            failures.append(
                f"sections.{spec['id']}: {text_units(body)} units, needs {section_minimum(spec)} - {spec['note']}")

    broken = candidate.get("broken_rule")
    if not isinstance(broken, dict):
        failures.append("broken_rule: missing - state which law was deleted and what replaced it")
    else:
        if text_units(text_of(broken.get("new_law"))) < MIN_IMPOSSIBLE:
            failures.append(f"broken_rule.new_law: needs at least {MIN_IMPOSSIBLE} units")
        if text_units(text_of(broken.get("now_impossible"))) < MIN_IMPOSSIBLE:
            failures.append(
                f"broken_rule.now_impossible: needs at least {MIN_IMPOSSIBLE} units - a world where "
                "the rule is merely gone is empty, not strange")

    domains = candidate.get("domains_used")
    if isinstance(domains, list):
        for i, d in enumerate(domains):
            if not isinstance(d, dict):
                failures.append(f"domains_used[{i}]: not an object")
                continue
            if text_units(text_of(d.get("answer_to_probe"))) < MIN_PROBE_ANSWER:
                failures.append(
                    f"domains_used[{i}] ({d.get('id') or '?'}).answer_to_probe: too thin - a domain that "
                    "answers nothing is a decoration; cut it or make it load-bearing")
    else:
        failures.append("domains_used: missing")

    resembles = candidate.get("resembles")
    if not isinstance(resembles, list) or not resembles:
        failures.append(
            "resembles: missing - name the nearest known works you checked against, or state "
            "explicitly what you searched and found nothing close to")
    else:
        for i, r in enumerate(resembles):
            if not isinstance(r, dict):
                failures.append(f"resembles[{i}]: not an object")
                continue
            if not text_of(r.get("work")):
                failures.append(f"resembles[{i}].work: missing")
            if text_units(text_of(r.get("how_it_differs"))) < MIN_DIFFERENCE:
                failures.append(f"resembles[{i}].how_it_differs: needs at least {MIN_DIFFERENCE} units")

    if text_units(text_of(candidate.get("weakest_fix"))) < MIN_FIX:
        failures.append(
            f"weakest_fix: needs at least {MIN_FIX} units - name the weakest axis and what a rewrite would change")

    axis_ids = [a["id"] for a in rubric["axes"]]
    if grounded and substitution:
        axis_ids = [substitution["axis"]["id"] if a == substitution["replaces"] else a for a in axis_ids]

    scores = candidate.get("scores")
    values: dict[str, int] = {}
    if not isinstance(scores, dict):
        failures.append("scores: missing or not an object")
    else:
        missing = [a for a in axis_ids if a not in scores]
        extra = [a for a in scores if a not in axis_ids]
        if missing:
            failures.append(f"scores: missing axes {', '.join(missing)}")
        if extra:
            failures.append(f"scores: unknown axes {', '.join(extra)}")
        for axis in axis_ids:
            entry = scores.get(axis)
            if entry is None:
                continue
            if not isinstance(entry, dict):
                failures.append(f"scores.{axis}: must be an object with 'score' and 'justification'")
                continue
            raw = entry.get("score")
            if not isinstance(raw, int) or isinstance(raw, bool) or not 1 <= raw <= 10:
                failures.append(f"scores.{axis}.score: must be an integer 1-10")
                continue
            values[axis] = raw
            if text_units(text_of(entry.get("justification"))) < MIN_JUSTIFICATION:
                failures.append(f"scores.{axis}.justification: needs at least {MIN_JUSTIFICATION} units of argument")

    mean = round(sum(values.values()) / len(values), 2) if values else 0.0
    if values and len(values) == len(axis_ids):
        if mean < min_mean:
            failures.append(f"mean {mean} is below the {min_mean} threshold - regenerate rather than resubmit")
        low = sorted((a for a in values if values[a] < min_axis), key=lambda a: values[a])
        if low:
            failures.append(
                f"axes below the floor of {min_axis}: " + ", ".join(f"{a}={values[a]}" for a in low))
        if len(set(values.values())) == 1:
            warnings.append("every axis has the same score, which usually means the rubric was filled in, not applied")
        if min(values.values()) >= 9:
            warnings.append("no axis below 9: self-scoring this generous is itself a signal - recheck the weakest part")
    return failures, warnings, values, mean


# -------------------------------------- the ban list and what will be shown


def check_banlist(candidate: dict[str, Any], banlist: dict[str, Any]) -> list[str]:
    """Manual entries used to be printed and then forgotten. Now they are answered."""
    failures: list[str] = []
    manual = banlist.get("manual_checks")
    manual = manual if isinstance(manual, list) else []
    cleared = candidate.get("manual_checks_cleared")
    cleared = cleared if isinstance(cleared, dict) else {}
    for entry in manual:
        if not isinstance(entry, dict) or "id" not in entry:
            failures.append("banlist.manual_checks: an entry has no id")
            continue
        answer = text_of(cleared.get(entry["id"]))
        if text_units(answer) < MIN_MANUAL_ANSWER:
            statement = str(entry.get("statement", ""))[:60]
            failures.append(
                f"manual_checks_cleared[{entry['id']}]: needs a written answer of at least "
                f"{MIN_MANUAL_ANSWER} units saying how the result avoids \"{statement}\" - "
                "a check that is only printed is not a check")
    return failures


def bound_blocks(markdown: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for match in BIND.finditer(markdown):
        out.setdefault(match.group(1), []).append(match.group(2))
    return out


def check_markdown(candidate: dict[str, Any], markdown: str, rubric: dict[str, Any],
                   banlist: dict[str, Any], needs_path: bool, decks: dict[str, Any]) -> list[str]:
    """The artefact that will be shown must be the one that was scored.

    Bound blocks rather than a similarity score: a fuzzy match cannot tell the
    difference between a passage being present and the same words being quoted
    inside a sentence that rejects them.
    """
    failures: list[str] = []
    sections = candidate.get("sections") if isinstance(candidate.get("sections"), dict) else {}
    blocks = bound_blocks(markdown)
    grounded_section = rubric.get("grounded_substitution", {}).get("requires_section")
    known = {f"sections.{s['id']}" for s in rubric["required_sections"]}

    for spec in rubric["required_sections"]:
        if spec["id"] == grounded_section and not needs_path:
            continue
        key = f"sections.{spec['id']}"
        found = blocks.get(key)
        if not found:
            failures.append(
                f"markdown: no <!-- bind: {key} --> block. The draft that gets shown has to carry the "
                "section that was scored, marked, so the two cannot drift apart")
            continue
        if len(found) > 1:
            failures.append(f"markdown: <!-- bind: {key} --> appears {len(found)} times; it must appear once")
            continue
        if canonical(found[0]) != canonical(text_of(sections.get(spec["id"]))):
            failures.append(
                f"markdown: the <!-- bind: {key} --> block is not the text that was scored. Update "
                "candidate.json to the final wording and re-gate; do not edit one side only")

    unknown = sorted(k for k in blocks if k not in known)
    if unknown:
        failures.append(f"markdown: bind blocks for unknown fields: {', '.join(unknown)}")

    entries = [e for e in (banlist.get("entries") or []) if isinstance(e, dict)]
    entries += [e for e in deck_entries(decks["cliches"]) if e["tier"] in ("ban", "warn")]
    patterns = [p for p in (banlist.get("structural_patterns") or []) if isinstance(p, dict)]
    for f in lint(markdown, entries, patterns, allow=set()):
        if f["tier"] != "ban":
            continue
        failures.append(
            f"markdown line {f['line']}: banned material '{f['match']}' [{f['id']}] - "
            "rewrite the thought, not the word")
    return failures


# ---------------------------------------------------------------------------


def gate(candidate: dict[str, Any], draw: dict[str, Any], banlist: dict[str, Any],
         markdown: str, rubric: dict[str, Any], decks: dict[str, Any]) -> dict[str, Any]:
    failures = replay_draw(draw, decks)
    failures += bind_candidate_to_draw(candidate, draw)

    # The profile is read off the validated run. There is no --extremal and no
    # --grounded: a flag is a claim made at verdict time, by the same party the
    # verdict is about.
    mode_ids = set(draw["request"]["mode_ids"])
    profile = "extremal" if "extremal" in mode_ids else "default"
    grounded = "grounded" in mode_ids
    anchor = int(draw["request"]["anchor"])
    # output-template.md requires the operational path at anchor 3 as well as in
    # grounded mode. The gate used to ask for it only in grounded, so anchor 3
    # could ship without the one thing that level is for.
    needs_path = grounded or anchor == 3
    thresholds = rubric[f"{profile}_thresholds"]
    min_mean, min_axis = float(thresholds["min_mean"]), int(thresholds["min_axis"])

    cand_failures, warnings, values, mean = check_candidate(
        candidate, rubric, min_mean, min_axis, grounded, needs_path)
    failures += cand_failures
    failures += check_banlist(candidate, banlist)
    failures += check_markdown(candidate, markdown, rubric, banlist, needs_path, decks)

    substitution = rubric.get("grounded_substitution", {})
    return {
        "engine_version": VERSION,
        "passed": not failures,
        "mean": mean,
        "policy": {
            "rubric": rubric.get("rubric", "imagination-engine"),
            "rubric_version": rubric.get("version"),
            "rubric_sha256": rubric["_sha256"],
            "profile": profile,
            "thresholds": {"min_mean": min_mean, "min_axis": min_axis},
            "anchor": anchor,
            "modes": sorted(mode_ids),
            "axis_substitution": substitution.get("axis", {}).get("id") if grounded else None,
        },
        "scores": values,
        "failures": failures,
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        rubric = load_rubric()
        decks = load_all_decks()
        candidate = read_json(args.candidate, "candidate")
        draw = read_json(args.draw, "draw")
        banlist = read_json(args.banlist, "ban list")
        try:
            markdown = Path(args.markdown).read_text(encoding="utf-8")
        except OSError as exc:
            raise EngineError(f"cannot read markdown {args.markdown}: {exc}") from exc
        verdict = gate(candidate, draw, banlist, markdown, rubric, decks)
    except EngineError as exc:
        die(str(exc), 1)
        return 1

    if args.json:
        print(json.dumps(verdict, ensure_ascii=False, indent=2))
    else:
        policy = verdict["policy"]
        print(f"POLICY LOCKED: {policy['rubric']}/{policy['rubric_version']} {policy['profile']}; "
              f"mean >= {policy['thresholds']['min_mean']}; every axis >= {policy['thresholds']['min_axis']}")
        print(f"mean {verdict['mean']}")
        for w in verdict["warnings"]:
            print(f"WARN  {w}")
        for f in verdict["failures"]:
            print(f"FAIL  {f}")
        print("PASSED - the required work is present." if verdict["passed"]
              else "GATE FAILED - do not show this to the user; fix or regenerate.")
    return 0 if verdict["passed"] else GATE_FAIL


if __name__ == "__main__":
    raise SystemExit(main())
