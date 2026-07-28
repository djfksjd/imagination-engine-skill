"""Repository-level invariants: version sync across manifests, the docs the
skill points at actually existing, and the README language set staying
cross-linked. These are the failures nobody notices until a user hits them."""

from __future__ import annotations

import json
import re

import pytest

LANGUAGES = {
    "README.md": "English",
    "README.ko.md": "한국어",
    "README.ja.md": "日本語",
    "README.zh-CN.md": "简体中文",
    "README.es.md": "Español",
    "README.fr.md": "Français",
    "README.de.md": "Deutsch",
    "README.pt-BR.md": "Português",
}

MANIFESTS = ("plugin.json", ".claude-plugin/plugin.json", ".codex-plugin/plugin.json")


def read_json(repo, rel):
    return json.loads((repo / rel).read_text(encoding="utf-8"))


def engine_version(repo) -> str:
    text = (repo / "skills" / "imagination-engine" / "scripts" / "engine.py").read_text(encoding="utf-8")
    match = re.search(r'^VERSION = "([^"]+)"', text, re.MULTILINE)
    assert match, "engine.py has no VERSION"
    return match.group(1)


@pytest.mark.parametrize("manifest", MANIFESTS)
def test_manifest_versions_match_engine(repo, manifest, decks):
    version = engine_version(repo)
    assert read_json(repo, manifest)["version"] == version, f"{manifest} version drifted"


def test_deck_versions_match_engine(repo, decks):
    version = engine_version(repo)
    for name, deck in decks.items():
        assert deck["version"] == version, f"deck {name} version drifted"
    rubric = read_json(repo, "skills/imagination-engine/references/rubric.json")
    assert rubric["version"] == version


@pytest.mark.parametrize("manifest", MANIFESTS)
def test_manifest_names_match_the_skill(repo, manifest):
    assert read_json(repo, manifest)["name"] == "imagination-engine"


def test_marketplace_lists_the_plugin(repo):
    market = read_json(repo, ".claude-plugin/marketplace.json")
    names = [p["name"] for p in market["plugins"]]
    assert names == ["imagination-engine"]


def test_root_skill_md_symlink_resolves(repo):
    root = repo / "SKILL.md"
    assert root.is_symlink(), "root SKILL.md should be a symlink to the skill body"
    assert root.resolve() == (repo / "skills" / "imagination-engine" / "SKILL.md").resolve()


def test_skill_frontmatter(repo):
    text = (repo / "skills" / "imagination-engine" / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---\n")
    front = text.split("---", 2)[1]
    assert re.search(r"^name: imagination-engine$", front, re.MULTILINE)
    description = re.search(r'^description: "(.+)"$', front, re.MULTILINE)
    assert description, "description must be a single quoted line"
    assert len(description.group(1)) < 1024


def test_referenced_files_exist(repo):
    skill_dir = repo / "skills" / "imagination-engine"
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    for rel in re.findall(r"`(references/[\w./-]+)`", text):
        target = skill_dir / rel
        assert target.exists(), f"SKILL.md points at missing {rel}"
    for script in re.findall(r"`(scripts/\w+\.py)`", text):
        assert (skill_dir / script).exists(), f"SKILL.md points at missing {script}"


@pytest.mark.parametrize("filename", sorted(LANGUAGES))
def test_every_readme_links_to_every_other(repo, filename):
    text = (repo / filename).read_text(encoding="utf-8")
    for other, label in LANGUAGES.items():
        if other == filename:
            assert f"**{label}**" in text, f"{filename} does not mark itself as the current language"
        else:
            assert f"({other})" in text, f"{filename} is missing the link to {other}"


@pytest.mark.parametrize("filename", sorted(LANGUAGES))
def test_readmes_reference_only_supported_hosts(repo, filename):
    text = (repo / filename).read_text(encoding="utf-8").lower()
    for removed in ("antigravity", "gemini", "cursor", "grok"):
        assert removed not in text, f"{filename} still mentions an unsupported host: {removed}"
    assert "claude code" in text and "codex" in text


def test_install_script_targets_both_hosts(repo):
    text = (repo / "install.sh").read_text(encoding="utf-8")
    assert "claude plugin install imagination-engine@djfksjd" in text
    assert "codex plugin add imagination-engine@djfksjd" in text
    assert "djfksjd/imagination-engine-skill" in text


def test_the_worked_example_shows_the_draft_that_was_gated(references):
    """Its delivered answer used to carry no bindings at all, so a reader who
    copied it got eight bind-block failures from the gate."""
    draft = (references / "example-draft.md").read_text(encoding="utf-8").strip()
    example = (references / "worked-example.md").read_text(encoding="utf-8")
    assert draft in example, "worked-example.md has drifted from the draft it gates"


def test_the_worked_example_calls_the_one_gate_with_all_four_artefacts(references):
    """It taught the pre-merge two-gate invocation, which now exits 1."""
    text = (references / "worked-example.md").read_text(encoding="utf-8")
    blocks = [b for b in re.findall(r"```bash\n(.*?)```", text, re.S) if "score_gate.py" in b]
    assert blocks, "the worked example never runs the gate"
    for block in blocks:
        for flag in ("--candidate", "--draw", "--banlist", "--markdown"):
            assert flag in block, f"the gate is invoked without {flag}"


def test_the_worked_examples_artefacts_are_the_shipped_ones(references):
    text = (references / "worked-example.md").read_text(encoding="utf-8")
    for name in ("example-obvious.txt", "example-banlist.json", "example-draw.json",
                 "example-candidate.json", "example-draft.md"):
        assert name in text, f"the worked example does not say where {name} fits"


def test_worked_example_matches_the_shipped_candidate(repo, references):
    candidate = json.loads((references / "example-candidate.json").read_text(encoding="utf-8"))
    example = (references / "worked-example.md").read_text(encoding="utf-8")
    assert candidate["sections"]["name"] in example
    for domain in candidate["domains_used"]:
        assert domain["id"] in example or domain["id"].replace("-", " ") in example
