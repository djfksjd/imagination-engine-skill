#!/usr/bin/env python3
"""Build blind comparison packets and score paired creativity evaluations."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


METRICS = ("fit", "useful_surprise", "set_diversity", "craft")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            line = raw.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number}: each row must be an object")
            rows.append(row)
    return rows


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def require_text(row: dict[str, Any], field: str, source: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{source}: {field!r} must be non-empty text")
    return value.strip()


def require_run(row: dict[str, Any], source: str) -> int:
    value = row.get("run")
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ValueError(f"{source}: 'run' must be a positive integer")
    return value


def stable_bit(seed: str, *parts: object) -> int:
    material = "|".join([seed, *(str(part) for part in parts)])
    return hashlib.sha256(material.encode("utf-8")).digest()[0] & 1


def comparison_id(seed: str, brief_id: str, run: int) -> str:
    material = f"{seed}|{brief_id}|{run}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()[:16]


def build_packet(args: argparse.Namespace) -> int:
    conditions = [part.strip() for part in args.conditions.split(",") if part.strip()]
    if len(conditions) != 2 or len(set(conditions)) != 2:
        raise ValueError("--conditions must name exactly two distinct conditions")

    briefs: dict[str, dict[str, Any]] = {}
    for row in read_jsonl(args.briefs):
        brief_id = require_text(row, "id", str(args.briefs))
        require_text(row, "prompt", f"{args.briefs}:{brief_id}")
        if brief_id in briefs:
            raise ValueError(f"{args.briefs}: duplicate brief id {brief_id!r}")
        briefs[brief_id] = row

    outputs: dict[tuple[str, int, str], dict[str, Any]] = {}
    runs_by_brief: dict[str, set[int]] = defaultdict(set)
    for index, row in enumerate(read_jsonl(args.outputs), 1):
        source = f"{args.outputs}:row {index}"
        brief_id = require_text(row, "brief_id", source)
        condition = require_text(row, "condition", source)
        run = require_run(row, source)
        require_text(row, "text", source)
        if brief_id not in briefs:
            raise ValueError(f"{source}: unknown brief_id {brief_id!r}")
        if condition not in conditions:
            continue
        key = (brief_id, run, condition)
        if key in outputs:
            raise ValueError(f"{source}: duplicate output {key!r}")
        outputs[key] = row
        runs_by_brief[brief_id].add(run)

    packet: list[dict[str, Any]] = []
    answer_key: list[dict[str, Any]] = []
    for brief_id in briefs:
        if args.expected_runs:
            expected = set(range(1, args.expected_runs + 1))
            actual = runs_by_brief.get(brief_id, set())
            if actual != expected:
                raise ValueError(
                    f"{brief_id!r}: expected runs {sorted(expected)}, got "
                    f"{sorted(actual)}"
                )
        for run in sorted(runs_by_brief.get(brief_id, set())):
            pair = [(brief_id, run, condition) for condition in conditions]
            missing = [key for key in pair if key not in outputs]
            if missing:
                raise ValueError(f"missing paired outputs: {missing!r}")

            left_condition, right_condition = conditions
            if stable_bit(args.seed, brief_id, run):
                left_condition, right_condition = right_condition, left_condition

            item_id = comparison_id(args.seed, brief_id, run)
            packet.append(
                {
                    "comparison_id": item_id,
                    "brief_id": brief_id,
                    "brief": briefs[brief_id]["prompt"],
                    "left": outputs[(brief_id, run, left_condition)]["text"],
                    "right": outputs[(brief_id, run, right_condition)]["text"],
                }
            )
            answer_key.append(
                {
                    "comparison_id": item_id,
                    "brief_id": brief_id,
                    "run": run,
                    "left_condition": left_condition,
                    "right_condition": right_condition,
                }
            )

    if not packet:
        raise ValueError("no paired comparisons were produced")
    write_jsonl(args.packet, packet)
    write_jsonl(args.key, answer_key)
    return 0


def rating(value: Any, source: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{source}: rating must be numeric")
    number = float(value)
    if not 1 <= number <= 7:
        raise ValueError(f"{source}: rating must be between 1 and 7")
    return number


def mean(values: list[float]) -> float | None:
    return statistics.fmean(values) if values else None


def wilson_interval(wins: int, total: int, z: float = 1.96) -> tuple[float, float] | None:
    if total == 0:
        return None
    proportion = wins / total
    denominator = 1 + z * z / total
    center = (proportion + z * z / (2 * total)) / denominator
    margin = (
        z
        * math.sqrt(
            proportion * (1 - proportion) / total + z * z / (4 * total * total)
        )
        / denominator
    )
    return center - margin, center + margin


def summarize_costs(outputs_path: Path | None) -> dict[str, Any]:
    if outputs_path is None:
        return {}
    by_condition: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for index, row in enumerate(read_jsonl(outputs_path), 1):
        condition = require_text(row, "condition", f"{outputs_path}:row {index}")
        if isinstance(row.get("total_tokens"), (int, float)):
            by_condition[condition]["total_tokens"].append(float(row["total_tokens"]))
        elif isinstance(row.get("input_tokens"), (int, float)) and isinstance(
            row.get("output_tokens"), (int, float)
        ):
            by_condition[condition]["total_tokens"].append(
                float(row["input_tokens"]) + float(row["output_tokens"])
            )
        if isinstance(row.get("wall_seconds"), (int, float)):
            by_condition[condition]["wall_seconds"].append(float(row["wall_seconds"]))

    return {
        condition: {
            metric: round(statistics.fmean(values), 4)
            for metric, values in metrics.items()
            if values
        }
        for condition, metrics in by_condition.items()
    }


def score(args: argparse.Namespace) -> int:
    keys = {
        require_text(row, "comparison_id", str(args.key)): row
        for row in read_jsonl(args.key)
    }
    if not keys:
        raise ValueError("answer key is empty")

    per_brief: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: {metric: [] for metric in METRICS}
    )
    want_balance: dict[tuple[str, str], int] = defaultdict(int)
    seen_votes: set[tuple[str, str]] = set()
    judges_by_comparison: dict[str, set[str]] = defaultdict(set)

    for index, row in enumerate(read_jsonl(args.votes), 1):
        source = f"{args.votes}:row {index}"
        item_id = require_text(row, "comparison_id", source)
        judge_id = require_text(row, "judge_id", source)
        if item_id not in keys:
            raise ValueError(f"{source}: unknown comparison_id {item_id!r}")
        vote_key = (item_id, judge_id)
        if vote_key in seen_votes:
            raise ValueError(f"{source}: duplicate vote from judge on comparison")
        seen_votes.add(vote_key)
        judges_by_comparison[item_id].add(judge_id)

        key = keys[item_id]
        sides = {
            key["left_condition"]: "left",
            key["right_condition"]: "right",
        }
        if args.control not in sides or args.treatment not in sides:
            raise ValueError(
                f"{source}: key does not contain control={args.control!r} and "
                f"treatment={args.treatment!r}"
            )
        ratings = row.get("ratings")
        if not isinstance(ratings, dict):
            raise ValueError(f"{source}: ratings must be an object")
        brief_id = require_text(key, "brief_id", source)

        for metric in METRICS:
            treatment_side = sides[args.treatment]
            control_side = sides[args.control]
            try:
                treatment_value = rating(
                    ratings[treatment_side][metric],
                    f"{source}:ratings.{treatment_side}.{metric}",
                )
                control_value = rating(
                    ratings[control_side][metric],
                    f"{source}:ratings.{control_side}.{metric}",
                )
            except (KeyError, TypeError) as exc:
                raise ValueError(f"{source}: missing rating for {metric!r}") from exc
            delta = treatment_value - control_value
            per_brief[brief_id][metric].append(delta)

        want = require_text(row, "want", source).lower()
        cell = (brief_id, judge_id)
        want_balance[cell] += 0
        if want == "tie":
            continue
        if want not in {"left", "right"}:
            raise ValueError(f"{source}: want must be left, right, or tie")
        if sides[args.treatment] == want:
            want_balance[cell] += 1
        else:
            want_balance[cell] -= 1

    if not seen_votes:
        raise ValueError("votes file is empty")
    if args.expected_judges:
        comparisons_by_brief: dict[str, list[str]] = defaultdict(list)
        for item_id, key in keys.items():
            comparisons_by_brief[require_text(key, "brief_id", str(args.key))].append(
                item_id
            )
        for brief_id, item_ids in comparisons_by_brief.items():
            judge_sets = [judges_by_comparison.get(item_id, set()) for item_id in item_ids]
            for item_id, judge_set in zip(item_ids, judge_sets):
                if len(judge_set) != args.expected_judges:
                    raise ValueError(
                        f"{item_id!r}: expected {args.expected_judges} judges, "
                        f"got {len(judge_set)}"
                    )
            if any(judge_set != judge_sets[0] for judge_set in judge_sets[1:]):
                raise ValueError(
                    f"{brief_id!r}: the same judges must rate every run so WANT "
                    "can be collapsed by brief × judge"
                )

    treatment_wins = sum(balance > 0 for balance in want_balance.values())
    control_wins = sum(balance < 0 for balance in want_balance.values())
    ties = sum(balance == 0 for balance in want_balance.values())
    decisive = treatment_wins + control_wins
    interval = wilson_interval(treatment_wins, decisive)
    pooled_differences = {
        metric: [
            mean(metric_values[metric])
            for metric_values in per_brief.values()
            if metric_values[metric]
        ]
        for metric in METRICS
    }
    report: dict[str, Any] = {
        "conditions": {"control": args.control, "treatment": args.treatment},
        "votes": {
            "raw_vote_rows": len(seen_votes),
            "brief_judge_cells": len(want_balance),
            "treatment_wins": treatment_wins,
            "control_wins": control_wins,
            "ties": ties,
            "treatment_win_rate_excluding_ties": (
                round(treatment_wins / decisive, 4) if decisive else None
            ),
            "wilson_95": [round(value, 4) for value in interval] if interval else None,
        },
        "mean_treatment_minus_control": {
            metric: round(mean(values), 4)
            for metric, values in pooled_differences.items()
        },
        "per_brief_mean_differences": {
            brief_id: {
                metric: round(mean(values), 4)
                for metric, values in metric_values.items()
            }
            for brief_id, metric_values in sorted(per_brief.items())
        },
        "per_brief_median_differences": {
            brief_id: {
                metric: round(statistics.median(values), 4)
                for metric, values in metric_values.items()
            }
            for brief_id, metric_values in sorted(per_brief.items())
        },
        "mean_costs": summarize_costs(args.outputs),
    }

    serialized = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(serialized + "\n", encoding="utf-8")
    else:
        print(serialized)
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    packet = commands.add_parser("packet", help="build a blind paired packet")
    packet.add_argument("--briefs", type=Path, required=True)
    packet.add_argument("--outputs", type=Path, required=True)
    packet.add_argument("--packet", type=Path, required=True)
    packet.add_argument("--key", type=Path, required=True)
    packet.add_argument("--conditions", default="control,treatment")
    packet.add_argument("--seed", required=True)
    packet.add_argument("--expected-runs", type=int, default=0)
    packet.set_defaults(func=build_packet)

    score_command = commands.add_parser("score", help="score blind judge votes")
    score_command.add_argument("--votes", type=Path, required=True)
    score_command.add_argument("--key", type=Path, required=True)
    score_command.add_argument("--outputs", type=Path)
    score_command.add_argument("--report", type=Path)
    score_command.add_argument("--control", default="control")
    score_command.add_argument("--treatment", default="treatment")
    score_command.add_argument("--expected-judges", type=int, default=0)
    score_command.set_defaults(func=score)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        return args.func(args)
    except ValueError as exc:
        raise SystemExit(f"error: {exc}") from exc


if __name__ == "__main__":
    raise SystemExit(main())
