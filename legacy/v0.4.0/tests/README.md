# tests

Offline pytest suite. Run from the repository root:

```bash
python3 -m pytest tests/ -q
```

The scripts under test use only the Python 3 standard library and make no
network calls, so nothing is stubbed and no fixtures beyond the repository
itself are needed. Each test invokes a script as a subprocess, which means exit
codes — the contract the skill actually depends on — are covered directly
rather than approximated.

| File | Covers |
|---|---|
| `test_decks.py` | Deck integrity: unique ids, declared and populated categories, probe questions, replacement-law requirements, valid cliché regexes, rubric ↔ schema agreement |
| `test_draw.py` | The draw is deterministic for a given topic, spans disjoint categories, deals fresh material on later runs, honours mode forcing and extremal widening, and fails loudly on bad arguments |
| `test_banlist.py` | The short-instinct-dump refusal (exit 2), bullet stripping, deduplication, long entries becoming manual checks, `--allow` and `--extra` |
| `test_cliche_lint.py` | Detection of disguised variants (plurals, hyphens, casing), absence of false positives on innocent words, structural pitch patterns, strict mode, and the shipped example passing its own lint |
| `test_score_gate.py` | Every way the required work can be skipped: thin sections, missing replacement law, decorative domains, absent `resembles`, thin justifications, out-of-range or uniform scores, extremal thresholds |
| `test_repo.py` | Version sync across manifests and decks, the root `SKILL.md` symlink, referenced files existing, and the eight READMEs staying cross-linked and host-accurate |

`conftest.py` holds the subprocess `run` helper plus the shared instinct-dump
and ban-list fixtures.
