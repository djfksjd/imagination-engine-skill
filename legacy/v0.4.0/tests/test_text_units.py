"""The measurement every length floor in this skill shares.

`text_units` is the one place a "how long is this" question is answered, so a
mistake in it is a mistake in every floor at once. Two mistakes were possible
and this repo and its sibling had one each: dropping combining marks holds the
scripts that write vowels as marks to roughly double the floor, and counting
marks without a per-base cap lets a run of stacked accents pad past any floor.
The tests below pin the union - marks count, capped per base, and the cap does
not reset on punctuation or whitespace.
"""

from __future__ import annotations

import sys
import unicodedata
from copy import deepcopy
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent /
                       "skills" / "imagination-engine" / "scripts"))

from engine import text_units  # noqa: E402

MIN_JUSTIFICATION = 40

# Natural sentences, one per script, each comfortably past the 40-unit floor the
# scored justifications carry. The point is not the exact number; it is that the
# number tracks the amount of argument rather than the script it is written in.
SAMPLES = {
    "devanagari": "हिन्दी में मात्राएँ और चिह्न ध्वनि तथा अर्थ को सूक्ष्म रूप से बदलते हैं और यह अंतर मायने रखता है",
    "hebrew": "בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ וְהָאָרֶץ הָיְתָה תֹהוּ",
    "thai": "ภาษาไทยมีสระและวรรณยุกต์ที่ซับซ้อนและเสียงวรรณยุกต์เปลี่ยนความหมายของคำ",
    "arabic": "اللُّغَةُ العَرَبِيَّةُ جَمِيلَةٌ وَالحَرَكَاتُ تُغَيِّرُ المَعنَى تَغيِيرًا كَامِلًا",
    "korean": "소리는 남고 뜻은 사라진다 그리고 남은 소리가 방을 다시 만든다",
    "japanese": "音だけが残り意味が消えるとき部屋の使い方が静かに変わっていく",
    "chinese": "声音留下而意义消失之后房间的用法也随之改变了很多",
    "latin": "the sound stays in the room and the meaning is what leaves it first",
}


def content_code_points(text: str) -> int:
    """Letters, digits and marks: what the reader would call the characters of
    the sentence. Spaces and punctuation are excluded because they never counted
    in any version of the measurement."""
    return sum(1 for ch in text if unicodedata.category(ch)[0] in ("L", "N", "M"))


@pytest.mark.parametrize("script", sorted(SAMPLES))
def test_a_mark_bearing_script_is_not_held_to_a_double_floor(script):
    """Stripping every Mn/Mc/Me mark read a 56-code-point Devanagari sentence as
    27 units. An author writing the same argument in Hindi, Hebrew or Thai had to
    write roughly twice as much of it to clear the same floor. The residual loss
    is the per-base cap, which a base carrying three marks does run into - it is
    a few percent, not a factor of two, and it is the price of the padding
    defence."""
    sample = SAMPLES[script]
    assert text_units(sample) >= content_code_points(sample) * 0.9, (
        f"{script} loses more than a tenth of its characters to the measurement"
    )


def longest_prefix_below(text: str, floor: int) -> str:
    out = ""
    for ch in text:
        if text_units(out + ch) >= floor:
            break
        out += ch
    return out


def shortest_prefix_at(text: str, floor: int) -> str:
    out = ""
    for ch in text:
        out += ch
        if text_units(out) >= floor:
            return out
    raise AssertionError("sample never reaches the floor")


@pytest.mark.parametrize("script", sorted(SAMPLES))
def test_the_floor_lands_where_the_measurement_says_it_does(gate, example_candidate, script):
    """At the floor and one unit below it, in every script the skill claims to
    work in. `scores.*.justification` carries the 40-unit floor."""
    sample = SAMPLES[script]
    below = longest_prefix_below(sample, MIN_JUSTIFICATION)
    at = shortest_prefix_at(sample, MIN_JUSTIFICATION)
    assert text_units(below) < MIN_JUSTIFICATION <= text_units(at)

    short = deepcopy(example_candidate)
    short["scores"]["imageability"]["justification"] = below
    res = gate(candidate=short)
    assert res.code == 2, f"{script}: {text_units(below)} units cleared a {MIN_JUSTIFICATION} floor"
    assert "scores.imageability.justification" in " ".join(res.json()["failures"])

    long_enough = deepcopy(example_candidate)
    long_enough["scores"]["imageability"]["justification"] = at
    res = gate(candidate=long_enough)
    assert res.code == 0, (
        f"{script}: {text_units(at)} units failed a {MIN_JUSTIFICATION} floor - {res.out}")


def test_stacked_marks_cannot_pad_a_floor():
    """The sibling repo's cap reset on any non-mark, so two accents after every
    dot bought two units each: 370 code points of dots and accents measured 251
    and cleared a 250-unit floor. The cap here belongs to the base character and
    punctuation does not open a new one."""
    padded = "Nurse" + (".́̂" * 120) + "waits"
    plain = "Nurse" + ("." * 360) + "waits"
    assert text_units(plain) == 10
    assert text_units(padded) <= 12, "a run of stacked marks bought units"


def test_a_mark_run_on_one_base_is_capped():
    assert text_units("a" + "́" * 50) == 3


def test_punctuation_and_whitespace_never_count():
    assert text_units(" " * 200) == 0
    assert text_units("." * 400) == 0
    assert text_units("　" * 200) == 0
    assert text_units("\U0001f30a" * 40) == 0


def test_a_mark_with_no_content_base_counts_nothing():
    """Marks are counted because they are carrying a vowel or a tone on a
    letter. A mark with no letter under it is decoration."""
    assert text_units("́" * 40) == 0
    assert text_units("..." + "́" * 40) == 0
