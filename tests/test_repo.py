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


@pytest.mark.parametrize("filename", sorted(set(LANGUAGES) - {"README.md"}))
def test_translations_name_the_same_flags_as_the_english(repo, filename):
    """All seven kept a sentence about --extremal/--grounded that the English
    had deleted, and that contradicted their own page eleven lines later."""
    def flags(name):
        return set(re.findall(r"--[a-z-]+", (repo / name).read_text(encoding="utf-8")))
    english = flags("README.md")
    theirs = flags(filename)
    assert theirs - english == set(), f"{filename} names flags the English does not"
    assert english - theirs == set(), f"{filename} is missing flags the English names"

    # The stale sentence lived in the --list-modes paragraph, where it told the
    # reader to pass flags that the same page says a few lines later do not exist.
    for text in ((repo / filename).read_text(encoding="utf-8"),):
        for para in text.split("\n\n"):
            if "--list-modes" not in para:
                continue
            assert "--extremal" not in para and "--grounded" not in para, (
                f"{filename} still tells the reader about deleted gate flags")


@pytest.mark.parametrize("filename", sorted(LANGUAGES))
def test_the_manual_pipeline_is_runnable_in_every_language(repo, filename):
    """It said the scripts live under skills/imagination-engine/scripts/ and then
    invoked python3 scripts/draw.py, which from the repo root exits 2 - the same
    code the page's own table defines as the gate failing. Three of its inputs
    appeared from nowhere while the repo shipped a finished version of each."""
    text = (repo / filename).read_text(encoding="utf-8")
    assert "cd skills/imagination-engine" in text, "no working directory is stated"
    for name in ("example-obvious.txt", "example-banlist.json", "example-draw.json",
                 "example-candidate.json", "example-draft.md"):
        assert name in text, f"{filename} never says where {name} fits"
    blocks = [b for b in re.findall(r"```bash\n(.*?)```", text, re.S) if "score_gate.py" in b]
    assert blocks, "the pipeline never reaches the gate"
    for block in blocks:
        for flag in ("--candidate", "--draw", "--banlist", "--markdown"):
            assert flag in block, f"{filename} invokes the gate without {flag}"


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


BIND = re.compile(r"<!--\s*bind:\s*([A-Za-z0-9_.\[\]]+)\s*-->(.*?)<!--\s*/bind\s*-->", re.S)


def test_output_template_bind_blocks_satisfy_the_gates_required_sections(
    references, example_candidate, gate
):
    """SKILL.md step 8 tells the user to write draft.md "per that template", so a
    reader who does exactly that and nothing else has to end up with a draft the
    gate accepts. Build that draft mechanically: take the delivered-contract body
    of output-template.md (everything the two `---` rules bracket off from the
    explanatory prose above and below it), and drop the shipped candidate's own
    section text into whatever bind blocks the template itself shows. A section
    the template never wraps in a bind block is a section this draft never binds
    either - which is exactly what a user copying only the template would produce.

    The template used to carry a bind block for `first_encounter` alone, so this
    reproduced eight "no bind block" failures before the fix.
    """
    template = (references / "output-template.md").read_text(encoding="utf-8")
    parts = template.split("---")
    assert len(parts) == 3, "expected exactly two --- rules bracketing the delivered contract"
    body = "---".join(parts[1:])

    sections = example_candidate["sections"]  # anchor 1, non-grounded: no operational_path

    def fill(match: re.Match[str]) -> str:
        key = match.group(1)
        section_id = key.split(".", 1)[1]
        text = sections.get(section_id)
        if text is None:
            return ""  # naive user leaves out the conditional section, as instructed
        return f"<!-- bind: {key} -->{text}<!-- /bind -->"

    draft = BIND.sub(fill, body)
    res = gate(markdown=draft)
    failures = res.json()["failures"]
    missing_binds = [f for f in failures if "no <!-- bind:" in f]
    assert missing_binds == [], (
        "a draft built strictly from output-template.md's own bind-block structure "
        f"is missing required binds the gate demands: {missing_binds}"
    )
