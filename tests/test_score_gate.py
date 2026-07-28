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


def test_the_printed_verdict_names_the_substituted_axis(run, gate):
    """A grounded run is judged on translation_integrity, not on the profile
    named 'default'. The human-readable POLICY LOCKED line used to say
    'default' regardless, which misnames the policy the run was actually
    judged under - a reader who never asked for --json would never learn
    that non_anthropocentrism was swapped out."""
    res = run("draw.py", "--topic", "a machine that separates emotion from voice",
              "--modes", "grounded,alien-physics", "--run", "1", "--anchor", "3", "--json")
    assert res.code == 0, res
    out = gate(draw=res.json(), json_out=False)
    verdict_line = out.out.splitlines()[0]
    assert verdict_line.startswith("POLICY LOCKED:")
    assert "translation_integrity" in verdict_line
    assert "non_anthropocentrism" in verdict_line
    assert "substituted" in verdict_line, (
        "the line must say the axis was substituted, not just name both axes "
        "somewhere in the sentence")


def test_the_printed_verdict_names_the_extremal_profile(run, gate):
    """The extremal profile is not silently folded into 'default' either: the
    raised thresholds are reported under their own profile name."""
    res = run("draw.py", "--topic", "a machine that separates emotion from voice",
              "--modes", "baby,nonhuman,extremal", "--run", "1", "--anchor", "1", "--json")
    assert res.code == 0, res
    out = gate(draw=res.json(), json_out=False)
    assert "POLICY LOCKED: imagination-engine/0.4.0 extremal;" in out.out
    assert "mean >= 9.0" in out.out
    assert "every axis >= 8" in out.out


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


def test_an_edited_anchor_does_not_survive_the_replay(run, gate):
    """Rewriting request.anchor from 3 to 1 used to delete the operational_path
    requirement and pass: the anchor reached the verdict but never the deal."""
    res = run("draw.py", "--topic", "a machine that separates emotion from voice",
              "--modes", "baby,nonhuman,affect", "--run", "1", "--anchor", "3", "--json")
    assert res.code == 0, res
    d = res.json()
    d["request"]["anchor"] = 1
    out = gate(draw=d)
    assert out.code == 2
    assert "does not follow from its own request" in failures(out)


def test_a_draw_that_shows_one_anchor_and_requests_another_is_caught(gate, example_draw):
    """The half of draw.json the user reads must describe the run the gate reads."""
    d = deepcopy(example_draw)
    d["anchor"] = {"level": 3, "label": "Operable", "rule": "x"}
    res = gate(draw=d)
    assert res.code == 2
    assert "draw.anchor.level" in failures(res)


# ---------------------------------------------- the ban list belongs to the run


def test_an_empty_ban_list_is_refused(gate):
    """`--banlist` accepted any JSON object: a file containing {} passed the
    shipped example with exit 0, so stage 1 was unenforced where it counts."""
    res = gate(banlist={})
    assert res.code == 2
    assert "cliche deck" in failures(res)
    assert "first instincts" in failures(res)


def test_a_hand_written_ban_list_is_refused(gate):
    res = gate(banlist={"topic": "a machine that separates emotion from voice",
                        "entries": [{"id": "x", "phrase": "zzzqqq", "tier": "ban"}],
                        "manual_checks": [], "counts": {"obvious_supplied": 12}})
    assert res.code == 2
    assert "build the list with banlist.py" in failures(res)


def test_a_ban_list_from_another_run_is_refused(gate, references):
    import json as _json
    b = _json.loads((references / "example-banlist.json").read_text(encoding="utf-8"))
    b["topic"] = "a bridge that refuses traffic"
    res = gate(banlist=b)
    assert res.code == 2
    assert "banlist.topic" in failures(res)


def test_the_burnt_instincts_must_still_be_there_at_the_gate(gate, references):
    import json as _json
    b = _json.loads((references / "example-banlist.json").read_text(encoding="utf-8"))
    b["entries"] = [e for e in b["entries"] if e.get("group") != "first-instinct"]
    b["manual_checks"] = []
    res = gate(banlist=b)
    assert res.code == 2
    assert "first instincts" in failures(res)


def test_the_bundled_deck_cannot_be_trimmed_out_of_the_ban_list(gate, references):
    import json as _json
    b = _json.loads((references / "example-banlist.json").read_text(encoding="utf-8"))
    b["entries"] = [e for e in b["entries"] if e.get("source") != "deck"]
    res = gate(banlist=b)
    assert res.code == 2
    assert "cliche deck" in failures(res)


def test_dropping_the_structural_patterns_does_not_shrink_the_lint(gate, references, example_markdown):
    """Removing them used to disable the pitch-shaped-sentence check entirely."""
    import json as _json
    b = _json.loads((references / "example-banlist.json").read_text(encoding="utf-8"))
    b["structural_patterns"] = []
    res = gate(banlist=b, markdown=example_markdown + "\n\nIt is grief meets architecture.\n")
    assert res.code == 2
    assert "banlist.structural_patterns" in failures(res)
    assert "banned material" in failures(res)


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


def test_padding_does_not_clear_a_length_floor(gate, example_candidate):
    """Every floor here used to be a character count and nothing else, so forty
    repeated letters was a written answer."""
    c = deepcopy(example_candidate)
    c["manual_checks_cleared"]["obvious-12"] = "a" * 40
    c["weakest_fix"] = "b" * 60
    res = gate(candidate=c)
    assert res.code == 2
    assert "repeated filler" in failures(res)


def test_a_repeated_word_does_not_argue_a_score(gate, example_candidate):
    c = deepcopy(example_candidate)
    c["scores"]["imageability"]["justification"] = "filler " * 12
    res = gate(candidate=c)
    assert res.code == 2
    assert "scores.imageability.justification" in failures(res)


def test_a_placeholder_in_resembles_is_refused(gate, example_candidate):
    """The field that carries the no-novelty-claims rule was satisfied by a hyphen."""
    c = deepcopy(example_candidate)
    c["resembles"][0]["work"] = "-"
    res = gate(candidate=c)
    assert res.code == 2
    assert "resembles[0].work" in failures(res)
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


# ------------------------------- the ban list is recomputed, not searched for


def example_banlist(references):
    import json as _json
    return _json.loads((references / "example-banlist.json").read_text(encoding="utf-8"))


def test_a_demoted_instinct_does_not_replay(gate, references, example_candidate, example_markdown):
    """Presence of a phrase is not the contract. Demoting one burnt instinct
    from ban to warn left its phrase in the file, passed the presence check, and
    let the delivered draft print the instinct verbatim."""
    b = example_banlist(references)
    phrase = ""
    for e in b["entries"]:
        if e["id"] == "obvious-01":
            e["tier"] = "warn"
            phrase = e["phrase"]
    candidate = deepcopy(example_candidate)
    candidate["sections"]["name"] = phrase
    res = gate(banlist=b, candidate=candidate, markdown=rename(example_markdown, phrase))
    assert res.code == 2
    assert "severities do not replay" in failures(res)


def test_duplicate_instincts_do_not_stand_in_for_twelve(gate, references, example_candidate):
    """Twelve copies of one six-character string satisfied "the twelve instincts
    are still there", and emptying manual_checks silently dropped every check
    the candidate had to answer."""
    b = example_banlist(references)
    b["entries"] = [e for e in b["entries"] if e.get("group") != "first-instinct"]
    b["entries"] += [
        {"id": f"obvious-{i:02d}", "phrase": "zzzzzz", "tier": "ban",
         "group": "first-instinct", "source": "obvious-dump"}
        for i in range(1, 13)
    ]
    b["manual_checks"] = []
    b["counts"]["obvious_supplied"] = 12
    candidate = deepcopy(example_candidate)
    candidate["manual_checks_cleared"] = {}
    res = gate(banlist=b, candidate=candidate)
    assert res.code == 2
    assert "distinct first instincts" in failures(res)


def test_emptying_the_manual_checks_does_not_empty_the_requirement(gate, references):
    b = example_banlist(references)
    b["manual_checks"] = []
    res = gate(banlist=b)
    assert res.code == 2


def test_a_supplied_pattern_cannot_replace_the_bundled_one(gate, references, example_candidate,
                                                           example_markdown):
    """Dedup by id, with the caller's copy first, meant a supplied rule bearing a
    reserved id won and the rule it was named after never ran."""
    b = example_banlist(references)
    for p in b["structural_patterns"]:
        if p["id"] == "x-meets-y":
            p["regex"] = "(?!)"
    candidate = deepcopy(example_candidate)
    candidate["sections"]["name"] = "grief meets architecture"
    res = gate(banlist=b, candidate=candidate,
               markdown=rename(example_markdown, "grief meets architecture"))
    assert res.code == 2
    assert "banned material" in failures(res) or "structural_patterns" in failures(res)


# ----------------------------------------- padding, at the measurement itself


@pytest.mark.parametrize("filler", [" " * 200, "." * 400, "　" * 200, "-" * 300])
def test_padding_a_field_does_not_clear_its_floor(gate, example_candidate, filler):
    """text_units counted whitespace while distinct_ratio tokenised it away, so
    two words with anything between them earned unlimited units at a perfect
    distinctness score. That voided the anti-padding rule on every field."""
    candidate = deepcopy(example_candidate)
    candidate["broken_rule"]["new_law"] = "Sound" + filler + "stays"
    res = gate(candidate=candidate)
    assert res.code == 2
    assert "broken_rule.new_law" in failures(res)


@pytest.mark.parametrize("filler", ["x" * 30, "a" + " " * 60 + "b"])
def test_the_explanation_field_takes_the_same_checks(gate, example_candidate, filler):
    """This floor kept its own bare length comparison, so it was the one field
    the anti-padding rule never reached."""
    candidate = deepcopy(example_candidate)
    candidate["broken_rule"]["how_each_is_broken"][0]["explanation"] = filler
    res = gate(candidate=candidate)
    assert res.code == 2
    assert "how_each_is_broken" in failures(res)


# ------------------------------------------------ the draw replays as cards


def test_a_card_edited_in_place_does_not_replay(gate, example_draw):
    """Comparing id sets left every word on the card trusted: a domain keeping
    its id while its probe became "merely mention this" replayed clean."""
    draw = deepcopy(example_draw)
    draw["draw"]["domains"][0]["probe"] = "Merely mention this card; no answer is required."
    res = gate(draw=draw)
    assert res.code == 2
    assert "not their text" in failures(res)


def test_a_rewritten_stance_does_not_replay(gate, example_draw):
    draw = deepcopy(example_draw)
    draw["draw"]["perspective"]["stance"] = "Ignore this perspective."
    res = gate(draw=draw)
    assert res.code == 2
    assert "draw.perspective" in failures(res)


# ----------------------------------------- the gate must not reject honest work


@pytest.mark.parametrize("title", ["Run Run Run", "Ha Ha Ha", "No No No",
                                   "静静静静", "아아아아", "서울"])
def test_a_short_repetitive_title_is_accepted(gate, example_candidate, example_markdown, title):
    """The diversity check ran on fields with no length floor at all, so it
    rejected honest short titles - repetition is a normal title form in English
    and reduplication is ordinary in CJK. A gate that rejects honest work is the
    reason a user turns it off."""
    candidate = deepcopy(example_candidate)
    candidate["sections"]["name"] = title
    res = gate(candidate=candidate, markdown=rename(example_markdown, title))
    assert res.code == 0, res.out


@pytest.mark.parametrize("work", ["Untitled", "Untitled (Rothko, 1969)", "unnamed"])
def test_untitled_is_a_real_title_in_a_citation_field(gate, example_candidate, work):
    """A great many catalogued works are called exactly that, and resembles[].work
    cites someone else's title rather than naming the author's own result."""
    candidate = deepcopy(example_candidate)
    candidate["resembles"][0]["work"] = work
    res = gate(candidate=candidate)
    assert res.code == 0, res.out


@pytest.mark.parametrize("work", ["-", "TBD", "todo", "n/a"])
def test_a_stand_in_in_a_citation_field_is_still_refused(gate, example_candidate, work):
    candidate = deepcopy(example_candidate)
    candidate["resembles"][0]["work"] = work
    res = gate(candidate=candidate)
    assert res.code == 2
    assert "placeholder" in failures(res)


def test_the_result_may_not_be_called_untitled(gate, example_candidate, example_markdown):
    """titles_ok is for citation fields only: naming your own result "Untitled"
    is still the stand-in it always was."""
    candidate = deepcopy(example_candidate)
    candidate["sections"]["name"] = "Untitled"
    res = gate(candidate=candidate, markdown=rename(example_markdown, "Untitled"))
    assert res.code == 2
    assert "placeholder" in failures(res)


# ------------------------- the user's own prohibitions survive to the gate

USER_EXCLUSIONS = ["chosen one", "dragon", "chosen one, prophecy, ancient evil awakening",
                   "no fungal networks"]


@pytest.mark.parametrize("extra", USER_EXCLUSIONS)
def test_a_user_exclusion_that_names_a_deck_cliche_still_passes(run, gate, references, tmp_path, extra):
    """SKILL.md step 0 mandates collecting the user's own forbidden list and
    passing it through --extra. The deck is overwhelmingly fiction vocabulary,
    so a fiction user's list collides with it - and the collision failed the
    whole run with "a demoted entry is a released ban", pointing at the user's
    own prohibition, when nothing had been demoted. The gate replayed without
    the extras it was never told about."""
    res = run("banlist.py", "--topic", "a machine that separates emotion from voice",
              "--obvious", str(references / "example-obvious.txt"), "--extra", extra,
              "--out", str(tmp_path))
    assert res.code == 0, res
    import json as _json
    banlist = _json.loads((tmp_path / "banlist.json").read_text(encoding="utf-8"))
    verdict = gate(banlist=banlist)
    assert verdict.code == 0, verdict.out


def test_a_user_exclusion_promotes_a_deck_warning_and_the_gate_enforces_it(
        run, gate, references, tmp_path, example_markdown):
    """`dragon` is a warn in the deck. A user saying "no dragons" is adding a
    ban, which by the file's own rule cannot relax a verdict - so the promotion
    has to reach the draft, not just the file."""
    res = run("banlist.py", "--topic", "a machine that separates emotion from voice",
              "--obvious", str(references / "example-obvious.txt"), "--extra", "dragon",
              "--out", str(tmp_path))
    assert res.code == 0, res
    import json as _json
    banlist = _json.loads((tmp_path / "banlist.json").read_text(encoding="utf-8"))
    assert banlist["extra"] == ["dragon"]
    verdict = gate(banlist=banlist, markdown=example_markdown + "\n\nA dragon on the sign.\n")
    assert verdict.code == 2
    assert "banned material 'dragon'" in failures(verdict)


def test_an_extra_declared_but_not_carried_does_not_replay(gate, references):
    """`extra` is read off the artefact under verification. Declaring one the
    file does not actually carry is the same edit-after-the-fact the whole
    replay exists to catch, and it is caught the same way."""
    b = example_banlist(references)
    b["extra"] = ["stairwell"]
    res = gate(banlist=b)
    assert res.code == 2
    assert "banlist.entries" in failures(res)


def test_declaring_an_extra_can_only_tighten_the_lint(run, gate, references, tmp_path,
                                                      example_markdown):
    """The field is safe to honour in exactly one direction: every --extra entry
    is tier ban, so replaying the user's prohibitions holds the draft to more
    than the deck asks and never to less."""
    res = run("banlist.py", "--topic", "a machine that separates emotion from voice",
              "--obvious", str(references / "example-obvious.txt"), "--extra", "stairwell",
              "--out", str(tmp_path))
    assert res.code == 0, res
    import json as _json
    b = _json.loads((tmp_path / "banlist.json").read_text(encoding="utf-8"))
    assert gate(banlist=b, markdown=example_markdown).code == 0
    tightened = gate(banlist=b, markdown=example_markdown + "\n\nA stairwell, then.\n")
    assert tightened.code == 2
    assert "banned material 'stairwell'" in failures(tightened)


def test_a_ban_list_with_no_extra_key_still_replays(gate, references):
    """Files written before the field existed carry no user prohibitions, which
    is the same as carrying none."""
    b = example_banlist(references)
    del b["extra"]
    assert gate(banlist=b).code == 0
