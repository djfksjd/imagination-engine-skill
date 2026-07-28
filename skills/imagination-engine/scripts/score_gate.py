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
        VERSION, EngineError, SKILL_DIR, UsageParser, die, distinct_ratio, is_placeholder,
        load_all_decks, normalize, text_units,
    )
    from banlist import MIN_OBVIOUS, compose_banlist, parse_obvious  # type: ignore
    from cliche_lint import deck_entries, lint  # type: ignore
    from draw import DRAW_SCHEMA_VERSION, build_draw  # type: ignore
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from engine import (  # type: ignore
        VERSION, EngineError, SKILL_DIR, UsageParser, die, distinct_ratio, is_placeholder,
        load_all_decks, normalize, text_units,
    )
    from banlist import MIN_OBVIOUS, compose_banlist, parse_obvious  # type: ignore
    from cliche_lint import deck_entries, lint  # type: ignore
    from draw import DRAW_SCHEMA_VERSION, build_draw  # type: ignore

GATE_FAIL = 2
MIN_JUSTIFICATION = 40
MIN_PROBE_ANSWER = 30
MIN_DIFFERENCE = 40
MIN_IMPOSSIBLE = 30
MIN_FIX = 40
MIN_MANUAL_ANSWER = 30
# Below this share of distinct tokens a field is filler that happens to be long
# enough. Ordinary prose in any language scores far above it; forty repeated
# letters scores zero.
MIN_DISTINCT_RATIO = 0.35

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


def check_text(label: str, value: Any, minimum: int = 0, note: str = "",
               titles_ok: bool = False) -> list[str]:
    """The one place a written field is judged.

    Every floor in this gate used to be a length comparison and nothing else,
    which made all of them satisfiable by one repeated letter, and left the
    fields with no length floor - `sections.name` aside - satisfiable by a
    hyphen. So each field is asked the same three questions here: is there
    anything, is it a stand-in, and is it argument rather than filler.

    The third question is only asked where there is a floor to pad towards. Asked
    everywhere, it rejected honest short answers that were never claiming to be
    long ones: the title "Run Run Run" scored 0.33 distinct, and so did a
    four-character CJK title built on a repeated character. A gate that rejects
    honest work is the reason a user turns it off, which costs more than the
    padding it caught.
    """
    failures: list[str] = []
    body = text_of(value)
    tail = f" - {note}" if note else ""
    if not body:
        failures.append(f"{label}: missing{tail}")
        return failures
    if is_placeholder(body, titles_ok=titles_ok):
        failures.append(f"{label}: '{body[:40]}' is a placeholder, not content{tail}")
        return failures
    if not minimum:
        return failures
    if text_units(body) < minimum:
        failures.append(f"{label}: {text_units(body)} units, needs {minimum}{tail}")
    ratio = distinct_ratio(body)
    if ratio < MIN_DISTINCT_RATIO:
        failures.append(
            f"{label}: repeated filler rather than content ({ratio:.2f} distinct) - a length floor "
            "asks for an amount of argument, not an amount of typing")
    return failures


def canonical(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).split())


def _ids(items: Any) -> set[str]:
    return {i["id"] for i in items if isinstance(i, dict) and "id" in i} if isinstance(items, list) else set()


def _card_ids(node: Any) -> set[str]:
    """Ids of a drawn slot, whether the slot holds one card or several."""
    if isinstance(node, list):
        return _ids(node)
    return {node["id"]} if isinstance(node, dict) and "id" in node else set()


def _edited_fields(got: Any, want: Any) -> list[str]:
    """Which keys of a card differ, for a message that names the edit."""
    got_list = got if isinstance(got, list) else [got]
    want_list = want if isinstance(want, list) else [want]
    changed: list[str] = []
    for a, b in zip(got_list, want_list):
        if not isinstance(a, dict) or not isinstance(b, dict):
            continue
        for key in sorted(set(a) | set(b)):
            if a.get(key) != b.get(key) and key not in changed:
                changed.append(key)
    return changed


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

    # Whole cards, not their ids. Comparing id sets left every word on the card
    # trusted: a domain keeping its id while its probe became "merely mention
    # this card" replayed clean, and draw.json then recorded, as a dealt hand,
    # instructions that were never dealt. The ids are still reported separately
    # because "you swapped a card" and "you rewrote one" are different mistakes.
    for label in ("domains", "constraints", "perspective", "sense", "affect_pair"):
        got, want = dealt.get(label), expected["draw"][label]
        if got == want:
            continue
        got_ids, want_ids = _card_ids(got), _card_ids(want)
        if got_ids != want_ids:
            failures.append(
                f"draw.{label}: does not follow from its own request - the file says {sorted(got_ids)} "
                f"but that request deals {sorted(want_ids)}. The hand was edited after it was dealt")
        else:
            failures.append(
                f"draw.{label}: carries the cards this request deals but not their text - "
                f"{', '.join(_edited_fields(got, want)) or 'the card body'} differs from the deck. A "
                "card whose probe, stance or replacement requirement was rewritten is a different card")

    # The rest of the file is derived from the same request, and the human-
    # readable half is what the user was shown. If it disagrees with the request
    # the gate reads, one of the two was rewritten afterwards.
    def mode_ids(node: Any) -> list[str]:
        return [m.get("id") for m in node if isinstance(m, dict)] if isinstance(node, list) else []

    anchor_level = draw.get("anchor", {}).get("level") if isinstance(draw.get("anchor"), dict) else None
    for label, got, want in (
        ("topic", draw.get("topic"), expected["topic"]),
        ("run", draw.get("run"), expected["run"]),
        ("salt", draw.get("salt"), expected["salt"]),
        ("anchor.level", anchor_level, expected["anchor"]["level"]),
        ("modes", mode_ids(draw.get("modes")), mode_ids(expected["modes"])),
        ("requirements.domain_categories",
         (draw.get("requirements") or {}).get("domain_categories"),
         expected["requirements"]["domain_categories"]),
    ):
        if got != want:
            failures.append(
                f"draw.{label}: says {got!r} while the request it carries produces {want!r}. The file "
                "and the request no longer describe the same run")

    # And every remaining key, by name. The checks above enumerate the fields
    # that were thought to matter, which left the rest of a recomputable file
    # unread: `notes` is prose the user was shown, `banned_phrase_count` and
    # `deck_wrapped` are what the run reported about itself, and all three could
    # be rewritten after the deal without a word from here. The whole file is
    # recomputed anyway, so comparing all of it costs nothing and removes the
    # question of which fields are covered.
    # Only the request itself is exempt: it is the input, not a result of it.
    checked = {"request"}
    for key in sorted(set(draw) | set(expected)):
        if key in checked:
            continue
        if draw.get(key) != expected.get(key):
            failures.append(
                f"draw.{key}: says {str(draw.get(key))[:60]!r} while this request produces "
                f"{str(expected.get(key))[:60]!r} - every field of a dealt hand is recomputed, "
                "including the ones only the reader sees")
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
        # check_text, not a bare length comparison: this field kept its own copy
        # of the floor and so was the one field the anti-padding rule never
        # reached - thirty repeated letters satisfied it.
        for entry in explained:
            failures += check_text(
                f"broken_rule.how_each_is_broken[{entry.get('constraint_id')}]",
                entry.get("explanation"), MIN_IMPOSSIBLE,
                "say what the drawn constraint stopped being able to do")

    for field, node in (("perspective_id", dealt.get("perspective")),
                        ("sense_seed_id", dealt.get("sense")),
                        ("affect_pair_id", dealt.get("affect_pair"))):
        drawn = node.get("id") if isinstance(node, dict) else None
        if text_of(candidate.get(field)) != drawn:
            failures.append(f"{field}: candidate says {candidate.get(field)!r}, the draw was {drawn!r}")
    return failures


# ------------------------------------------------------------ the candidate


def check_candidate(candidate: dict[str, Any], rubric: dict[str, Any],
                    grounded: bool, needs_path: bool, affect: bool) -> tuple[list[str], list[str], dict[str, int], float]:
    """Every structural requirement, and no numeric threshold.

    The eight axes are still required, still have to be integers, and still have
    to be argued in writing - answering them changes the work. What was removed
    is the comparison: no mean and no per-axis floor decides the verdict.

    The measurement that removed it: twenty gated runs across four unrelated
    briefs self-scored into the interval [8.00, 8.25], fourteen of them on
    exactly 8.125, against a threshold of 8.0 - including runs blind judges
    ranked last in their pile. A number with no observed variance cannot tell a
    good run from a bad one; what it could do was let the party the verdict is
    about write the verdict. This file had already refused --min-mean,
    --min-axis and --rubric for exactly that reason and then accepted the score
    itself, which is the same hole one level down.

    A low axis is now reported as a warning naming the axis, because it is worth
    reading; it does not fail the run. Every structural check above and below is
    unchanged and exactly as strict as it was - those are the ones that
    demonstrably catch things.
    """
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
        failures += check_text(
            f"sections.{spec['id']}", sections.get(spec["id"]), section_minimum(spec), spec["note"])

    broken = candidate.get("broken_rule")
    if not isinstance(broken, dict):
        failures.append("broken_rule: missing - state which law was deleted and what replaced it")
    else:
        failures += check_text("broken_rule.new_law", broken.get("new_law"), MIN_IMPOSSIBLE)
        failures += check_text(
            "broken_rule.now_impossible", broken.get("now_impossible"), MIN_IMPOSSIBLE,
            "a world where the rule is merely gone is empty, not strange")

    # SKILL.md says the affect card "requires an invented sense with all four
    # fields answered", and candidate.schema.json says the same. Nothing checked
    # it: a run could draw affect, skip the field entirely, and pass. A
    # requirement stated in two documents and enforced in none is the same
    # silence as a ban that stops firing - the reader believes it was applied.
    if affect:
        sense = candidate.get("invented_sense")
        if not isinstance(sense, dict):
            failures.append(
                "invented_sense: missing - the affect card was dealt, and it requires an invented "
                "sense with detects, mechanism, consequence and cost all answered")
        else:
            for field in ("detects", "mechanism", "consequence", "cost"):
                failures += check_text(f"invented_sense.{field}", sense.get(field), MIN_IMPOSSIBLE)

    domains = candidate.get("domains_used")
    if isinstance(domains, list):
        for i, d in enumerate(domains):
            if not isinstance(d, dict):
                failures.append(f"domains_used[{i}]: not an object")
                continue
            failures += check_text(
                f"domains_used[{i}] ({d.get('id') or '?'}).answer_to_probe", d.get("answer_to_probe"),
                MIN_PROBE_ANSWER,
                "a domain that answers nothing is a decoration; cut it or make it load-bearing")
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
            # titles_ok: a great many real works are called "Untitled", and this
            # is a citation field, not a field the author names themselves.
            failures += check_text(
                f"resembles[{i}].work", r.get("work"), 0,
                "name the work, or state what you searched and found nothing close to",
                titles_ok=True)
            failures += check_text(f"resembles[{i}].how_it_differs", r.get("how_it_differs"), MIN_DIFFERENCE)

    failures += check_text(
        "weakest_fix", candidate.get("weakest_fix"), MIN_FIX,
        "name the weakest axis and what a rewrite would change")

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
            failures += check_text(
                f"scores.{axis}.justification", entry.get("justification"), MIN_JUSTIFICATION,
                "argue the score")

    mean = round(sum(values.values()) / len(values), 2) if values else 0.0
    if values and len(values) == len(axis_ids):
        weakest = min(values, key=lambda a: values[a])
        if values[weakest] <= 4:
            warnings.append(
                f"weakest axis {weakest}={values[weakest]}: read that axis's own question again and "
                "check that weakest_fix names this, not something easier. This is a warning, not a "
                "verdict - no score decides whether this run passes")
        if len(set(values.values())) == 1:
            warnings.append("every axis has the same score, which usually means the rubric was filled in, not applied")
        if min(values.values()) >= 9:
            warnings.append("no axis below 9: self-scoring this generous is itself a signal - recheck the weakest part")
    return failures, warnings, values, mean


# -------------------------------------- the ban list and what will be shown


OBVIOUS_ID = re.compile(r"obvious-\d+")
EXTRA_ID = re.compile(r"extra-\d+")


def marks_instinct(entry: dict[str, Any]) -> bool:
    """Does this row record a burnt first instinct, by any of the marks it carries?

    Three independent marks, any one of which counts: the group, the source and
    the reserved id. banlist.py writes all three together, so a row that has lost
    two of them is still recognised by the third. See `protected_statements`.
    """
    return (entry.get("group") == "first-instinct"
            or entry.get("source") == "obvious-dump"
            or bool(OBVIOUS_ID.fullmatch(str(entry.get("id")))))


def marks_user_prohibition(entry: dict[str, Any]) -> bool:
    """Same question for a row that records one of the user's own exclusions."""
    return (entry.get("group") == "user-specified"
            or entry.get("source") == "--extra"
            or bool(EXTRA_ID.fullmatch(str(entry.get("id")))))


def recover_dump(banlist: dict[str, Any]) -> list[str]:
    """Reconstruct, in order, the stage-1 dump this file says it was built from.

    banlist.py numbers every line of the dump `obvious-NN` and files it either as
    a matchable entry or, if it is too long to match literally, as a manual
    check. Reading both back by that number recovers the input; recomputing from
    it is what turns "these strings appear somewhere" into "this is the file
    banlist.py would have written".

    A row is read as an instinct if *any* of its three marks says so. Selecting
    on the group alone made one keystroke enough to delete a line from the dump:
    retyping `first-instinct` as `deck` dropped the row out of this function, the
    recomputed contract no longer carried the phrase, and the draft printed it.
    """
    numbered: list[tuple[int, str]] = []
    for entry in banlist.get("entries") or []:
        if isinstance(entry, dict) and marks_instinct(entry):
            numbered.append((_dump_index(entry.get("id")), str(entry.get("phrase", ""))))
    for check in banlist.get("manual_checks") or []:
        if isinstance(check, dict):
            numbered.append((_dump_index(check.get("id")), str(check.get("statement", ""))))
    return [text for _, text in sorted(numbered, key=lambda pair: pair[0])]


def _dump_index(entry_id: Any) -> int:
    match = re.fullmatch(r"obvious-(\d+)", str(entry_id))
    return int(match.group(1)) if match else 10**6


def protected_statements(dump: list[str], extra: list[str]) -> list[dict[str, str]]:
    """The statements the gate enforces by content, whatever else the file says.

    Every other check in this file reads *something* the run wrote about a rule -
    its id, its group, its tier, its source, its membership of `extra` - to decide
    what the contract is. Each of those readings is a lever: five separate edits
    to banlist.json were found that left a protected phrase sitting in the file,
    in plain sight, and stopped it being enforced. Deleting the `extra` field
    while leaving the row; demoting the leftover row to `warn`; renaming its id
    onto a bundled deck id; retyping an instinct's group as `deck`; deleting an
    instinct row outright once the dump was longer than the twelve-line floor.
    Every one of them exited 0 and printed PASSED.

    So the levers are not patched one at a time. A statement is protected if any
    location in the file records it, the set is the union of those locations, and
    the pass that enforces it (`check_protected`) reads no id, no tier, no group
    and no release. Union is what makes editing monotone: a rename, a retier, a
    regrouping, a collision or a deletion from one field removes the statement
    from at most one source, and the others still carry it.

    The limit, stated exactly: a statement deleted from *every* location that
    records it is gone. The gate holds no copy of the ban list that the judged
    run did not write, so twelve instincts and a user exclusion cannot be
    recovered from an artefact that no longer mentions them. What union removes
    is the cheap edit - the one that keeps the file looking like a ban list.
    """
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for label, items in (("a first instinct burnt in stage 1", dump),
                         ("the user's own exclusion", extra)):
        for text in items:
            body = text.strip()
            key = normalize(body)
            if not body or key in seen:
                continue
            seen.add(key)
            out.append({"phrase": body, "label": label})
    return out


def replay_banlist(banlist: dict[str, Any], draw: dict[str, Any],
                   decks: dict[str, Any]) -> tuple[list[str], list[str], dict[str, Any]]:
    """Recompute the ban list this run implies, and lint against that, not the file.

    The first version of this checked that expected *phrases* appeared somewhere
    in the supplied file and then linted with the supplied objects, which is a
    much weaker thing than it reads as. Presence of a string is not the contract:
    demoting one real instinct from `ban` to `warn` left its phrase present and
    let the draft print it verbatim, and twelve copies of `"zzzzzz"` with
    `manual_checks` emptied satisfied "the twelve instincts are still there".

    So the file is not consulted for what to enforce. The dump it claims to have
    been built from is read back out of it, banlist.py is run again over that
    dump and the bundled deck, and the result is what the markdown is linted
    against - severities, structural patterns and manual checks included. The
    supplied file may only *add*: entries it carries beyond the recomputed set
    are kept, because adding a ban cannot relax a verdict.

    The honest limit: this proves the file is internally consistent with a run of
    banlist.py, not that the dump was the model's genuine first instincts. Twelve
    distinct throwaway lines still recompute cleanly. What it removes is the free
    edit - a downgrade now has to be committed to before the work is written,
    where SKILL.md's regeneration protocol can see it.
    """
    failures: list[str] = []
    warnings: list[str] = []
    cliches = decks["cliches"]

    drawn_topic = str(draw["request"]["topic"])
    topic = text_of(banlist.get("topic"))
    if not topic:
        failures.append(
            "banlist.topic: missing - this is not a contract built by banlist.py for a run")
    elif normalize(canonical(topic)) != normalize(canonical(drawn_topic)):
        failures.append(
            f"banlist.topic: the ban list was built for {topic!r} but the hand was dealt for "
            f"{drawn_topic!r} - a ban list from another run bans another run's answers")

    allowed = banlist.get("allowed", [])
    if not isinstance(allowed, list) or any(not isinstance(i, str) for i in allowed):
        failures.append("banlist.allowed: must be the list of cliche ids released when the list was built")
        allowed = []
    known_ids = {p["id"] for p in cliches["phrases"]}
    unknown = sorted(set(allowed) - known_ids)
    if unknown:
        failures.append(f"banlist.allowed: releases id(s) that are not in the cliche deck: {', '.join(unknown)}")
    honoured = sorted(set(allowed) - set(unknown))
    if honoured:
        # Said out loud, not only in README.md. This gate reads the release and
        # enforces the phrase anyway - deliberately, because `allowed` sits in
        # the artefact under verification - and a user who wrote it is entitled
        # to hear that from the run rather than from a document.
        warnings.append(
            f"banlist.allowed releases {', '.join(honoured)} and this gate honours no release: those "
            "phrases are enforced here regardless. The release applies to cliche_lint.py while you "
            "draft. To drop a bundled phrase for good, fork references/decks/cliches.json")

    supplied_entries = [e for e in (banlist.get("entries") or []) if isinstance(e, dict)]
    # Through banlist.py's own parser, because that is what it did to the dump:
    # it drops stubs and placeholders and - the part that matters here - dedupes.
    # Twelve copies of one string are one instinct, not twelve.
    #
    # strip_bullets=False: these phrases have already been through parse_obvious
    # once, in the builder, and bullet stripping is not idempotent. Stripping
    # again turned a legitimate nested bullet into a different phrase, and the
    # gate then told the user to build the list with the tool that had built it.
    dump = parse_obvious("\n".join(recover_dump(banlist)), strip_bullets=False)
    extra = banlist.get("extra") or []
    if not isinstance(extra, list) or any(not isinstance(i, str) for i in extra):
        failures.append(
            "banlist.extra: must be the list of user prohibitions the list was built with")
        extra = []
    # The user's exclusions, as the union of the two places this file records
    # them: the `extra` field and the rows built from it. Reading the field alone
    # made deleting one line enough to discharge a prohibition the user stated -
    # the row stayed in the file, wearing its own id, and stopped being enforced.
    # Adding a phrase here can only ban more, never less, which is why the union
    # is safe to take off the artefact under verification at all.
    extra = list(extra)
    known_extra = {normalize(str(i)) for i in extra}
    for entry in supplied_entries:
        phrase = str(entry.get("phrase", "")).strip()
        if phrase and marks_user_prohibition(entry) and normalize(phrase) not in known_extra:
            known_extra.add(normalize(phrase))
            extra.append(phrase)
    try:
        expected = compose_banlist(
            topic=drawn_topic, obvious=dump, extra=extra,
            allow=set(allowed) - set(unknown), cliches=cliches)
    except EngineError as exc:
        # compose_banlist refuses a short dump for the same reason banlist.py
        # does, and parse_obvious dedupes, so twelve identical lines arrive here
        # as one and are refused rather than counted.
        failures.append(
            f"banlist: the contract for this run - the bundled cliche deck plus the instincts burnt "
            f"before writing - cannot be rebuilt from the {len(dump)} distinct first instincts this "
            f"file carries. Stage 1 is the subtraction this skill is named after: build the list "
            f"with banlist.py rather than by hand. {exc}")
        return failures, warnings, {
            "entries": [e for e in deck_entries(cliches) if e["tier"] in ("ban", "warn")] + supplied_entries,
            "patterns": list(cliches["structural_patterns"]),
            "manual_checks": [],
            "protected": protected_statements(dump, extra),
        }

    by_phrase = {normalize(str(e.get("phrase", ""))): e for e in supplied_entries}
    mismatched: list[str] = []
    missing: list[str] = []
    for want in expected["entries"]:
        got = by_phrase.get(normalize(want["phrase"]))
        if got is None:
            missing.append(want["phrase"])
        elif (got.get("tier"), got.get("group")) != (want["tier"], want["group"]):
            mismatched.append(
                f"{want['phrase']!r} is {got.get('tier')}/{got.get('group')} here and "
                f"{want['tier']}/{want['group']} in the list this run produces")
    if missing:
        failures.append(
            f"banlist.entries: missing {len(missing)} phrase(s) of the contract this run produces - the "
            f"bundled cliche deck plus the burnt instincts ({', '.join(missing[:3])}...). Build the "
            "list with banlist.py rather than by hand")
    if mismatched:
        failures.append(
            "banlist.entries: severities do not replay - " + "; ".join(mismatched[:3]) +
            ". A demoted entry is a released ban wearing the word 'ban list'")

    supplied_manual = {
        str(m.get("id")): str(m.get("statement", ""))
        for m in (banlist.get("manual_checks") or []) if isinstance(m, dict)
    }
    lost = [m for m in expected["manual_checks"] if supplied_manual.get(m["id"]) != m["statement"]]
    if lost:
        failures.append(
            f"banlist.manual_checks: {len(lost)} check(s) the recomputed contract carries are absent or "
            f"altered (first: {lost[0]['statement'][:60]!r}) - the long instincts are the ones grep "
            "cannot help with, so dropping them drops exactly the part that needs a person")

    supplied_patterns = [p for p in (banlist.get("structural_patterns") or []) if isinstance(p, dict)]
    by_id = {p.get("id"): p for p in supplied_patterns}
    for want in expected["structural_patterns"]:
        got = by_id.get(want["id"])
        if got is None:
            failures.append(
                f"banlist.structural_patterns: missing {want['id']} - these are what catch the "
                "pitch-shaped sentence, and a list without them lints for nothing")
        elif got.get("regex") != want["regex"] or got.get("tier") != want["tier"]:
            failures.append(
                f"banlist.structural_patterns: {want['id']} does not match the bundled pattern - a "
                "supplied rule carrying a reserved id is a rewritten rule, not an added one")

    reserved_ids = {p["id"] for p in expected["structural_patterns"]}
    # A pattern this file adds is refused, not dropped. Compiling it reopens the
    # denial of verdict - `(a+)+b$` against a line of a's does not finish, and a
    # gate with no verdict gets read as one that did not fail - but ignoring it in
    # silence is worse than the hang it replaced: `{"id": "mine", "regex":
    # "\\bcheese\\b"}` plus "it smells faintly of cheese" in the draft printed
    # PASSED, named nothing, and told a user who had written their own ban that
    # their draft was clean. A refusal rather than a warning because there is no
    # honest way to print a pass over a ban that was never applied, and because
    # the fix takes one line: put the pattern in a forked deck, where it is a
    # distribution decision and the gate will compile it like any other.
    unusable = [p for p in supplied_patterns if p.get("id") not in reserved_ids and p.get("regex")]
    for p in unusable:
        failures.append(
            f"banlist.structural_patterns: {str(p.get('id'))!r} is not a rule of the bundled deck, and "
            f"a regex supplied in this file is never compiled - one that does not finish would leave "
            f"this gate with no verdict at all. So {str(p.get('regex'))[:40]!r} was NOT applied to the "
            "draft and nothing here checked what it was written to catch. Move it into a forked "
            "references/decks/cliches.json, or delete it and hold the line by reading")

    # A row cannot claim to be part of the bundled deck unless it is. Without
    # this, the way to release a protected phrase was to erase every mark that
    # said what it was: retype its id as a deck id, its group and source as
    # `deck`, its tier as `warn`, and the phrase sat in the file as a rule that
    # the deck had supposedly always carried. The deck is on disk and cannot be
    # edited from here, so the claim is checkable, and the union above then has
    # nothing left to lose a mark to.
    deck_rows = {e["id"]: e for e in deck_entries(cliches)}
    for entry in supplied_entries:
        eid = str(entry.get("id"))
        row = deck_rows.get(eid)
        if row is None:
            if entry.get("source") == "deck" or entry.get("group") == "deck":
                failures.append(
                    f"banlist.entries: {eid!r} is filed as a bundled deck rule and the deck has no such "
                    f"rule. A row relabelled as the deck's is a row whose own provenance was erased")
        elif (normalize(str(entry.get("phrase", ""))) != normalize(row["phrase"])
              or entry.get("tier") != row["tier"]):
            failures.append(
                f"banlist.entries: {eid} carries a reserved deck id but not the deck's rule - the deck "
                f"says {row['phrase']!r}/{row['tier']} and this file says "
                f"{str(entry.get('phrase', ''))[:40]!r}/{entry.get('tier')}")

    # Prose, and the gate says so rather than leaving the impression it is
    # checked. banlist.py copies the deck's forbidden moves into the file for the
    # model to read; nothing machine-checks them, so a move added here is obeyed
    # by whoever reads it or by nobody. That is not a hole - no lint can check
    # "do not explain the strangeness away" - but it is a field a user can write
    # into and hear nothing back about, which is the same silence the pattern
    # above was refused for.
    deck_moves = list(cliches["moves"])
    supplied_moves = banlist.get("forbidden_moves")
    if isinstance(supplied_moves, list) and supplied_moves != deck_moves:
        added = [str(m) for m in supplied_moves if m not in deck_moves]
        dropped = [m for m in deck_moves if m not in supplied_moves]
        warnings.append(
            f"banlist.forbidden_moves differs from the bundled deck ({len(added)} added, "
            f"{len(dropped)} missing{': ' + added[0][:50] if added else ''}). This gate never reads "
            "that field - the moves are prose for the model to obey, and nothing here enforces them "
            "either way")

    counts = banlist.get("counts")
    declared = counts.get("obvious_supplied") if isinstance(counts, dict) else None
    if declared != expected["counts"]["obvious_supplied"]:
        failures.append(
            f"banlist.counts.obvious_supplied says {declared!r} but the file replays as "
            f"{expected['counts']['obvious_supplied']} - the count and the contents disagree, so one "
            "of them was edited")
    # The other three counts, for the same reason. They do not protect a phrase -
    # a number cannot restore a deleted line - but a deleted row leaves them
    # stale, so removing one is no longer a single edit.
    for key in ("matchable", "warn", "manual"):
        got = counts.get(key) if isinstance(counts, dict) else None
        if got != expected["counts"][key]:
            failures.append(
                f"banlist.counts.{key} says {got!r} but the file replays as "
                f"{expected['counts'][key]} - the count and the contents disagree, so one of them "
                "was edited")

    # What the markdown is actually linted against: the recomputed contract,
    # plus whatever the supplied file adds on top of it. Bundled patterns are
    # taken from the deck rather than from the file, so a supplied rule bearing a
    # reserved id cannot replace the rule it is named after.
    #
    # Recomputed with nothing released: `allowed` is read off the artefact under
    # verification, so it is allowed to explain why a deck phrase is absent from
    # the file (above) but not to decide what the gate enforces. Honouring it
    # here would let the run release its own bans at verdict time, which is the
    # objection that deleted --min-mean and --rubric.
    #
    # This behaviour is unchanged. What was wrong here was the comment: it said
    # SKILL.md recorded the gap, and SKILL.md did not mention --allow at all,
    # while banlist.py and cliche_lint.py both advertise the flag in --help and
    # cliche_lint.py honours it. A limit stated inaccurately is worse than one
    # stated plainly, and it was stated in a file no user reads. SKILL.md stage
    # 1 now documents it, and this comment no longer claims documentation that
    # has to be checked to be believed.
    #
    # `extra` is honoured, above and here, because it can only add bans. The
    # asymmetry is the point: a release read off the graded artefact relaxes the
    # verdict, an addition read off it cannot.
    enforced = compose_banlist(
        topic=drawn_topic, obvious=dump, extra=extra, allow=set(), cliches=cliches)
    effective_entries = list(enforced["entries"])
    known_phrases = {normalize(e["phrase"]) for e in effective_entries}
    effective_entries += [
        e for e in supplied_entries
        if normalize(str(e.get("phrase", ""))) not in known_phrases and e.get("phrase")
    ]
    # Only the bundled patterns are compiled. A supplied pattern used to be added
    # if its id was not reserved, on the reasoning that an added rule can only ban
    # more; what it can also do is not finish. `(a+)+b$` against a line of sixty
    # a's backtracks for longer than anyone waits, and a gate that never reaches a
    # verdict is one an impatient caller reads as "it did not fail". The deck is
    # the least author-controlled source of a regex available here, so it is the
    # only one. This costs the ability to add a project-specific pattern at
    # verdict time; add it to a forked deck instead, where it is a distribution
    # decision rather than a per-run one.
    effective_patterns = list(enforced["structural_patterns"])
    return failures, warnings, {
        "entries": effective_entries,
        "patterns": effective_patterns,
        "manual_checks": expected["manual_checks"],
        "protected": protected_statements(dump, extra),
    }


MANUAL_SHAPE = (
    'manual_checks_cleared is an object keyed by check id: '
    '{"obvious-01": "how the result avoids it, in a sentence or two", "obvious-02": "..."}. '
    'One entry per id below, each at least %d units of written answer.' % MIN_MANUAL_ANSWER
)


def check_banlist(candidate: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    """Manual entries used to be printed and then forgotten. Now they are answered.

    The checks come from the recomputed contract, not from the supplied file:
    emptying `manual_checks` used to empty this loop with it.

    A missing field is reported once with its shape, not once per check. The
    shape - an object keyed by `obvious-NN` - appeared in no instruction, so an
    honest first attempt used a list of {check, answer} objects and got twelve
    identical FAILs in a row. A fiction brief produces twelve of twelve manual
    checks, because a sentence-shaped instinct is always too long to match
    literally, so this was the normal outcome outside a product brief rather
    than an edge case. Saying the same thing twelve times does not make it
    twelve findings; saying it once, with the shape, is what the reader needs.
    Checks that are present but thin are still reported one by one, because
    those are twelve different problems.
    """
    failures: list[str] = []
    manual = contract.get("manual_checks")
    manual = manual if isinstance(manual, list) else []
    raw = candidate.get("manual_checks_cleared")
    cleared = raw if isinstance(raw, dict) else {}
    ided = [e for e in manual if isinstance(e, dict) and "id" in e]
    if len(ided) != len(manual):
        failures.append("banlist.manual_checks: an entry has no id")

    unanswered = [e for e in ided if not text_of(cleared.get(e["id"]))]
    if len(unanswered) > 1:
        listed = ", ".join(str(e["id"]) for e in unanswered)
        wrong_shape = "" if isinstance(raw, dict) else (
            f" The field is {type(raw).__name__ if raw is not None else 'absent'} here, not an object."
        )
        failures.append(
            f"manual_checks_cleared: {len(unanswered)} of {len(ided)} checks have no written "
            f"answer ({listed}). These are the instincts too long to phrase-match, so they are "
            f"answered here or not at all.{wrong_shape} {MANUAL_SHAPE}")
    for entry in ided:
        if entry in unanswered and len(unanswered) > 1:
            continue
        statement = str(entry.get("statement", ""))[:60]
        failures += check_text(
            f"manual_checks_cleared[{entry['id']}]", cleared.get(entry["id"]), MIN_MANUAL_ANSWER,
            f"say how the result avoids \"{statement}\" - a check that is only printed is not a check")
    return failures


def bound_blocks(markdown: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for match in BIND.finditer(markdown):
        out.setdefault(match.group(1), []).append(match.group(2))
    return out


def check_markdown(candidate: dict[str, Any], markdown: str, rubric: dict[str, Any],
                   contract: dict[str, Any], needs_path: bool) -> list[str]:
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

    # The contract is the one replay_banlist recomputed, so a trimmed, demoted or
    # rule-shadowed file cannot quietly shrink the lint to what its author chose
    # to leave in.
    for f in lint(markdown, contract["entries"], contract["patterns"], allow=set()):
        if f["tier"] != "ban":
            continue
        failures.append(
            f"markdown line {f['line']}: banned material '{f['match']}' [{f['id']}] - "
            "rewrite the thought, not the word")
    failures += check_protected(markdown, contract)
    return failures


def check_protected(markdown: str, contract: dict[str, Any]) -> list[str]:
    """The second pass, over content alone.

    Deliberately duplicates work the pass above already does, and deliberately
    knows nothing about how the file above filed any of it. This one takes the
    union of every location that records a burnt instinct or a user exclusion,
    forces every one of them to `ban`, and reads no id, no tier, no group and no
    release on the way. A statement that survives in one field of banlist.json
    therefore still fires from that field, however the other fields describing it
    were edited.

    The message names the statement rather than an id, because an id is one of
    the things an attacker edits: `[cyberpunk]` on a line that is really the
    user's own exclusion tells the reader nothing true.
    """
    failures: list[str] = []
    protected = contract.get("protected") or []
    entries = [{"id": f"protected-{i:02d}", "phrase": p["phrase"], "tier": "ban", "group": "protected"}
               for i, p in enumerate(protected, start=1)]
    labels = {e["id"]: p["label"] for e, p in zip(entries, protected)}
    statements = {e["id"]: p["phrase"] for e, p in zip(entries, protected)}
    for f in lint(markdown, entries, [], allow=set()):
        failures.append(
            f"markdown line {f['line']}: '{f['match']}' is {labels[f['id']]} - "
            f"\"{statements[f['id']][:60]}\" is enforced by its content, not by how banlist.json "
            "files it, so retiering, renaming or unfiling the row does not release it")
    return failures


# ---------------------------------------------------------------------------


def gate(candidate: dict[str, Any], draw: dict[str, Any], banlist: dict[str, Any],
         markdown: str, rubric: dict[str, Any], decks: dict[str, Any]) -> dict[str, Any]:
    failures = replay_draw(draw, decks)
    failures += bind_candidate_to_draw(candidate, draw)
    banlist_failures, banlist_warnings, contract = replay_banlist(banlist, draw, decks)
    failures += banlist_failures

    # The profile is read off the validated run. There is no --extremal and no
    # --grounded: a flag is a claim made at verdict time, by the same party the
    # verdict is about. The profile no longer sets a threshold - there is none -
    # but it still names how the run was dealt, and grounded still substitutes
    # an axis, so both are recorded.
    mode_ids = set(draw["request"]["mode_ids"])
    profile = "extremal" if "extremal" in mode_ids else "default"
    grounded = "grounded" in mode_ids
    anchor = int(draw["request"]["anchor"])
    # output-template.md requires the operational path at anchor 3 as well as in
    # grounded mode. The gate used to ask for it only in grounded, so anchor 3
    # could ship without the one thing that level is for.
    needs_path = grounded or anchor == 3

    cand_failures, warnings, values, mean = check_candidate(
        candidate, rubric, grounded, needs_path, affect="affect" in mode_ids)
    # Printed on both paths, pass and fail: everything the gate read off an
    # artefact and did not act on is said out loud, so no user is left believing
    # a rule they wrote was applied.
    warnings = banlist_warnings + warnings
    failures += cand_failures
    failures += check_banlist(candidate, contract)
    failures += check_markdown(candidate, markdown, rubric, contract, needs_path)

    substitution = rubric.get("grounded_substitution", {})
    return {
        "engine_version": VERSION,
        "passed": not failures,
        # Recorded, not compared. `establishes` says what a pass means, in the
        # verdict itself, so a reader of the JSON cannot take it for more.
        "mean": mean,
        "establishes": ("the required work is present and the four artefacts are bound to each "
                        "other; not that the result is good"),
        "policy": {
            "rubric": rubric.get("rubric", "imagination-engine"),
            "rubric_version": rubric.get("version"),
            "rubric_sha256": rubric["_sha256"],
            "profile": profile,
            "score_threshold": None,
            "anchor": anchor,
            "modes": sorted(mode_ids),
            "axis_substitution": substitution.get("axis", {}).get("id") if grounded else None,
            "axis_substitution_replaces": substitution.get("replaces") if grounded else None,
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
        profile_label = policy["profile"]
        if policy["axis_substitution"]:
            profile_label += (
                f" ({policy['axis_substitution']} substituted for "
                f"{policy['axis_substitution_replaces']})")
        print(f"POLICY LOCKED: {policy['rubric']}/{policy['rubric_version']} {profile_label}; "
              "all eight axes required and argued; no score threshold")
        print(f"mean {verdict['mean']} - recorded, not a pass mark")
        for w in verdict["warnings"]:
            print(f"WARN  {w}")
        for f in verdict["failures"]:
            print(f"FAIL  {f}")
        print("PASSED - the required work is present and the four artefacts are bound to each "
              "other. This is not a judgement that the result is good; read it yourself."
              if verdict["passed"]
              else "GATE FAILED - do not show this to the user; fix or regenerate.")
    return 0 if verdict["passed"] else GATE_FAIL


if __name__ == "__main__":
    raise SystemExit(main())
