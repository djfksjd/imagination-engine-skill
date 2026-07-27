"""The draw is the part of the pipeline the model does not control. These tests
pin the three properties the rest of the skill relies on: it is reproducible,
the drawn domains are genuinely far apart, and a rerun deals new material
instead of the same favourites."""

from __future__ import annotations

import json

TOPIC = "a machine that separates emotion from voice"


def draw(run_fixture, *args):
    res = run_fixture("draw.py", "--topic", TOPIC, "--json", *args)
    assert res.code == 0, res
    return res.json()


def test_same_inputs_give_the_same_hand(run):
    a = draw(run, "--modes", "baby,affect")
    b = draw(run, "--modes", "baby,affect")
    assert a == b


def test_salt_changes_the_hand(run):
    a = draw(run, "--modes", "baby,affect")
    b = draw(run, "--modes", "baby,affect", "--salt", "second attempt")
    assert a["draw"] != b["draw"]


def test_different_topic_changes_the_hand(run):
    a = draw(run)
    res = run("draw.py", "--topic", "a bridge that refuses traffic", "--json")
    assert res.code == 0
    assert res.json()["draw"] != a["draw"]


def test_domains_span_disjoint_categories(run):
    for run_index in ("1", "2", "3", "4"):
        payload = draw(run, "--run", run_index)
        cats = [d["category"] for d in payload["draw"]["domains"]]
        assert len(cats) == len(set(cats)), f"run {run_index} drew two domains from one category"


def test_reruns_deal_fresh_material(run):
    first = {d["id"] for d in draw(run, "--run", "1")["draw"]["domains"]}
    second = {d["id"] for d in draw(run, "--run", "2")["draw"]["domains"]}
    third = {d["id"] for d in draw(run, "--run", "3")["draw"]["domains"]}
    assert not (first & second)
    assert not (second & third)
    assert not (first & third)


def test_baby_mode_forces_the_cognition_error_category(run):
    for run_index in ("1", "2", "5"):
        payload = draw(run, "--modes", "baby", "--run", run_index)
        cats = {d["category"] for d in payload["draw"]["domains"]}
        assert "cognition-error" in cats


def test_extremal_raises_thresholds_and_widens_the_draw(run):
    normal = draw(run, "--modes", "nonhuman")
    extremal = draw(run, "--modes", "extremal")
    assert extremal["requirements"]["thresholds"] == {"min_mean": 9.0, "min_axis": 8}
    assert normal["requirements"]["thresholds"] == {"min_mean": 8.0, "min_axis": 6}
    assert len(extremal["draw"]["domains"]) > len(normal["draw"]["domains"])
    assert len(extremal["draw"]["constraints"]) == 2


def test_default_modes_apply_when_unspecified(run):
    payload = draw(run)
    assert [m["id"] for m in payload["modes"]] == ["nonhuman", "alien-physics"]


def test_sense_carries_its_required_fields(run):
    payload = draw(run, "--modes", "affect")
    assert len(payload["draw"]["sense"]["required_fields"]) == 4


def test_stacking_too_many_modes_warns(run):
    payload = draw(run, "--modes", "baby,nonhuman,affect,alien-physics")
    assert any("modes stacked" in note for note in payload["notes"])


def test_unknown_mode_fails(run):
    res = run("draw.py", "--topic", TOPIC, "--modes", "chaos")
    assert res.code == 1
    assert "unknown mode" in res.err


def test_too_many_domains_fails_rather_than_repeating_a_category(run):
    res = run("draw.py", "--topic", TOPIC, "--domains", "99")
    assert res.code == 1
    assert "disjointness" in res.err


def test_missing_topic_fails(run):
    res = run("draw.py", "--modes", "baby")
    assert res.code == 1


def test_bad_anchor_fails(run):
    res = run("draw.py", "--topic", TOPIC, "--anchor", "9")
    assert res.code == 1


def test_out_writes_draw_json(run, tmp_path):
    res = run("draw.py", "--topic", TOPIC, "--out", str(tmp_path))
    assert res.code == 0
    payload = json.loads((tmp_path / "draw.json").read_text(encoding="utf-8"))
    assert payload["topic"] == TOPIC
    assert payload["draw"]["domains"]


def test_list_modes(run):
    res = run("draw.py", "--list-modes")
    assert res.code == 0
    assert "extremal" in res.out and "anchors" in res.out


def test_human_output_contains_probes_and_guards(run):
    res = run("draw.py", "--topic", TOPIC, "--modes", "nonhuman")
    assert res.code == 0
    assert "probe:" in res.out and "guard:" in res.out and "THRESHOLDS" in res.out
