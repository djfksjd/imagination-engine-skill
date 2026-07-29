"""banlist.py exists to make the model's own first instincts unavailable. The
gate that matters here is the short-dump refusal: if stage 1 can be skipped,
nothing downstream is protected."""

from __future__ import annotations

import json

import pytest

from conftest import REFERENCES

REFERENCE_BANLIST = REFERENCES / "example-banlist.json"


# A realistic dump. Not a template with a counter in it: the builder now refuses
# those, because twelve variants of one line are one instinct written twelve
# times - and being short, they all become matchable bans and empty the manual
# checks the long instincts would have produced.
REAL_TWELVE = [
    "headset that strips feeling",
    "emotion filter for calls",
    "feelings stored in vials",
    "flat robotic voice",
    "company selling emotional privacy",
    "government mandate",
    "feelings shown as colour",
    "therapy machine for grief",
    "singer who loses her range",
    "black market for tone",
    "neural implant that mutes affect",
    "a courtroom where recordings are inadmissible because they carry no charge",
]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_builds_from_dump_and_deck(run, tmp_path, obvious_file):
    res = run("banlist.py", "--topic", "voice", "--obvious", str(obvious_file), "--out", str(tmp_path))
    assert res.code == 0, res
    payload = load(tmp_path / "banlist.json")
    ids = {e["id"] for e in payload["entries"]}
    assert "cyberpunk" in ids, "deck defaults missing"
    assert any(i.startswith("obvious-") for i in ids), "first instincts missing"
    assert any(i.startswith("hollow-") for i in ids), "hollow adjectives missing"
    assert payload["counts"]["obvious_supplied"] == 12


def test_short_dump_is_refused_with_code_2(run, tmp_path):
    thin = tmp_path / "thin.txt"
    thin.write_text("one idea\ntwo ideas\n", encoding="utf-8")
    res = run("banlist.py", "--topic", "voice", "--obvious", str(thin), "--out", str(tmp_path))
    assert res.code == 2
    assert "high-probability" in res.err


def test_bullets_and_numbering_are_stripped(run, tmp_path, obvious_file):
    run("banlist.py", "--topic", "voice", "--obvious", str(obvious_file), "--out", str(tmp_path))
    phrases = {e["phrase"] for e in load(tmp_path / "banlist.json")["entries"]}
    assert "singer who loses feeling" in phrases
    assert "black market for emotions" in phrases


def test_an_instinct_that_is_already_a_cliche_stays_a_first_instinct(run, tmp_path, obvious_file):
    """Dedup used to let the deck copy win, which lost one of the twelve. The
    gate counts them, so a lost instinct would fail an honest run."""
    dump = tmp_path / "collides.txt"
    dump.write_text(obvious_file.read_text(encoding="utf-8").replace(
        "headset that strips feeling", "cyberpunk"), encoding="utf-8")
    res = run("banlist.py", "--topic", "voice", "--obvious", str(dump), "--out", str(tmp_path))
    assert res.code == 0, res
    payload = load(tmp_path / "banlist.json")
    instincts = [e for e in payload["entries"] if e["group"] == "first-instinct"]
    assert len(instincts) + payload["counts"]["manual"] == payload["counts"]["obvious_supplied"]
    assert any(e["phrase"] == "cyberpunk" for e in instincts)


def test_long_entries_become_manual_checks(run, tmp_path, obvious_file):
    run("banlist.py", "--topic", "voice", "--obvious", str(obvious_file), "--out", str(tmp_path))
    payload = load(tmp_path / "banlist.json")
    assert payload["counts"]["manual"] == 1
    assert "too long to match literally" in payload["manual_checks"][0]["note"]


def test_extra_phrases_are_banned(run, tmp_path, obvious_file):
    run("banlist.py", "--topic", "voice", "--obvious", str(obvious_file),
        "--extra", "neural scan,emotion meter", "--out", str(tmp_path))
    phrases = {e["phrase"] for e in load(tmp_path / "banlist.json")["entries"]}
    assert {"neural scan", "emotion meter"} <= phrases


def test_allow_releases_a_deck_entry(run, tmp_path, obvious_file):
    run("banlist.py", "--topic", "voice", "--obvious", str(obvious_file),
        "--allow", "cyberpunk", "--out", str(tmp_path))
    payload = load(tmp_path / "banlist.json")
    assert "cyberpunk" not in {e["id"] for e in payload["entries"]}
    assert payload["allowed"] == ["cyberpunk"]


def test_unknown_allow_id_is_an_error(run, tmp_path, obvious_file):
    res = run("banlist.py", "--topic", "voice", "--obvious", str(obvious_file), "--allow", "not-a-thing")
    assert res.code == 1
    assert "unknown cliche id" in res.err


def test_duplicate_instincts_are_collapsed(run, tmp_path):
    dump = tmp_path / "dump.txt"
    lines = ["Flat  Robotic Voice", "- flat robotic voice"] + REAL_TWELVE
    dump.write_text("\n".join(lines) + "\n", encoding="utf-8")
    res = run("banlist.py", "--topic", "voice", "--obvious", str(dump), "--out", str(tmp_path))
    assert res.code == 0
    payload = load(tmp_path / "banlist.json")
    assert payload["counts"]["obvious_supplied"] == 12


def test_stdin_input(run, tmp_path):
    dump = "\n".join(REAL_TWELVE)
    res = run("banlist.py", "--topic", "voice", "--obvious", "-", "--out", str(tmp_path), stdin=dump)
    assert res.code == 0, res


def test_the_burn_cannot_be_declared_complete_with_a_flag(run, tmp_path):
    """--min-obvious was a caller-supplied floor, so `--min-obvious 0` with an
    empty file exited 0: the whole stage skipped with a passing status."""
    empty = tmp_path / "empty.txt"
    empty.write_text("", encoding="utf-8")
    res = run("banlist.py", "--topic", "voice", "--obvious", str(empty), "--min-obvious", "0")
    assert res.code == 1
    assert "unrecognized arguments" in res.err


def test_the_floor_is_the_twelve_the_skill_asks_for(run, tmp_path):
    eleven = tmp_path / "eleven.txt"
    eleven.write_text("\n".join(REAL_TWELVE[:11]), encoding="utf-8")
    res = run("banlist.py", "--topic", "voice", "--obvious", str(eleven), "--out", str(tmp_path))
    assert res.code == 2
    assert "12 are required" in res.err


# ------------------------------- the builder and the gate agree on a phrase

TOPIC = "a machine that separates emotion from voice"


def build(run, tmp_path, lines, *extra_args):
    dump = tmp_path / "roundtrip.txt"
    dump.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return run("banlist.py", "--topic", TOPIC, "--obvious", str(dump),
               "--out", str(tmp_path), *extra_args)


def twelve(replacements: dict[int, str] | None = None) -> list[str]:
    lines = list(REAL_TWELVE)
    for index, text in (replacements or {}).items():
        lines[index] = text
    return lines


def test_a_placeholder_line_is_refused_by_the_builder_not_by_the_gate(run, tmp_path):
    """`is_placeholder` ran at the gate and not at the builder, so a dump whose
    first line was `Untitled` built cleanly at twelve entries, replayed as
    eleven, and was rejected with "build the list with banlist.py" - by the tool
    that had just built it. The refusal belongs where the dump is still open."""
    res = build(run, tmp_path, twelve({0: "Untitled"}))
    assert res.code == 2
    assert "12 are required" in res.err


def test_a_nested_bullet_survives_the_round_trip(run, tmp_path, gate):
    """Bullet stripping is not idempotent. The builder stored
    "- nested instinct" and the gate read "nested instinct", so the two tools
    disagreed about what a phrase is."""
    res = build(run, tmp_path, twelve({0: "- - nested instinct"}))
    assert res.code == 0, res
    payload = load(tmp_path / "banlist.json")
    assert any(e["phrase"] == "- nested instinct" for e in payload["entries"])
    assert gate(banlist=payload).code == 0, "the gate rejected its own sibling's output"


AWKWARD_DUMPS = {
    "nested-bullet": twelve({0: "- - nested instinct"}),
    "numbered": twelve({0: "1) a numbered instinct", 1: "2. another numbered one"}),
    "quoted": twelve({0: '"a quoted instinct"'}),
    "comment-line": twelve() + ["# a note to self that is not an instinct"],
    "blank-lines": twelve() + ["", "  "],
    "duplicate": twelve() + ["the obvious answer number 1"],
    "long-and-short": twelve({
        0: "vial",
        1: "an entire premise spelled out in more words than any lint could usefully match at all"}),
    "non-latin": twelve({0: "감정을 지우는 헤드셋", 1: "声を平らにする機械"}),
    "marked-script": twelve({0: "एक ऐसी मशीन जो आवाज़ से भाव हटाती है"}),
}


@pytest.mark.parametrize("shape", sorted(AWKWARD_DUMPS))
def test_anything_the_builder_accepts_the_gate_accepts(run, tmp_path, gate, shape):
    """The property, not the two instances of it: a file `banlist.py` exits 0 on
    must never be one `score_gate.py` tells the user to build with `banlist.py`.
    A tool that refuses its own sibling's output is worse than one that refuses
    everything, because the advice it gives is the thing that just failed."""
    res = build(run, tmp_path, AWKWARD_DUMPS[shape])
    assert res.code == 0, res
    payload = load(tmp_path / "banlist.json")
    verdict = gate(banlist=payload)
    contract_failures = [
        f for f in verdict.json()["failures"]
        if f.startswith("banlist") or "build the list with banlist.py" in f
    ]
    assert contract_failures == [], f"{shape}: the gate rejected a file the builder wrote"


# --------------------------- twelve variants of one line are not twelve instincts

TEMPLATE_DUMPS = {
    "numbered-throwaway": [f"throwaway instinct {i}" for i in range(1, 13)],
    "obvious-idea-n": [f"obvious idea {i}" for i in range(12)],
    "sentence-template": [f"the obvious answer number {i}" for i in range(1, 13)],
    "one-word-swapped": [f"a machine that {v} the voice" for v in
                         ("flattens", "sharpens", "empties", "fills", "cools", "warms",
                          "slows", "speeds", "hides", "shows", "keeps", "loses")],
}


@pytest.mark.parametrize("shape", sorted(TEMPLATE_DUMPS))
def test_a_template_dump_is_not_twelve_instincts(run, tmp_path, shape):
    """Exact duplicates were closed a round ago and twelve *distinct* throwaways
    walked through: they recompute cleanly, and because they are all short they
    all become matchable bans, so manual_checks comes out empty and the
    obligation to answer the long instincts in writing disappears with it."""
    res = build(run, tmp_path, TEMPLATE_DUMPS[shape])
    assert res.code == 2, res
    assert "one line with a number changed" in res.err


REAL_DUMPS = {
    "shipped": REAL_TWELVE,
    "fiction": [
        "a walled city with a forbidden zone beyond it",
        "a road that ends at a wall of fog",
        "a village that sacrifices one child a year to the thing in the woods",
        "travellers who never return and are never spoken of",
        "a map with a blank space labelled here be monsters",
        "a caravan that must not stop moving after dark",
        "the last inn before the wilderness",
        "a border guarded by an order of monks",
        "nomads who know the way and will not tell",
        "a river that marks the edge of the known",
        "ruins of an older civilisation past the last road",
        "a child who wanders past the boundary and comes back changed",
    ],
    "product": [
        "handover app with structured form", "ward status board",
        "smart whiteboard at the station", "voice memo handover", "checklist app",
        "shift summary dashboard", "tablet at the bedside", "barcode scan for patients",
        "shared notes document", "automated summary from the chart", "handover timer",
        "structured SBAR template",
    ],
}


@pytest.mark.parametrize("shape", sorted(REAL_DUMPS))
def test_a_real_dump_is_not_mistaken_for_a_template(run, tmp_path, shape):
    """The threshold is set where it is because the gap is wide, not because
    half is a principled number: real dumps from three different domains share
    almost no words between entries, and every template tried shares half or
    more on every pair. A check that rejected honest work would cost more than
    the forgery it caught."""
    res = build(run, tmp_path, REAL_DUMPS[shape])
    assert res.code == 0, res


def test_the_gate_refuses_a_template_dump_too(run, tmp_path, gate):
    """The builder and the gate have to agree, or this becomes the round-trip
    break the previous commit fixed. Both refuse; neither refuses the other's
    output."""
    import json as _json
    banlist = _json.loads((REFERENCE_BANLIST).read_text(encoding="utf-8"))
    banlist["entries"] = [e for e in banlist["entries"] if e.get("group") != "first-instinct"] + [
        {"id": f"obvious-{i:02d}", "phrase": f"throwaway instinct {i}", "tier": "ban",
         "group": "first-instinct", "source": "obvious-dump"} for i in range(1, 13)]
    banlist["manual_checks"] = []
    banlist["counts"]["obvious_supplied"] = 12
    res = gate(banlist=banlist)
    assert res.code == 2
    assert "one line with a number changed" in " ".join(res.json()["failures"])
