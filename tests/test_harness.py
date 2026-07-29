import json
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
HARNESS = REPO / "evals" / "harness.py"


def write_jsonl(path, rows):
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def read_jsonl(path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_packet_is_paired_blind_and_scoreable(tmp_path):
    briefs = tmp_path / "briefs.jsonl"
    outputs = tmp_path / "outputs.jsonl"
    packet = tmp_path / "packet.jsonl"
    key = tmp_path / "key.jsonl"
    votes = tmp_path / "votes.jsonl"
    report = tmp_path / "report.json"

    write_jsonl(
        briefs,
        [
            {"id": "a", "prompt": "A sufficiently concrete first evaluation brief."},
            {"id": "b", "prompt": "A sufficiently concrete second evaluation brief."},
        ],
    )
    output_rows = []
    for brief_id in ("a", "b"):
        for run in (1, 2):
            for condition in ("control", "treatment"):
                output_rows.append(
                    {
                        "brief_id": brief_id,
                        "condition": condition,
                        "run": run,
                        "text": f"{brief_id}-{run}-{condition}",
                        "input_tokens": 10 if condition == "control" else 12,
                        "output_tokens": 20 if condition == "control" else 24,
                        "wall_seconds": 1 if condition == "control" else 2,
                    }
                )
    write_jsonl(outputs, output_rows)

    subprocess.run(
        [
            sys.executable,
            str(HARNESS),
            "packet",
            "--briefs",
            str(briefs),
            "--outputs",
            str(outputs),
            "--packet",
            str(packet),
            "--key",
            str(key),
            "--seed",
            "frozen",
        ],
        check=True,
    )

    packet_rows = read_jsonl(packet)
    key_rows = read_jsonl(key)
    assert len(packet_rows) == len(key_rows) == 4
    assert all("condition" not in json.dumps(row) for row in packet_rows)
    assert {row["comparison_id"] for row in packet_rows} == {
        row["comparison_id"] for row in key_rows
    }

    votes_rows = []
    for answer in key_rows:
        treatment_side = (
            "left" if answer["left_condition"] == "treatment" else "right"
        )
        control_side = "right" if treatment_side == "left" else "left"
        ratings = {
            treatment_side: {
                "fit": 6,
                "useful_surprise": 6,
                "set_diversity": 6,
                "craft": 6,
            },
            control_side: {
                "fit": 5,
                "useful_surprise": 5,
                "set_diversity": 5,
                "craft": 5,
            },
        }
        votes_rows.append(
            {
                "comparison_id": answer["comparison_id"],
                "judge_id": "judge-1",
                "ratings": ratings,
                "want": treatment_side,
            }
        )
    write_jsonl(votes, votes_rows)

    subprocess.run(
        [
            sys.executable,
            str(HARNESS),
            "score",
            "--votes",
            str(votes),
            "--key",
            str(key),
            "--outputs",
            str(outputs),
            "--report",
            str(report),
        ],
        check=True,
    )
    result = json.loads(report.read_text(encoding="utf-8"))
    assert result["votes"]["raw_vote_rows"] == 4
    assert result["votes"]["brief_judge_cells"] == 2
    assert result["votes"]["treatment_wins"] == 2
    assert result["votes"]["control_wins"] == 0
    assert result["mean_treatment_minus_control"] == {
        "craft": 1.0,
        "fit": 1.0,
        "set_diversity": 1.0,
        "useful_surprise": 1.0,
    }
    assert result["mean_costs"]["control"]["total_tokens"] == 30.0
    assert result["mean_costs"]["treatment"]["total_tokens"] == 36.0


def test_packet_refuses_an_unpaired_run(tmp_path):
    briefs = tmp_path / "briefs.jsonl"
    outputs = tmp_path / "outputs.jsonl"
    write_jsonl(briefs, [{"id": "a", "prompt": "A concrete evaluation brief."}])
    write_jsonl(
        outputs,
        [
            {
                "brief_id": "a",
                "condition": "control",
                "run": 1,
                "text": "only one side",
            }
        ],
    )
    completed = subprocess.run(
        [
            sys.executable,
            str(HARNESS),
            "packet",
            "--briefs",
            str(briefs),
            "--outputs",
            str(outputs),
            "--packet",
            str(tmp_path / "packet.jsonl"),
            "--key",
            str(tmp_path / "key.jsonl"),
            "--seed",
            "frozen",
        ],
        text=True,
        capture_output=True,
    )
    assert completed.returncode != 0
    assert "missing paired outputs" in completed.stderr
