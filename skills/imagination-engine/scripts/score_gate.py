#!/usr/bin/env python3
"""score_gate.py - fail-closed gate between a candidate and the user.

Validates the candidate JSON: every required section present and substantive,
the broken law replaced by something that forbids something, each drawn domain
actually answering its probe, the nearest known works named honestly, and all
eight rubric axes scored with a written justification.

The gate cannot tell whether an idea is good. It can tell whether the work that
makes an idea good was skipped, which is the failure this skill is built around.

Usage:
  score_gate.py --candidate ./work/candidate.json
  score_gate.py --candidate ./work/candidate.json --extremal

Exit codes: 0 pass, 1 usage or parse error, 2 gate failed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from engine import VERSION, EngineError, SKILL_DIR, die, is_placeholder, text_units  # type: ignore
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from engine import VERSION, EngineError, SKILL_DIR, die, is_placeholder, text_units  # type: ignore

GATE_FAIL = 2
MIN_JUSTIFICATION = 40
MIN_PROBE_ANSWER = 30
MIN_DIFFERENCE = 40
MIN_IMPOSSIBLE = 30
MIN_FIX = 40
MIN_DOMAINS = 3


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Gate a candidate against the imagination-engine rubric.")
    p.add_argument("--candidate", required=True, help="candidate.json (see references/candidate.schema.json)")
    p.add_argument("--extremal", action="store_true", help="apply extremal thresholds (mean 9.0, no axis below 8)")
    p.add_argument("--grounded", action="store_true",
                   help="grounded mode: score translation_integrity in place of non_anthropocentrism, "
                        "and require the operational_path section. The candidate must declare "
                        "'grounded' in its own modes, and must not also declare 'nonhuman'")
    p.add_argument("--min-mean", type=float, default=None, help="override the mean threshold")
    p.add_argument("--min-axis", type=int, default=None, help="override the per-axis floor")
    p.add_argument("--rubric", default=None, help="path to an alternative rubric.json")
    p.add_argument("--json", action="store_true", help="emit the verdict as JSON")
    return p


def load_rubric(path: str | None) -> dict[str, Any]:
    target = Path(path) if path else SKILL_DIR / "references" / "rubric.json"
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EngineError(f"cannot read rubric {target}: {exc}") from exc
    if "axes" not in data or "required_sections" not in data:
        raise EngineError(f"rubric {target} is missing 'axes' or 'required_sections'")
    return data


def text_of(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def section_minimum(spec: dict[str, Any]) -> int:
    """Rubrics written before units existed still say min_chars."""
    return int(spec.get("min_units", spec.get("min_chars", 0)))


def check(candidate: dict[str, Any], rubric: dict[str, Any], min_mean: float, min_axis: int,
          grounded: bool = False) -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []
    substitution = rubric.get("grounded_substitution", {})
    grounded_section = substitution.get("requires_section")

    sections = candidate.get("sections")
    if not isinstance(sections, dict):
        failures.append("sections: missing or not an object")
        sections = {}
    for spec in rubric["required_sections"]:
        if spec["id"] == grounded_section and not grounded:
            continue
        body = text_of(sections.get(spec["id"]))
        if not body:
            failures.append(f"sections.{spec['id']}: missing - {spec['note']}")
        elif spec["id"] == "name":
            # A name is an identifier, not prose. Asking it to be N characters
            # long rejects a complete two-character name and accepts "TBD".
            if is_placeholder(body):
                failures.append(f"sections.name: '{body}' is a placeholder, not a name - {spec['note']}")
        elif text_units(body) < section_minimum(spec):
            failures.append(
                f"sections.{spec['id']}: {text_units(body)} units, needs {section_minimum(spec)} - {spec['note']}"
            )

    broken = candidate.get("broken_rule")
    if not isinstance(broken, dict):
        failures.append("broken_rule: missing - state which law was deleted and what replaced it")
    else:
        if not text_of(broken.get("constraint_id")):
            failures.append("broken_rule.constraint_id: missing - name the drawn constraint you broke")
        if text_units(text_of(broken.get("new_law"))) < MIN_IMPOSSIBLE:
            failures.append(f"broken_rule.new_law: needs at least {MIN_IMPOSSIBLE} units")
        impossible = text_of(broken.get("now_impossible"))
        if text_units(impossible) < MIN_IMPOSSIBLE:
            failures.append(
                f"broken_rule.now_impossible: needs at least {MIN_IMPOSSIBLE} units - a world where "
                "the rule is merely gone is empty, not strange"
            )

    domains = candidate.get("domains_used")
    if not isinstance(domains, list) or len(domains) < MIN_DOMAINS:
        failures.append(f"domains_used: needs at least {MIN_DOMAINS} entries drawn by draw.py")
    else:
        ids = []
        for i, d in enumerate(domains):
            if not isinstance(d, dict):
                failures.append(f"domains_used[{i}]: not an object")
                continue
            did = text_of(d.get("id"))
            ids.append(did)
            if not did:
                failures.append(f"domains_used[{i}].id: missing")
            if text_units(text_of(d.get("answer_to_probe"))) < MIN_PROBE_ANSWER:
                failures.append(
                    f"domains_used[{i}] ({did or '?'}).answer_to_probe: too thin - a domain that answers "
                    "nothing is a decoration; cut it or make it load-bearing"
                )
        if len(set(ids)) != len(ids):
            failures.append("domains_used: duplicate domain ids")

    resembles = candidate.get("resembles")
    if not isinstance(resembles, list) or not resembles:
        failures.append(
            "resembles: missing - name the nearest known works you checked against, or state "
            "explicitly what you searched and found nothing close to"
        )
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
            f"weakest_fix: needs at least {MIN_FIX} units - name the weakest axis and what a rewrite would change"
        )

    axis_ids = [a["id"] for a in rubric["axes"]]
    if grounded and substitution:
        # Substitution, not exemption: the axis a result built for someone
        # cannot satisfy is replaced by the one it must.
        #
        # The flag alone is not evidence. Unchecked, --grounded is a way to
        # delete any axis you are about to score badly, and the axis it deletes
        # is the one nonhuman mode exists to enforce - so a candidate that
        # claims nonhuman may not use it, and a candidate that does not claim
        # grounded may not either.
        declared = candidate.get("modes")
        declared = [m for m in declared if isinstance(m, str)] if isinstance(declared, list) else []
        if "grounded" not in declared:
            failures.append(
                "--grounded was passed but the candidate does not declare grounded in its own modes - "
                "the flag is not evidence, the run is. Re-run draw.py with --modes grounded, or drop the flag"
            )
        elif "nonhuman" in declared:
            failures.append(
                f"modes {', '.join(declared)}: grounded cannot substitute for {substitution['replaces']} "
                "in a run that also claims nonhuman - that axis is the one nonhuman mode exists to enforce. "
                "Drop one of the two modes and regenerate"
            )
        else:
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
            justification = text_of(entry.get("justification"))
            if text_units(justification) < MIN_JUSTIFICATION:
                failures.append(
                    f"scores.{axis}.justification: needs at least {MIN_JUSTIFICATION} units of argument"
                )

    mean = round(sum(values.values()) / len(values), 2) if values else 0.0
    if values and len(values) == len(axis_ids):
        if mean < min_mean:
            failures.append(f"mean {mean} is below the {min_mean} threshold - regenerate rather than resubmit")
        low = sorted((a for a in values if values[a] < min_axis), key=lambda a: values[a])
        if low:
            failures.append(
                "axes below the floor of "
                f"{min_axis}: " + ", ".join(f"{a}={values[a]}" for a in low)
            )
        if len(set(values.values())) == 1:
            warnings.append("every axis has the same score, which usually means the rubric was filled in, not applied")
        if min(values.values()) >= 9:
            warnings.append("no axis below 9: self-scoring this generous is itself a signal - recheck the weakest part")

    return {
        "engine_version": VERSION,
        "passed": not failures,
        "mean": mean,
        "thresholds": {"min_mean": min_mean, "min_axis": min_axis},
        "grounded": grounded,
        "scores": values,
        "failures": failures,
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        rubric = load_rubric(args.rubric)
        try:
            candidate = json.loads(Path(args.candidate).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise EngineError(f"cannot read candidate {args.candidate}: {exc}") from exc
        if not isinstance(candidate, dict):
            raise EngineError("candidate must be a JSON object")
        defaults = rubric["extremal_thresholds"] if args.extremal else rubric["default_thresholds"]
        min_mean = args.min_mean if args.min_mean is not None else float(defaults["min_mean"])
        min_axis = args.min_axis if args.min_axis is not None else int(defaults["min_axis"])
        verdict = check(candidate, rubric, min_mean, min_axis, grounded=args.grounded)
    except EngineError as exc:
        die(str(exc), 1)
        return 1

    if args.json:
        print(json.dumps(verdict, ensure_ascii=False, indent=2))
    else:
        print(f"mean {verdict['mean']} (threshold {min_mean}, axis floor {min_axis})")
        for w in verdict["warnings"]:
            print(f"WARN  {w}")
        for f in verdict["failures"]:
            print(f"FAIL  {f}")
        print("PASSED - the required work is present." if verdict["passed"]
              else "GATE FAILED - do not show this to the user; fix or regenerate.")
    return 0 if verdict["passed"] else GATE_FAIL


if __name__ == "__main__":
    raise SystemExit(main())
