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
    assert payload["counts"]["obvious_supplied"] == 11


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
    lines = ["flat robotic voice", "Flat  Robotic Voice", "- flat robotic voice"] + [f"idea number {i}" for i in range(9)]
    dump.write_text("\n".join(lines) + "\n", encoding="utf-8")
    res = run("banlist.py", "--topic", "voice", "--obvious", str(dump), "--out", str(tmp_path))
    assert res.code == 0
    payload = load(tmp_path / "banlist.json")
    assert payload["counts"]["obvious_supplied"] == 10


def test_stdin_input(run, tmp_path):
    dump = "\n".join(f"obvious idea {i}" for i in range(10))
    res = run("banlist.py", "--topic", "voice", "--obvious", "-", "--out", str(tmp_path), stdin=dump)
    assert res.code == 0, res
