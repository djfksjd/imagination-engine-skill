# AGENTS.md — imagination-engine

> Shared agent guide, loaded as context by Claude Code and Codex.

## Role

This plugin ships one skill: a radical idea-generation pipeline. The
authoritative document is `skills/imagination-engine/SKILL.md` — workflow, hard
rules, gates and output contract all live there. Follow it whenever the user
asks for something genuinely strange (creature, world, premise, mechanic,
ritual, artifact, concept brief), says the ideas so far are generic or
predictable or "AI-sounding", or asks to escape genre conventions.

Do **not** route ordinary brainstorming, naming, copy work, or factual questions
here. This skill exists for the case where the predictable answer is the
problem; when a conventional answer is what the user needs, say so and answer
normally.

## Dependencies

Python 3 standard library only. No installation, no API keys, no network access.

## Script paths

Scripts live in `skills/imagination-engine/scripts/`.

- Claude Code → `${CLAUDE_PLUGIN_ROOT}/skills/imagination-engine/scripts/`
- Codex → substitute Codex's plugin root. If the variable is unknown, resolve
  the directory containing `SKILL.md` and use absolute paths. For a standalone
  clone that is `<clone>/skills/imagination-engine/scripts/`.
- Each script resolves its decks from its own parent directory
  (`references/decks/`), so it can be invoked from any working directory.
- Write working files (`draw.json`, `banlist.json`, `candidate.json`, drafts)
  into a scratch directory. Never into the skill folder.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | ok |
| 1 | usage or deck error |
| 2 | gate failed — `banlist.py` (instinct dump too short) or `score_gate.py` (rubric) |
| 3 | `cliche_lint.py` found banned material in the draft |

A non-zero exit is never treated as success, and a failed gate means regenerate,
never resubmit with rounded scores.

## Conduct (summary — full text in SKILL.md)

- The internal search stays internal. The user sees the output contract only.
- Never claim that no human or model has thought of this. Name the nearest
  known works and state the difference instead.
- Every broken law is replaced by one that forbids something. Absence is not
  strangeness.
- Cruelty, gore, sexual violence, and degradation of real groups are banned as
  shortcuts to discomfort. Unease comes from the premise.
- Do not narrow the user's request to make it easier. If they need something
  buildable, raise the anchor level rather than softening the premise.
- Reason in English, deliver in the user's language. Section order is fixed;
  headings translate.
