"""The lint is a floor, not a ceiling: it proves specific familiar moves are
absent and claims nothing more. These tests cover both directions - it must fire
on disguised variants, and it must not fire on innocent words that happen to
contain a banned string."""

from __future__ import annotations

import pytest


def draft(tmp_path, text):
    path = tmp_path / "draft.md"
    path.write_text(text, encoding="utf-8")
    return str(path)


def test_clean_draft_passes(run, tmp_path, banlist):
    path = draft(tmp_path, "A grade forms wherever a sentence is repeated, and the charge settles on the plaster.\n")
    res = run("cliche_lint.py", "--banlist", str(banlist), "--draft", path)
    assert res.code == 0, res
    assert "PASSED the mechanical check" in res.out


def test_banned_phrase_fails_with_code_3(run, tmp_path, banlist):
    path = draft(tmp_path, "The city is a cyberpunk sprawl.\n")
    res = run("cliche_lint.py", "--banlist", str(banlist), "--draft", path)
    assert res.code == 3
    assert "cyberpunk" in res.out


def test_hyphen_and_plural_variants_are_caught(run, tmp_path, banlist):
    path = draft(tmp_path, "Neon  Lights everywhere.\nThe holograms shimmer.\n")
    res = run("cliche_lint.py", "--banlist", str(banlist), "--draft", path, "--json")
    assert res.code == 3
    ids = {f["id"] for f in res.json()["findings"]}
    assert {"neon-lights", "hologram"} <= ids


def test_word_boundaries_prevent_false_positives(run, tmp_path, banlist):
    path = draft(tmp_path, "They met in a restaurant near the auratic archive of Auralia.\n")
    res = run("cliche_lint.py", "--banlist", str(banlist), "--draft", path, "--json")
    assert res.code == 0, res.out
    assert res.json()["findings"] == []


def test_first_instincts_from_the_dump_are_enforced(run, tmp_path, banlist):
    path = draft(tmp_path, "At its centre is a headset that strips feeling.\n")
    res = run("cliche_lint.py", "--banlist", str(banlist), "--draft", path, "--json")
    assert res.code == 3
    assert any(f["source"] == "obvious-dump" for f in res.json()["findings"])


def test_structural_pitch_patterns_fail(run, tmp_path, banlist):
    path = draft(tmp_path, "It is a cross between a lighthouse and a debt.\n")
    res = run("cliche_lint.py", "--banlist", str(banlist), "--draft", path, "--json")
    assert res.code == 3
    kinds = {(f["kind"], f["id"]) for f in res.json()["findings"]}
    assert ("pattern", "cross-between") in kinds


def test_hollow_adjectives_fail(run, tmp_path, banlist):
    path = draft(tmp_path, "An innovative and futuristic organism.\n")
    res = run("cliche_lint.py", "--banlist", str(banlist), "--draft", path, "--json")
    assert res.code == 3
    ids = {f["id"] for f in res.json()["findings"]}
    assert {"hollow-innovative", "hollow-futuristic"} <= ids


def test_warnings_do_not_fail_unless_strict(run, tmp_path, banlist):
    path = draft(tmp_path, "The chamber has an eerie stillness.\n")
    ok = run("cliche_lint.py", "--banlist", str(banlist), "--draft", path)
    assert ok.code == 0
    strict = run("cliche_lint.py", "--banlist", str(banlist), "--draft", path, "--strict")
    assert strict.code == 3


def test_allow_suppresses_a_finding(run, tmp_path, banlist):
    path = draft(tmp_path, "A cyberpunk street, as requested.\n")
    res = run("cliche_lint.py", "--banlist", str(banlist), "--draft", path, "--allow", "cyberpunk")
    assert res.code == 0, res


def test_manual_checks_are_reported(run, tmp_path, banlist):
    path = draft(tmp_path, "Nothing objectionable here.\n")
    res = run("cliche_lint.py", "--banlist", str(banlist), "--draft", path)
    assert "MANUAL CHECKS" in res.out


def test_deck_only_mode_without_a_banlist(run, tmp_path):
    path = draft(tmp_path, "A dystopian corridor.\n")
    res = run("cliche_lint.py", "--deck-only", "--draft", path)
    assert res.code == 3


def test_missing_banlist_argument_is_a_usage_error(run, tmp_path):
    path = draft(tmp_path, "text\n")
    res = run("cliche_lint.py", "--draft", path)
    assert res.code == 1
    assert "--deck-only" in res.err


def test_line_numbers_are_reported(run, tmp_path, banlist):
    path = draft(tmp_path, "clean line\nclean line\nthe hologram flickers\n")
    res = run("cliche_lint.py", "--banlist", str(banlist), "--draft", path, "--json")
    assert res.json()["findings"][0]["line"] == 3


def test_the_shipped_example_passes_its_own_lint(run, references, tmp_path):
    import json

    candidate = json.loads((references / "example-candidate.json").read_text(encoding="utf-8"))
    path = draft(tmp_path, "\n".join(candidate["sections"].values()))
    res = run("cliche_lint.py", "--deck-only", "--draft", path, "--strict")
    assert res.code == 0, res.out


# ------------------------------- the deck must not ban ordinary English

ORDINARY_PROSE = [
    "The committee meets each Tuesday in the west room.",
    "Where fresh water meets salt water the silt drops out.",
    "The family meets once a year to wash the stones.",
    "Where the congregation meets on Sundays the floor is cold.",
    "The group meets in this room or the tokens are gone forever.",
    "A door meets its frame and the sound changes.",
    "The children cross between the courtyards after lunch.",
    "Her answer carries a mix of fear and relief.",
    "The rite is a blend of two older customs nobody remembers separately.",
    "The same procession, but with magic, would be a different rite entirely.",
    "The matrix of obligations between the four households is the mechanic.",
]

PITCHES = [
    "It is Alien meets Jaws.",
    "Think of it as Tetris meets grief.",
    "This is architecture meets liturgy.",
    "It's kind of like Minecraft meets probate.",
    "It is a cross between a lighthouse and a debt.",
    "But with AI it would ship next quarter.",
]


@pytest.mark.parametrize("line", ORDINARY_PROSE)
def test_ordinary_prose_is_not_banned(run, tmp_path, banlist, line):
    """The engine advertises story seeds, rituals, worlds and mechanics, and the
    bundled deck was banning the English those briefs are written in: 'meets' is
    a verb, 'cross between' is a verb, 'a mix of fear and relief' is how the
    affect section is ordinarily written. The gate's advice on a ban - 'rewrite
    the thought, not the word' - is actively wrong when there is no thought
    there, because deleting the word is the only available fix."""
    path = draft(tmp_path, line + "\n")
    res = run("cliche_lint.py", "--banlist", str(banlist), "--draft", path, "--json")
    bans = [f for f in res.json()["findings"] if f["tier"] == "ban"]
    assert bans == [], f"ordinary prose banned: {bans}"
    assert res.code == 0


@pytest.mark.parametrize("line", PITCHES)
def test_the_pitch_frame_is_still_banned(run, tmp_path, banlist, line):
    """Narrowing is not deleting. The frame the rules exist for still fails."""
    path = draft(tmp_path, line + "\n")
    res = run("cliche_lint.py", "--banlist", str(banlist), "--draft", path, "--json")
    assert res.code == 3, res.out
