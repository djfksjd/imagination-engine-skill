"""Shared fixtures. Offline by construction: the scripts make no network calls
and read nothing outside the repository, so the suite runs anywhere."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "imagination-engine"
SCRIPTS = SKILL / "scripts"
REFERENCES = SKILL / "references"
DECKS = REFERENCES / "decks"


class Result:
    def __init__(self, proc: subprocess.CompletedProcess[str]):
        self.code = proc.returncode
        self.out = proc.stdout
        self.err = proc.stderr

    def json(self):
        return json.loads(self.out)

    def __repr__(self) -> str:  # pragma: no cover - only used on failure
        return f"Result(code={self.code}, out={self.out[:400]!r}, err={self.err[:400]!r})"


@pytest.fixture(scope="session")
def repo() -> Path:
    return REPO


@pytest.fixture(scope="session")
def references() -> Path:
    return REFERENCES


@pytest.fixture(scope="session")
def decks() -> dict:
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in DECKS.glob("*.json")}


@pytest.fixture
def run():
    def _run(script: str, *args: str, stdin: str | None = None) -> Result:
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / script), *args],
            input=stdin,
            capture_output=True,
            text=True,
        )
        return Result(proc)

    return _run


@pytest.fixture
def obvious_file(tmp_path: Path) -> Path:
    path = tmp_path / "obvious.txt"
    path.write_text(
        "\n".join(
            [
                "headset that strips feeling",
                "emotion filter for calls",
                "feelings stored in vials",
                "flat robotic voice",
                "company selling emotional privacy",
                "government mandate",
                "feelings shown as colour",
                "therapy machine for grief",
                "- singer who loses feeling",
                "1. black market for emotions",
                "a very long entry that describes an entire premise in more words than any lint could usefully match",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return path


@pytest.fixture
def banlist(tmp_path: Path, run, obvious_file: Path) -> Path:
    res = run("banlist.py", "--topic", "voice", "--obvious", str(obvious_file), "--out", str(tmp_path))
    assert res.code == 0, res
    return tmp_path / "banlist.json"
