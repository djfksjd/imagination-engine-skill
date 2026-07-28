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


def test_extremal_widens_the_draw_and_carries_no_threshold(run):
    """extremal used to raise a rubric threshold as well as widening the hand.
    The threshold is gone from the whole skill - it discriminated nothing - so
    what is left is the part that always did the work: more domains, two rules
    to break, and a stricter cull."""
    normal = draw(run, "--modes", "nonhuman")
    extremal = draw(run, "--modes", "extremal")
    assert len(extremal["draw"]["domains"]) > len(normal["draw"]["domains"])
    assert len(extremal["draw"]["constraints"]) == 2
    for payload in (normal, extremal):
        assert "thresholds" not in payload["requirements"]


def test_default_modes_apply_when_unspecified(run):
    payload = draw(run)
    assert [m["id"] for m in payload["modes"]] == ["nonhuman", "alien-physics"]


def test_sense_carries_its_required_fields(run):
    payload = draw(run, "--modes", "affect")
    assert len(payload["draw"]["sense"]["required_fields"]) == 4


def test_stacking_too_many_modes_is_refused(run):
    """SKILL.md says stack up to three. A warning left the rule advisory."""
    res = run("draw.py", "--topic", "x", "--modes", "baby,nonhuman,affect,extremal", "--json")
    assert res.code == 1
    assert "the limit is 3" in res.err


def test_grounded_and_nonhuman_are_refused_at_the_draw(run):
    """grounded substitutes the axis nonhuman exists to enforce, so one of the
    two would have no effect. The draw is where the run is defined, so it is
    refused here rather than left to the gate."""
    res = run("draw.py", "--topic", "x", "--modes", "grounded,nonhuman", "--json")
    assert res.code == 1
    assert "cannot be stacked" in res.err


def test_the_draw_records_the_request_that_produced_it(run, tmp_path):
    res = run("draw.py", "--topic", "a stairwell", "--modes", "nonhuman", "--run", "2",
              "--anchor", "1", "--json")
    assert res.code == 0, res
    payload = res.json()
    assert payload["draw_schema_version"] == 3
    assert payload["request"] == {
        "topic": "a stairwell", "run": 2, "salt": "", "mode_ids": ["nonhuman"],
        "anchor": 1, "requested_domains": 3,
    }


def test_the_anchor_is_seed_material(run):
    """--anchor used only to be copied into the payload, so rewriting it in
    draw.json replayed clean and deleted the operational_path requirement."""
    a1 = draw(run, "--modes", "baby,nonhuman,affect", "--anchor", "1")
    a3 = draw(run, "--modes", "baby,nonhuman,affect", "--anchor", "3")
    assert a1["draw"] != a3["draw"]


def test_grounded_is_seed_material(run):
    """grounded substitutes a rubric axis and requires a section, so removing it
    afterwards is the same relaxation the anchor edit was."""
    plain = draw(run, "--modes", "affect")
    grounded = draw(run, "--modes", "affect,grounded")
    assert plain["draw"] != grounded["draw"]


def test_the_requested_domain_count_is_seed_material(run):
    wide = draw(run, "--domains", "4")
    normal = draw(run, "--domains", "3")
    assert {d["id"] for d in normal["draw"]["domains"]} - {d["id"] for d in wide["draw"]["domains"]}


def test_a_narrower_hand_than_three_is_refused(run):
    res = run("draw.py", "--topic", "x", "--domains", "2", "--json")
    assert res.code == 1
    assert "at least 3" in res.err

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
    assert "probe:" in res.out and "guard:" in res.out
    assert "RUBRIC:" in res.out and "No numeric threshold" in res.out


# --------------------------------------------- the salt cannot be the policy


def test_the_salt_cannot_spell_a_policy_field(run):
    """The policy fields seed the shuffle, but they used to be pasted into one
    string with a separator `--salt` was free to contain: `--anchor 1 --salt
    $'\x1fanchor=3'` dealt the anchor-3 hand exactly, and the gate then accepted
    a run that owed no operational path. The downgrade cost nothing at all."""
    strict = draw(run, "--modes", "baby,nonhuman,affect", "--anchor", "3")
    for salt in ("\x1fanchor=3", "anchor=3", "|8:anchor=3", "0:|8:anchor=3",
                 " anchor=3", "0:|8:anchor=3|8:domains=4"):
        res = run("draw.py", "--topic", TOPIC, "--json", "--modes", "baby,nonhuman,affect",
                  "--anchor", "1", "--salt", salt)
        if res.code == 0:
            assert res.json()["draw"] != strict["draw"], f"salt {salt!r} impersonated --anchor 3"
        else:
            assert res.code == 1, res


def test_the_seed_separator_is_refused_rather_than_stripped(run):
    """Stripping it would map two different requests onto one hand, which is the
    property being defended."""
    for args in (("--salt", "\x1fanchor=3"), ("--topic", f"{TOPIC}\x1fx")):
        res = run("draw.py", "--topic", TOPIC, "--json", *args)
        assert res.code == 1, res
        assert "U+001F" in res.err


def test_an_ordinary_salt_still_redeals(run):
    """The fix must not have turned --salt into a no-op."""
    plain = draw(run, "--modes", "baby,affect")
    salted = draw(run, "--modes", "baby,affect", "--salt", "second attempt")
    assert plain["draw"] != salted["draw"]


def test_a_salt_cannot_spell_a_policy_field_through_normalization(run):
    """The length prefix used to be measured *before* the normalization that
    collapses whitespace runs, so it described a string that no longer existed
    by the time the seed was hashed. Two salts of equal raw length packed
    differently and normalized identically, and this pair reproduced the
    anchor-3 hand byte for byte from an anchor-1 request."""
    strict = draw(run, "--modes", "", "--anchor", "3", "--salt", "x" + " " * 99)
    downgraded = draw(run, "--modes", "", "--anchor", "1",
                      "--salt", "x" + " " * 88 + "|8:anchor=3")
    assert downgraded["draw"] != strict["draw"], (
        "an anchor-1 request impersonated anchor 3 through whitespace collapse")


def test_whitespace_padding_of_a_salt_cannot_shift_a_field_boundary(run):
    """The general form of the same bug: any transformation the hash applies
    after the measurement lets one field grow into the next. Salts that differ
    only in collapsible whitespace are one salt; salts that differ in content
    are different salts, whatever their raw lengths."""
    base = draw(run, "--modes", "affect", "--salt", "retry two")
    spaced = draw(run, "--modes", "affect", "--salt", "  retry   two  ")
    assert base["draw"] == spaced["draw"], "normalization must apply before measurement, not after"
    for salt in ("retry two|", "9:retry two", "retry twp"):
        other = draw(run, "--modes", "affect", "--salt", salt)
        assert other["draw"] != base["draw"], f"salt {salt!r} collided with a different salt"


def test_the_topic_and_the_salt_do_not_share_a_boundary(run):
    """`--topic` is the other free-text field that reaches the seed. It arrives
    as its own part rather than inside the packed one, so moving characters
    across the topic/salt boundary must change the hand: if it did not, a topic
    could carry salt material and vice versa. Codex flagged this field as
    unexamined; this is the examination."""
    seen = []
    for topic, salt in (("a stairwell", "between floors"),
                        ("a stairwell between floors", ""),
                        ("a stairwell between", "floors"),
                        ("a", "stairwell between floors")):
        res = run("draw.py", "--topic", topic, "--json", "--modes", "affect", "--salt", salt)
        assert res.code == 0, res
        seen.append(json.dumps(res.json()["draw"], sort_keys=True))
    assert len(set(seen)) == len(seen), "a split of the same characters dealt the same hand"
