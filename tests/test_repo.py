import json
import re
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO / "skills" / "imagination-engine"
SKILL = SKILL_DIR / "SKILL.md"
VERSION = "0.5.2"
README_NAMES = {
    "README.md",
    "README.ko.md",
    "README.ja.md",
    "README.zh-CN.md",
    "README.es.md",
    "README.fr.md",
    "README.de.md",
    "README.pt-BR.md",
}


def test_root_skill_symlink_resolves_to_runtime_skill():
    root = REPO / "SKILL.md"
    assert root.is_symlink()
    assert root.resolve() == SKILL.resolve()


def test_runtime_skill_is_small_and_markdown_only():
    text = SKILL.read_text(encoding="utf-8")
    assert len(text.splitlines()) <= 180
    assert len(text.split()) <= 1_800
    assert not (SKILL_DIR / "scripts").exists()
    assert not (SKILL_DIR / "references").exists()
    assert sorted(
        path.relative_to(SKILL_DIR).as_posix()
        for path in SKILL_DIR.rglob("*")
        if path.is_file()
    ) == ["SKILL.md", "agents/openai.yaml"]


def test_frontmatter_has_only_name_and_description():
    text = SKILL.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    assert match
    keys = [
        line.split(":", 1)[0].strip()
        for line in match.group(1).splitlines()
        if ":" in line
    ]
    assert keys == ["name", "description"]
    assert "name: imagination-engine" in match.group(1)
    assert "explicitly invokes" in match.group(1)


def test_implicit_invocation_stays_disabled_during_incubation():
    metadata = (SKILL_DIR / "agents" / "openai.yaml").read_text(encoding="utf-8")
    assert "allow_implicit_invocation: false" in metadata
    assert "$imagination-engine" in metadata


def test_runtime_requires_private_survivor_proof():
    text = SKILL.read_text(encoding="utf-8")
    assert "## Prove each survivor" in text
    assert "**Constraint evidence:**" in text
    assert "**Causal chain:**" in text
    assert "**First encounter:**" in text
    assert "Keep these cards private" in text


def test_versions_and_descriptions_are_synchronized():
    manifests = [
        REPO / "plugin.json",
        REPO / ".claude-plugin" / "plugin.json",
        REPO / ".codex-plugin" / "plugin.json",
    ]
    for path in manifests:
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["version"] == VERSION
        description = data["description"].lower()
        assert "ban list" not in description
        assert "hash-seeded" not in description
        assert "fail-closed" not in description


def test_readmes_cover_all_supported_languages():
    actual = {path.name for path in REPO.glob("README*.md")}
    assert README_NAMES <= actual

    for name in README_NAMES:
        text = (REPO / name).read_text(encoding="utf-8")
        assert all(f"]({target})" in text for target in README_NAMES)
        assert "0.5.2" in text
        assert "25" in text


def test_development_briefs_are_unique_and_actionable():
    rows = [
        json.loads(line)
        for line in (REPO / "evals" / "briefs.dev.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    assert len(rows) >= 12
    assert len({row["id"] for row in rows}) == len(rows)
    assert all(len(row["prompt"]) >= 100 for row in rows)
    assert {row["language"] for row in rows} >= {"en", "ko"}


def test_legacy_pipeline_is_preserved_outside_runtime():
    legacy = REPO / "legacy" / "v0.4.0"
    assert (legacy / "SKILL.md").exists()
    assert (legacy / "scripts" / "score_gate.py").exists()
    assert (legacy / "references" / "rubric.json").exists()
    assert len(list((legacy / "tests").glob("test_*.py"))) >= 7
