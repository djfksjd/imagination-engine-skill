"""The gate is fail-closed and it is the only path to "passed".

Every test here has the same shape: take the shipped set of four artefacts that
passes, change exactly one thing, and check that the gate notices. The changes
are the ones a model under pressure would actually make.
"""

from __future__ import annotations

import re
from copy import deepcopy

import pytest


def rename(markdown: str, new: str) -> str:
    """Swap only the bound name. A blanket replace would also hit the word
    where it appears inside the other sections."""
    return re.sub(r"(<!-- bind: sections\.name -->).*?(<!-- /bind -->)",
                  lambda m: m.group(1) + new + m.group(2), markdown, count=1, flags=re.S)


def failures(res) -> str:
    return " ".join(res.json()["failures"])


# --------------------------------------------------------------- the baseline


def test_the_shipped_set_passes(gate):
    res = gate()
    assert res.code == 0, res.out


def test_the_verdict_records_the_policy_that_ran(gate):
    policy = gate().json()["policy"]
    assert policy["profile"] == "default"
    assert policy["thresholds"] == {"min_mean": 8.0, "min_axis": 6}
    assert len(policy["rubric_sha256"]) == 64
    assert policy["axis_substitution"] is None


# ------------------------------------------------------- policy cannot be set


@pytest.mark.parametrize("flag", ["--min-mean", "--min-axis", "--rubric"])
def test_thresholds_cannot_be_set_at_verdict_time(run, gate_args, flag):
    """These were larger bypasses than any of the mode flags: --extremal
    --min-mean 1 --min-axis 1 passed the shipped example with exit 0."""
    res = run("score_gate.py", *gate_args, flag, "1")
    assert res.code == 1
    assert "unrecognized arguments" in res.err


@pytest.mark.parametrize("flag", ["--extremal", "--grounded"])
def test_the_profile_cannot_be_asserted_at_verdict_time(run, gate_args, flag):
    res = run("score_gate.py", *gate_args, flag)
    assert res.code == 1
    assert "unrecognized arguments" in res.err


def test_the_profile_comes_from_the_drawn_modes(run, gate):
    """A run drawn with extremal is judged at 9.0/8 without anyone saying so."""
    res = run("draw.py", "--topic", "a machine that separates emotion from voice",
              "--modes", "baby,nonhuman,extremal", "--run", "1", "--anchor", "1", "--json")
    assert res.code == 0, res
    out = gate(draw=res.json())
    assert out.json()["policy"]["thresholds"] == {"min_mean": 9.0, "min_axis": 8}


# ----------------------------------------------------------- the draw replays


def test_a_card_swapped_after_the_deal_is_caught(gate, example_draw):
    d = deepcopy(example_draw)
    d["draw"]["perspective"] = {"id": "one-i-preferred", "stance": "x", "test": "y"}
    res = gate(draw=d)
    assert res.code == 2
    assert "does not follow from its own request" in failures(res)


def test_a_domain_swapped_after_the_deal_is_caught(gate, example_draw):
    d = deepcopy(example_draw)
    d["draw"]["domains"][0] = {"id": "fungal-networks", "category": "nonhuman-biology",
                               "label": "x", "probe": "y"}
    res = gate(draw=d)
    assert res.code == 2
    assert "draw.domains" in failures(res)


def test_a_draw_without_a_request_block_is_a_usage_error(gate, example_draw):
    d = deepcopy(example_draw)
    del d["request"]
    res = gate(draw=d, json_out=False)
    assert res.code == 1
    assert "no request block" in res.err


# ------------------------------------------------ the candidate is bound to it


def test_a_candidate_from_another_run_is_caught(gate, example_candidate):
    c = deepcopy(example_candidate)
    c["run"] = 2
    res = gate(candidate=c)
    assert res.code == 2
    assert "run: candidate says 2" in failures(res)


def test_a_candidate_claiming_modes_it_was_not_drawn_with_is_caught(gate, example_candidate):
    """This is how the grounded substitution used to be obtained: assert the
    mode on the candidate and pass the matching flag."""
    c = deepcopy(example_candidate)
    c["modes"] = ["grounded"]
    res = gate(candidate=c)
    assert res.code == 2
    assert "the profile the gate applies comes from the run" in failures(res)


def test_dropping_a_drawn_domain_is_caught(gate, example_candidate):
    """A domain that did no work is not dropped - it is replaced by redealing."""
    c = deepcopy(example_candidate)
    c["domains_used"] = c["domains_used"][:2]
    res = gate(candidate=c)
    assert res.code == 2
    assert "Every drawn domain is binding" in failures(res)


def test_a_constraint_left_unaccounted_for_is_caught(gate, example_candidate):
    c = deepcopy(example_candidate)
    c["broken_rule"]["how_each_is_broken"] = []
    res = gate(candidate=c)
    assert res.code == 2
    assert "must account for every drawn constraint" in failures(res)


@pytest.mark.parametrize("field", ["perspective_id", "sense_seed_id", "affect_pair_id"])
def test_the_quiet_cards_are_bound_too(gate, example_candidate, field):
    """Before this, only domains and the constraint were checked, so three of
    the drawn cards could be ignored while the gate still said passed."""
    c = deepcopy(example_candidate)
    c[field] = "something-else"
    res = gate(candidate=c)
    assert res.code == 2
    assert field in failures(res)


# --------------------------------------------------------------- the scoring


def test_mean_below_threshold_fails(gate, example_candidate):
    c = deepcopy(example_candidate)
    for axis in c["scores"]:
        c["scores"][axis]["score"] = 7
    res = gate(candidate=c)
    assert res.code == 2
    assert "below the 8.0 threshold" in failures(res)


def test_a_single_low_axis_fails_even_with_a_good_mean(gate, example_candidate):
    c = deepcopy(example_candidate)
    c["scores"]["non_anthropocentrism"]["score"] = 3
    for axis in ("internal_consistency", "emotional_residue", "integration"):
        c["scores"][axis]["score"] = 10
    res = gate(candidate=c)
    assert res.code == 2
    assert "non_anthropocentrism=3" in failures(res)


def test_a_thin_justification_fails(gate, example_candidate):
    c = deepcopy(example_candidate)
    c["scores"]["imageability"]["justification"] = "it is good"
    res = gate(candidate=c)
    assert res.code == 2
    assert "scores.imageability.justification" in failures(res)


def test_a_decorative_domain_fails(gate, example_candidate):
    c = deepcopy(example_candidate)
    c["domains_used"][1]["answer_to_probe"] = "it is in there"
    res = gate(candidate=c)
    assert res.code == 2
    assert "decoration" in failures(res)


def test_uniform_scores_are_flagged(gate, example_candidate):
    c = deepcopy(example_candidate)
    for axis in c["scores"]:
        c["scores"][axis]["score"] = 9
    warnings = gate(candidate=c).json()["warnings"]
    assert any("same score" in w for w in warnings)


def test_a_two_character_cjk_name_is_a_name(gate, example_candidate, example_markdown):
    """The old floor was three characters, which rejects a complete Korean or
    Chinese name and accepts 'TBD - fill in later'."""
    c = deepcopy(example_candidate)
    c["sections"]["name"] = "기둥"
    res = gate(candidate=c, markdown=rename(example_markdown, "기둥"))
    assert res.code == 0, res.out


def test_a_placeholder_name_is_refused_however_long(gate, example_candidate, example_markdown):
    c = deepcopy(example_candidate)
    c["sections"]["name"] = "TBD"
    res = gate(candidate=c, markdown=rename(example_markdown, "TBD"))
    assert res.code == 2
    assert "placeholder" in failures(res)


# ----------------------------------------------------------- the manual bans


def test_a_manual_ban_with_no_written_answer_fails(gate, example_candidate):
    """These used to be printed by banlist.py and then never checked again."""
    c = deepcopy(example_candidate)
    c["manual_checks_cleared"] = {}
    res = gate(candidate=c)
    assert res.code == 2
    assert "manual_checks_cleared[obvious-12]" in failures(res)


def test_a_one_word_answer_to_a_manual_ban_fails(gate, example_candidate):
    c = deepcopy(example_candidate)
    c["manual_checks_cleared"] = {"obvious-12": "avoided"}
    res = gate(candidate=c)
    assert res.code == 2
    assert "manual_checks_cleared[obvious-12]" in failures(res)


# ------------------------------------------ the draft is bound to the candidate


def test_the_draft_that_gets_shown_must_be_the_one_that_was_scored(gate, example_markdown):
    """The whole reason the two gates were merged: score_gate read candidate.json
    and cliche_lint read draft.md, and nothing connected them."""
    tampered = example_markdown.replace(
        "<!-- bind: sections.avoided -->",
        "<!-- bind: sections.avoided -->\nSomething else entirely, written after the score.", 1)
    res = gate(markdown=tampered)
    assert res.code == 2
    assert "is not the text that was scored" in failures(res)


def test_a_draft_with_no_bind_blocks_fails(gate):
    res = gate(markdown="# Flatting\n\nA nice piece of prose with no binding at all.\n")
    assert res.code == 2
    assert "no <!-- bind: sections." in failures(res)


def test_a_duplicated_bind_block_fails(gate, example_markdown):
    doubled = example_markdown + "\n<!-- bind: sections.name -->Flatting<!-- /bind -->\n"
    res = gate(markdown=doubled)
    assert res.code == 2
    assert "appears 2 times" in failures(res)


def test_banned_material_in_the_draft_fails(gate, example_markdown):
    res = gate(markdown=example_markdown + "\n\nIt is basically a cyberpunk city, but stranger.\n")
    assert res.code == 2
    assert "banned material" in failures(res)


def test_whitespace_normalization_does_not_break_the_binding(gate, example_markdown):
    """Reflowing a paragraph is editing, not rewriting; it must still pass."""
    res = gate(markdown=example_markdown.replace(". ", ".\n"))
    assert res.code == 0, res.out


# ------------------------------------------------------------------ plumbing


def test_all_four_artefacts_are_required(run, gate_args):
    for i in range(0, 8, 2):
        partial = gate_args[:i] + gate_args[i + 2:]
        res = run("score_gate.py", *partial)
        assert res.code == 1, f"{gate_args[i]} should be required"


def test_an_unreadable_candidate_is_a_usage_error(run, gate_args, tmp_path):
    broken = tmp_path / "broken.json"
    broken.write_text("{not json", encoding="utf-8")
    res = run("score_gate.py", "--candidate", str(broken), *gate_args[2:])
    assert res.code == 1
