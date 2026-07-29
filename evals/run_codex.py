#!/usr/bin/env python3
"""Run reproducible Codex generation and blind-judge calls for the A/B harness."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import subprocess
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Iterable


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
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
                raise ValueError(f"{path}:{line_number}: row must be an object")
            rows.append(row)
    return rows


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def render(template: str, brief: str) -> str:
    if "{{BRIEF}}" not in template:
        raise ValueError("prompt template must contain {{BRIEF}}")
    return template.replace("{{BRIEF}}", brief)


def run_codex(
    prompt: str,
    *,
    model: str,
    reasoning: str,
    timeout: int,
    output_schema: Path | None = None,
) -> tuple[str, dict[str, int], float]:
    command = [
        "codex",
        "exec",
        "--ignore-user-config",
        "--ignore-rules",
        "--ephemeral",
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        "--model",
        model,
        "-c",
        f'model_reasoning_effort="{reasoning}"',
        "--json",
    ]
    if output_schema is not None:
        command.extend(["--output-schema", str(output_schema.resolve())])
    command.append("-")

    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="imagination-eval-") as clean_dir:
        command[2:2] = ["--cd", clean_dir]
        result = subprocess.run(
            command,
            input=prompt,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    elapsed = time.monotonic() - started
    if result.returncode:
        raise RuntimeError(
            f"codex exited {result.returncode}: {result.stderr[-2000:]}"
        )

    message = ""
    usage: dict[str, int] = {}
    for raw in result.stdout.splitlines():
        try:
            event = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "item.completed":
            item = event.get("item", {})
            if item.get("type") == "agent_message":
                message = str(item.get("text", "")).strip()
        elif event.get("type") == "turn.completed":
            raw_usage = event.get("usage", {})
            usage = {
                key: int(value)
                for key, value in raw_usage.items()
                if isinstance(value, (int, float))
            }
    if not message:
        raise RuntimeError(f"codex returned no final message: {result.stdout[-2000:]}")
    return message, usage, elapsed


def generation_prompt(task: str, skill: str | None) -> str:
    clean_room = (
        "Do not use tools, browse, inspect files, discuss the evaluation, or reveal "
        "private reasoning. Return only the requested user-facing result.\n\n"
    )
    if skill is None:
        return clean_room + task
    return (
        clean_room
        + "Apply the following skill instructions faithfully while solving the task.\n\n"
        + "<skill>\n"
        + skill.strip()
        + "\n</skill>\n\n"
        + task
    )


def generate(args: argparse.Namespace) -> int:
    briefs = read_jsonl(args.briefs)
    control_template = args.control_prompt.read_text(encoding="utf-8")
    treatment_template = args.treatment_prompt.read_text(encoding="utf-8")
    skill = args.skill.read_text(encoding="utf-8")
    existing = read_jsonl(args.output)
    by_key = {
        (row.get("brief_id"), row.get("condition"), row.get("run")): row
        for row in existing
    }
    conditions = tuple(
        condition.strip()
        for condition in args.conditions.split(",")
        if condition.strip()
    )
    if not conditions or set(conditions) - {"control", "treatment"}:
        raise ValueError("--conditions must contain control and/or treatment")

    jobs: list[tuple[dict[str, Any], str, int]] = []
    for brief in briefs:
        for run in range(1, args.runs + 1):
            for condition in conditions:
                key = (brief["id"], condition, run)
                if key not in by_key:
                    jobs.append((brief, condition, run))

    lock = threading.Lock()
    completed = 0

    def one(job: tuple[dict[str, Any], str, int]) -> dict[str, Any]:
        nonlocal completed
        brief, condition, run = job
        template = control_template if condition == "control" else treatment_template
        task = render(template, brief["prompt"])
        prompt = generation_prompt(task, None if condition == "control" else skill)
        message, usage, elapsed = run_codex(
            prompt,
            model=args.model,
            reasoning=args.reasoning,
            timeout=args.timeout,
        )
        row = {
            "brief_id": brief["id"],
            "condition": condition,
            "run": run,
            "text": message,
            "model": args.model,
            "reasoning": args.reasoning,
            "wall_seconds": round(elapsed, 4),
            **usage,
        }
        if "input_tokens" in usage and "output_tokens" in usage:
            row["total_tokens"] = usage["input_tokens"] + usage["output_tokens"]
        with lock:
            completed += 1
            print(f"[{completed}/{len(jobs)}] {brief['id']} {condition} run={run}")
        return row

    errors: list[str] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(one, job) for job in jobs]
        for future in concurrent.futures.as_completed(futures):
            try:
                row = future.result()
            except Exception as exc:  # Preserve every other completed sample.
                errors.append(repr(exc))
                print(f"[error] {exc}")
                continue
            by_key[(row["brief_id"], row["condition"], row["run"])] = row
            write_jsonl(
                args.output,
                sorted(
                    by_key.values(),
                    key=lambda item: (
                        str(item.get("brief_id")),
                        int(item.get("run", 0)),
                        str(item.get("condition")),
                    ),
                ),
            )
    if errors:
        raise RuntimeError(
            f"{len(errors)} generation call(s) failed; rerun to fill missing rows"
        )
    return 0


def judge_schema(metrics: list[str]) -> dict[str, Any]:
    side = {
        "type": "object",
        "properties": {
            metric: {"type": "integer", "minimum": 1, "maximum": 7}
            for metric in metrics
        },
        "required": metrics,
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {
            "ratings": {
                "type": "object",
                "properties": {"left": side, "right": side},
                "required": ["left", "right"],
                "additionalProperties": False,
            },
            "want": {"type": "string", "enum": ["left", "right", "tie"]},
        },
        "required": ["ratings", "want"],
        "additionalProperties": False,
    }


def judge(args: argparse.Namespace) -> int:
    packet = read_jsonl(args.packet)
    judge_instructions = args.judge_prompt.read_text(encoding="utf-8")
    metrics = [part.strip() for part in args.metrics.split(",") if part.strip()]
    if not metrics:
        raise ValueError("--metrics must not be empty")
    existing = read_jsonl(args.votes)
    by_key = {
        (row.get("comparison_id"), row.get("judge_id")): row for row in existing
    }
    judge_ids = [
        f"{args.judge_prefix}-{number}" for number in range(1, args.judges + 1)
    ]
    jobs = [
        (item, judge_id)
        for item in packet
        for judge_id in judge_ids
        if (item["comparison_id"], judge_id) not in by_key
    ]

    args.schema.parent.mkdir(parents=True, exist_ok=True)
    args.schema.write_text(
        json.dumps(judge_schema(metrics), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    lock = threading.Lock()
    completed = 0

    def one(job: tuple[dict[str, Any], str]) -> dict[str, Any]:
        nonlocal completed
        item, judge_id = job
        prompt = (
            "Do not use tools, browse, inspect files, or infer the generating "
            "condition. Judge only the delivered texts. Return only JSON matching "
            "the supplied schema.\n\n"
            + judge_instructions.strip()
            + "\n\nBRIEF:\n"
            + item["brief"]
            + "\n\nLEFT:\n"
            + item["left"]
            + "\n\nRIGHT:\n"
            + item["right"]
        )
        message, usage, elapsed = run_codex(
            prompt,
            model=args.model,
            reasoning=args.reasoning,
            timeout=args.timeout,
            output_schema=args.schema,
        )
        verdict = json.loads(message)
        row = {
            "comparison_id": item["comparison_id"],
            "judge_id": judge_id,
            "ratings": verdict["ratings"],
            "want": verdict["want"],
            "judge_model": args.model,
            "judge_reasoning": args.reasoning,
            "judge_wall_seconds": round(elapsed, 4),
            "judge_usage": usage,
        }
        with lock:
            completed += 1
            print(f"[{completed}/{len(jobs)}] {item['brief_id']} {judge_id}")
        return row

    errors: list[str] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(one, job) for job in jobs]
        for future in concurrent.futures.as_completed(futures):
            try:
                row = future.result()
            except Exception as exc:  # Preserve every other completed verdict.
                errors.append(repr(exc))
                print(f"[error] {exc}")
                continue
            by_key[(row["comparison_id"], row["judge_id"])] = row
            write_jsonl(
                args.votes,
                sorted(
                    by_key.values(),
                    key=lambda item: (
                        str(item.get("comparison_id")),
                        str(item.get("judge_id")),
                    ),
                ),
            )
    if errors:
        raise RuntimeError(
            f"{len(errors)} judge call(s) failed; rerun to fill missing rows"
        )
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    generation = commands.add_parser("generate")
    generation.add_argument("--briefs", type=Path, required=True)
    generation.add_argument("--control-prompt", type=Path, required=True)
    generation.add_argument("--treatment-prompt", type=Path, required=True)
    generation.add_argument("--skill", type=Path, required=True)
    generation.add_argument("--output", type=Path, required=True)
    generation.add_argument("--runs", type=int, default=1)
    generation.add_argument("--conditions", default="control,treatment")
    generation.add_argument("--model", default="gpt-5.4")
    generation.add_argument("--reasoning", default="medium")
    generation.add_argument("--workers", type=int, default=4)
    generation.add_argument("--timeout", type=int, default=300)
    generation.set_defaults(handler=generate)

    judging = commands.add_parser("judge")
    judging.add_argument("--packet", type=Path, required=True)
    judging.add_argument("--judge-prompt", type=Path, required=True)
    judging.add_argument("--metrics", required=True)
    judging.add_argument("--votes", type=Path, required=True)
    judging.add_argument("--schema", type=Path, required=True)
    judging.add_argument("--judges", type=int, default=3)
    judging.add_argument("--judge-prefix", default="ai-judge")
    judging.add_argument("--model", default="gpt-5.4")
    judging.add_argument("--reasoning", default="medium")
    judging.add_argument("--workers", type=int, default=4)
    judging.add_argument("--timeout", type=int, default=300)
    judging.set_defaults(handler=judge)
    return root


def main() -> int:
    args = parser().parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
