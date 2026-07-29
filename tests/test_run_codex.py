from __future__ import annotations

import importlib.util
from pathlib import Path


RUNNER_PATH = Path(__file__).parents[1] / "evals" / "run_codex.py"
SPEC = importlib.util.spec_from_file_location("run_codex", RUNNER_PATH)
assert SPEC and SPEC.loader
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


def test_render_replaces_brief() -> None:
    assert RUNNER.render("Before {{BRIEF}} after", "the task") == (
        "Before the task after"
    )


def test_treatment_prompt_contains_skill_but_control_does_not() -> None:
    control = RUNNER.generation_prompt("TASK", None)
    treatment = RUNNER.generation_prompt("TASK", "SKILL RULE")

    assert "SKILL RULE" not in control
    assert "<skill>\nSKILL RULE\n</skill>" in treatment
    assert "TASK" in control and "TASK" in treatment


def test_generation_prompt_can_inject_a_baseline_skill() -> None:
    baseline = RUNNER.generation_prompt("TASK", "BASELINE SKILL")

    assert "<skill>\nBASELINE SKILL\n</skill>" in baseline
    assert "TASK" in baseline


def test_judge_schema_requires_all_metrics() -> None:
    metrics = ["fit", "craft"]
    schema = RUNNER.judge_schema(metrics)
    ratings = schema["properties"]["ratings"]

    assert ratings["required"] == ["left", "right"]
    assert ratings["properties"]["left"]["required"] == metrics
    assert schema["properties"]["want"]["enum"] == ["left", "right", "tie"]
