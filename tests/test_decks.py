"""Deck integrity. A corrupt deck degrades every run silently - a missing
category or a duplicated id would quietly reduce the distance guarantee that
the whole pipeline rests on."""

from __future__ import annotations

import json
import re

import pytest

DECK_ITEM_KEY = {
    "domains": "domains",
    "constraints": "constraints",
    "senses": "senses",
    "perspectives": "perspectives",
    "affects": "pairs",
    "modes": "modes",
}
MIN_SIZE = {
    "domains": 60,
    "constraints": 20,
    "senses": 15,
    "perspectives": 12,
    "affects": 10,
    "modes": 5,
}


def test_all_decks_present(decks):
    assert set(decks) == {"domains", "constraints", "senses", "perspectives", "affects", "modes", "cliches"}


@pytest.mark.parametrize("name", sorted(DECK_ITEM_KEY))
def test_ids_unique_and_deck_large_enough(decks, name):
    items = decks[name][DECK_ITEM_KEY[name]]
    ids = [i["id"] for i in items]
    assert len(ids) == len(set(ids)), f"{name} has duplicate ids"
    assert len(items) >= MIN_SIZE[name], f"{name} shrank below its working minimum"


def test_domain_categories_are_declared_and_populated(decks):
    domains = decks["domains"]
    declared = {c["id"] for c in domains["categories"]}
    used = {d["category"] for d in domains["domains"]}
    assert used <= declared, f"undeclared categories: {used - declared}"
    assert declared == used, f"empty categories: {declared - used}"
    assert len(declared) >= 10, "fewer than 10 categories weakens the disjointness guarantee"


def test_every_domain_has_a_probe_question(decks):
    for d in decks["domains"]["domains"]:
        assert d["probe"].endswith("?"), f"{d['id']} probe is not a question"


def test_constraints_demand_a_replacement_law(decks):
    for c in decks["constraints"]["constraints"]:
        assert c["statement"] and c["inversion_prompt"]
        assert len(c["replacement_requirement"]) > 20, f"{c['id']} does not demand a real replacement law"


def test_mode_forces_reference_real_decks(decks):
    known = set(decks)
    categories = {c["id"] for c in decks["domains"]["categories"]}
    for mode in decks["modes"]["modes"]:
        for force in mode["forces"]:
            deck, _, cat = force.partition(":")
            assert deck in known, f"{mode['id']} forces unknown deck {deck}"
            if cat:
                assert cat in categories, f"{mode['id']} forces unknown category {cat}"
        assert mode["directives"] and mode["guard"]


def test_default_modes_exist(decks):
    ids = {m["id"] for m in decks["modes"]["modes"]}
    assert set(decks["modes"]["default_modes"]) <= ids


def test_anchor_levels_are_contiguous(decks):
    levels = sorted(a["level"] for a in decks["modes"]["anchors"])
    assert levels == list(range(len(levels)))


def test_cliche_tiers_and_regexes(decks):
    cliches = decks["cliches"]
    for p in cliches["phrases"]:
        assert p["tier"] in {"ban", "warn"}
        assert p["phrase"].strip()
    for pattern in cliches["structural_patterns"]:
        re.compile(pattern["regex"])  # raises on a malformed deck
        assert pattern["tier"] in {"ban", "warn"}
        assert pattern["why"]
    overlap = set(cliches["hollow_adjectives"]["ban"]) & set(cliches["hollow_adjectives"]["warn"])
    assert not overlap, f"adjective in both tiers: {overlap}"
    assert len(cliches["moves"]) >= 8


def test_rubric_matches_schema(references):
    rubric = json.loads((references / "rubric.json").read_text(encoding="utf-8"))
    schema = json.loads((references / "candidate.schema.json").read_text(encoding="utf-8"))
    axes = [a["id"] for a in rubric["axes"]]
    assert len(axes) == 8 and len(set(axes)) == 8
    assert set(schema["properties"]["scores"]["required"]) == set(axes)
    sections = [s["id"] for s in rubric["required_sections"]]
    conditional = {rubric["grounded_substitution"]["requires_section"]}
    assert set(schema["properties"]["sections"]["required"]) == set(sections) - conditional
    assert conditional <= set(schema["properties"]["sections"]["properties"])
    for spec, prop in ((s, schema["properties"]["sections"]["properties"][s["id"]]) for s in rubric["required_sections"]):
        if "min_units" not in spec:
            continue  # 'name' is checked for being a placeholder, not for length
        # The schema floor must never reject what the gate accepts: the gate
        # counts units, so a CJK section clears its floor at about half the
        # code points, and a plain minLength has no way to express that.
        assert prop["minLength"] <= spec["min_units"] / 2 + 1, (
            f"{spec['id']}: schema minLength would reject CJK text the gate accepts")
    assert rubric["extremal_thresholds"]["min_mean"] > rubric["default_thresholds"]["min_mean"]


def test_grounded_substitution_is_coherent(references):
    """grounded asks for a path to something real, which in practice usually
    means something built for someone - and the human-centring axis then scores
    near its floor. Not unsatisfiable in every case, but routinely so, and the
    answer is substitution rather than a waiver: an axis comes out, an axis and
    a required section go in."""
    rubric = json.loads((references / "rubric.json").read_text(encoding="utf-8"))
    sub = rubric["grounded_substitution"]
    axis_ids = {a["id"] for a in rubric["axes"]}
    assert sub["replaces"] in axis_ids
    assert sub["axis"]["id"] not in axis_ids, "the substitute must not also be a default axis"
    assert sub["requires_section"] in {s["id"] for s in rubric["required_sections"]}
