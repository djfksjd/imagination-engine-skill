"""banlist.py exists to make the model's own first instincts unavailable. The
gate that matters here is the short-dump refusal: if stage 1 can be skipped,
nothing downstream is protected."""

from __future__ import annotations

import json


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
    lines = ["flat robotic voice", "Flat  Robotic Voice", "- flat robotic voice"] + [f"idea number {i}" for i in range(11)]
    dump.write_text("\n".join(lines) + "\n", encoding="utf-8")
    res = run("banlist.py", "--topic", "voice", "--obvious", str(dump), "--out", str(tmp_path))
    assert res.code == 0
    payload = load(tmp_path / "banlist.json")
    assert payload["counts"]["obvious_supplied"] == 12


def test_stdin_input(run, tmp_path):
    dump = "\n".join(f"obvious idea {i}" for i in range(12))
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
    eleven.write_text("\n".join(f"obvious idea {i}" for i in range(11)), encoding="utf-8")
    res = run("banlist.py", "--topic", "voice", "--obvious", str(eleven), "--out", str(tmp_path))
    assert res.code == 2
    assert "12 are required" in res.err
