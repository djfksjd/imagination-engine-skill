"""The gate is fail-closed: anything it cannot verify is a failure. These tests
pin each way the required work can be skipped."""

from __future__ import annotations

import json
from copy import deepcopy

import pytest


@pytest.fixture
def candidate(references):
    return json.loads((references / "example-candidate.json").read_text(encoding="utf-8"))


def write(tmp_path, payload):
    path = tmp_path / "candidate.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return str(path)


def test_the_shipped_example_passes(run, references):
    res = run("score_gate.py", "--candidate", str(references / "example-candidate.json"))
    assert res.code == 0, res.out
    assert "PASSED" in res.out


def test_mean_below_threshold_fails(run, tmp_path, candidate):
    c = deepcopy(candidate)
    for axis in c["scores"]:
        c["scores"][axis]["score"] = 7
    res = run("score_gate.py", "--candidate", write(tmp_path, c), "--json")
    assert res.code == 2
    assert any("below the 8.0 threshold" in f for f in res.json()["failures"])


def test_single_low_axis_fails_even_with_a_good_mean(run, tmp_path, candidate):
    c = deepcopy(candidate)
    c["scores"]["non_anthropocentrism"]["score"] = 3
    c["scores"]["internal_consistency"]["score"] = 10
    c["scores"]["emotional_residue"]["score"] = 10
    c["scores"]["integration"]["score"] = 10
    res = run("score_gate.py", "--candidate", write(tmp_path, c), "--json")
    assert res.code == 2
    assert any("non_anthropocentrism=3" in f for f in res.json()["failures"])


def test_uniform_scores_are_flagged(run, tmp_path, candidate):
    c = deepcopy(candidate)
    for axis in c["scores"]:
        c["scores"][axis]["score"] = 9
    res = run("score_gate.py", "--candidate", write(tmp_path, c), "--json")
    warnings = res.json()["warnings"]
    assert any("same score" in w for w in warnings)
    assert any("no axis below 9" in w for w in warnings)


def test_thin_justification_fails(run, tmp_path, candidate):
    c = deepcopy(candidate)
    c["scores"]["imageability"]["justification"] = "it is good"
    res = run("score_gate.py", "--candidate", write(tmp_path, c), "--json")
    assert res.code == 2
    assert any("justification" in f for f in res.json()["failures"])


def test_missing_section_fails(run, tmp_path, candidate):
    c = deepcopy(candidate)
    del c["sections"]["world_effect"]
    res = run("score_gate.py", "--candidate", write(tmp_path, c), "--json")
    assert res.code == 2
    assert any("sections.world_effect: missing" in f for f in res.json()["failures"])


def test_thin_section_fails(run, tmp_path, candidate):
    c = deepcopy(candidate)
    c["sections"]["first_encounter"] = "She walks in and it is strange."
    res = run("score_gate.py", "--candidate", write(tmp_path, c), "--json")
    assert res.code == 2
    assert any("sections.first_encounter" in f for f in res.json()["failures"])


def test_deleted_law_without_a_replacement_fails(run, tmp_path, candidate):
    c = deepcopy(candidate)
    c["broken_rule"]["now_impossible"] = "nothing"
    res = run("score_gate.py", "--candidate", write(tmp_path, c), "--json")
    assert res.code == 2
    assert any("now_impossible" in f for f in res.json()["failures"])


def test_decorative_domain_fails(run, tmp_path, candidate):
    c = deepcopy(candidate)
    c["domains_used"][1]["answer_to_probe"] = "it is in there"
    res = run("score_gate.py", "--candidate", write(tmp_path, c), "--json")
    assert res.code == 2
    assert any("decoration" in f for f in res.json()["failures"])


def test_too_few_domains_fails(run, tmp_path, candidate):
    c = deepcopy(candidate)
    c["domains_used"] = c["domains_used"][:2]
    res = run("score_gate.py", "--candidate", write(tmp_path, c), "--json")
    assert res.code == 2


def test_duplicate_domains_fail(run, tmp_path, candidate):
    c = deepcopy(candidate)
    c["domains_used"][1]["id"] = c["domains_used"][0]["id"]
    res = run("score_gate.py", "--candidate", write(tmp_path, c), "--json")
    assert res.code == 2
    assert any("duplicate domain ids" in f for f in res.json()["failures"])


def test_missing_resembles_fails(run, tmp_path, candidate):
    c = deepcopy(candidate)
    c["resembles"] = []
    res = run("score_gate.py", "--candidate", write(tmp_path, c), "--json")
    assert res.code == 2
    assert any("resembles" in f for f in res.json()["failures"])


def test_missing_weakest_fix_fails(run, tmp_path, candidate):
    c = deepcopy(candidate)
    c["weakest_fix"] = "fine"
    res = run("score_gate.py", "--candidate", write(tmp_path, c), "--json")
    assert res.code == 2


def test_unknown_or_missing_axis_fails(run, tmp_path, candidate):
    c = deepcopy(candidate)
    c["scores"]["vibes"] = {"score": 9, "justification": "x" * 50}
    del c["scores"]["integration"]
    res = run("score_gate.py", "--candidate", write(tmp_path, c), "--json")
    assert res.code == 2
    failures = " ".join(res.json()["failures"])
    assert "unknown axes" in failures and "missing axes" in failures


def test_out_of_range_score_fails(run, tmp_path, candidate):
    c = deepcopy(candidate)
    c["scores"]["integration"]["score"] = 11
    res = run("score_gate.py", "--candidate", write(tmp_path, c), "--json")
    assert res.code == 2
    assert any("integer 1-10" in f for f in res.json()["failures"])


def test_extremal_thresholds_reject_a_passing_default_candidate(run, references):
    res = run("score_gate.py", "--candidate", str(references / "example-candidate.json"), "--extremal", "--json")
    assert res.code == 2
    assert res.json()["thresholds"] == {"min_mean": 9.0, "min_axis": 8}


def test_unreadable_candidate_is_a_usage_error(run, tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{not json", encoding="utf-8")
    res = run("score_gate.py", "--candidate", str(path))
    assert res.code == 1


def test_grounded_mode_swaps_the_unsatisfiable_axis(run, tmp_path, candidate):
    """A buildable result exists for someone by construction, so scoring it on
    distance from human centring guarantees failure. --grounded replaces that
    axis and adds an obligation instead of removing one."""
    c = deepcopy(candidate)
    c["modes"] = ["alien-physics", "grounded"]
    del c["scores"]["non_anthropocentrism"]
    c["scores"]["translation_integrity"] = {
        "score": 8,
        "justification": "The broken law survives the buildable version intact and the losses are named in the path.",
    }
    c["sections"]["operational_path"] = "A" + " concrete path a team could take within a month, and the part of the principle that does not survive it." * 3
    res = run("score_gate.py", "--candidate", write(tmp_path, c), "--grounded", "--json")
    assert res.code == 0, res.out
    assert res.json()["grounded"] is True


def test_grounded_requires_the_operational_path(run, tmp_path, candidate):
    c = deepcopy(candidate)
    c["modes"] = ["alien-physics", "grounded"]
    del c["scores"]["non_anthropocentrism"]
    c["scores"]["translation_integrity"] = {
        "score": 8, "justification": "The law survives and the losses from building it are stated in full.",
    }
    res = run("score_gate.py", "--candidate", write(tmp_path, c), "--grounded", "--json")
    assert res.code == 2
    assert any("operational_path" in f for f in res.json()["failures"])


def test_the_default_gate_still_wants_the_default_axis(run, tmp_path, candidate):
    c = deepcopy(candidate)
    del c["scores"]["non_anthropocentrism"]
    c["scores"]["translation_integrity"] = {
        "score": 8, "justification": "Scored for a grounded run, but this call does not pass the flag.",
    }
    res = run("score_gate.py", "--candidate", write(tmp_path, c), "--json")
    assert res.code == 2
    failures = " ".join(res.json()["failures"])
    assert "missing axes non_anthropocentrism" in failures and "unknown axes translation_integrity" in failures


def test_the_grounded_flag_is_not_evidence_of_a_grounded_run(run, tmp_path, candidate):
    """Unchecked, --grounded is a way to delete whichever axis you are about to
    score badly. The flag has to agree with the run the candidate declares."""
    c = deepcopy(candidate)
    c["modes"] = ["alien-physics"]
    del c["scores"]["non_anthropocentrism"]
    c["scores"]["translation_integrity"] = {
        "score": 8, "justification": "Scored as though this were a grounded run, which the candidate never claims.",
    }
    c["sections"]["operational_path"] = "A path a team could take, and what the principle loses on the way. " * 4
    res = run("score_gate.py", "--candidate", write(tmp_path, c), "--grounded", "--json")
    assert res.code == 2
    assert any("does not declare grounded" in f for f in res.json()["failures"])


def test_grounded_cannot_delete_the_axis_nonhuman_mode_enforces(run, tmp_path, candidate):
    c = deepcopy(candidate)
    c["modes"] = ["nonhuman", "grounded"]
    del c["scores"]["non_anthropocentrism"]
    c["scores"]["translation_integrity"] = {
        "score": 8, "justification": "Claiming both modes at once would exempt the axis that defines one of them.",
    }
    c["sections"]["operational_path"] = "A path a team could take, and what the principle loses on the way. " * 4
    res = run("score_gate.py", "--candidate", write(tmp_path, c), "--grounded", "--json")
    assert res.code == 2
    assert any("also claims nonhuman" in f for f in res.json()["failures"])


def test_a_two_character_cjk_name_is_a_name(run, tmp_path, candidate):
    """The old floor was three characters, which rejects a complete Korean or
    Chinese name and accepts 'TBD - fill in later'."""
    c = deepcopy(candidate)
    c["sections"]["name"] = "\uae30\ub465"
    res = run("score_gate.py", "--candidate", write(tmp_path, c), "--json")
    assert res.code == 0, res.out


def test_a_placeholder_name_is_refused_however_long(run, tmp_path, candidate):
    c = deepcopy(candidate)
    c["sections"]["name"] = "TBD"
    res = run("score_gate.py", "--candidate", write(tmp_path, c), "--json")
    assert res.code == 2
    assert any("placeholder" in f for f in res.json()["failures"])
