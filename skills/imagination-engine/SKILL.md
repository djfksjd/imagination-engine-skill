---
name: imagination-engine
description: "Radical idea generation that blocks the obvious answer instead of asking for a better one. Use when the user wants something genuinely strange - creature, world, premise, product concept, story seed, mechanic, ritual, form of life - or says the ideas so far are generic, predictable, or 'AI-sounding', or asks to think outside genre conventions. The engine burns its own first instincts into a ban list, deals a hash-seeded hand of distant domains and a reality rule to break, and gates the result on a rubric before it is shown. Works in any language. Not for factual questions, naming, or normal brainstorming where a conventional answer is the correct answer."
---

# Imagination Engine

An idea pipeline built on one observation: a model asked to "be creative" samples
from the most probable continuations of the word *creative*, which is why the
results converge. Instructing harder does not change the distribution. Removing
paths does.

So this skill does not ask for originality. It makes the familiar answers
unavailable - explicitly, in writing, before generation - deals constraints that
the model did not choose, and refuses to output anything that fails a mechanical
check. Every stage below is either a deletion or a gate.

**Working language.** Reason, draw, and gate in English; deliver in whatever
language the user wrote in. The section order of the output contract is fixed;
the headings are translatable.

## Hard rules

1. **Never show the internal search.** Stages 1-7 stay hidden unless the user
   asks for the work. The delivered answer is the output contract, nothing else:
   no preamble, no summary of how hard this was, no offer to make it stranger.
2. **No unverifiable novelty claims.** Never write that no human, no model, or
   no one in history has thought of this. You cannot know it. What you can do is
   name the nearest known works and state the difference, which is required in
   the `resembles` field and in the final section.
3. **Strangeness is structural, not decorative.** If deleting the visual
   description leaves nothing, there was no idea. If deleting the invented
   vocabulary makes it an ordinary thing again, the vocabulary was the disguise.
4. **Broken rules get replaced.** A world where a law is merely absent is empty,
   not strange. Every deletion installs a new law, and the new law must forbid
   something the ordinary world allows. State the impossibility explicitly.
5. **No shock as a substitute.** Cruelty, gore, sexual violence, and degradation
   of real groups are the cheapest available way to make a reader uncomfortable
   and are banned as shortcuts here. Unease must come from the premise. Content
   the user could not use is not a strange result, it is a wasted one.
6. **Do not quietly narrow the request.** If the user needs something buildable,
   raise the anchor level rather than softening the premise. If a genuinely
   strange answer would not serve them, say so in one sentence and give them the
   ordinary answer they need - do not deliver decoration and call it invention.
7. **Honest gates.** A failed gate means regenerate, not resubmit with rounded
   scores. If a run cannot clear the threshold, say that and show the closest
   failure with the reason it failed.

## When not to use this

Factual questions, product naming, copy editing, ordinary brainstorming where
conventional options are what the user needs, and any task where the user has
already chosen a genre and wants competent work inside it. Say so and proceed
normally. This skill is for the case where the predictable answer is the
problem.

## Scripts

Paths are relative to this file's directory. In Claude Code that is
`${CLAUDE_PLUGIN_ROOT}/skills/imagination-engine/`; in Codex, resolve the
directory containing this SKILL.md and use absolute paths. Python 3, standard
library only, no installation.

| Script | Role | Non-zero exit |
|---|---|---|
| `scripts/draw.py` | Deals the constraint hand: distant domains across disjoint categories, a rule to break, a non-human stance, a sense seed, an affect pair | 1 usage/deck error |
| `scripts/banlist.py` | Turns the stage-1 instinct dump plus the cliche deck into a machine-checkable ban list | 2 if the dump is too short |
| `scripts/cliche_lint.py` | Scans the draft for banned phrases, hollow adjectives, and pitch-shaped sentences | 3 if banned material is present |
| `scripts/score_gate.py` | Validates the candidate against the rubric, fail-closed | 2 if the gate fails |

A non-zero exit is never treated as success. Write working files to a scratch
directory, not into the skill folder.

## Modes

Stack up to three. `draw.py --list-modes` prints them; `references/decks/modes.json`
is authoritative.

| Mode | What it removes |
|---|---|
| `baby` | Learned function, correct names, and the order of cause and effect. Infant logic, adult execution - a cute result is a failed one. |
| `nonhuman` | Human benefit. Nothing here is for anyone; if the result is a product, it is disqualified. |
| `alien-physics` | Appearance as the site of novelty. Physics, time, or selfhood changes instead. |
| `affect` | The five senses and the named emotions. Requires an invented sense with all four fields answered. |
| `extremal` | Every safe candidate. Raises thresholds to mean 9.0, no axis below 8. |
| `grounded` | Nothing. Adds one operational path without editing the principle, and swaps one rubric axis (below). Use with anchor 2-3. |

Default when the user does not choose: `nonhuman,alien-physics` at anchor 1.

**Anchors** set how far the result must stay reachable: 0 unbound, 1 legible in
three sentences without analogy, 2 stageable as a concrete scene or artifact,
3 operable with one real path and its stated losses.

## Pipeline

### 0. Intake

Ask only what changes the work, in one short message: the subject; what it is
for (story, world, game mechanic, artifact, concept art brief, nothing);
modes and anchor if the user has a preference; and anything that must be
avoided. If the user gave enough to proceed, do not interrogate them - draw and
go. **Always ask for their own forbidden list if they did not give one**; a
user's "not another X" is the highest-value constraint available and it costs
one sentence to obtain.

### 1. Burn the first instincts (hidden)

Write down the twelve answers most likely to be produced by this prompt - your
own first instincts, phrased as short noun phrases. These are not candidates.
They are the ban list. Then name the *skeleton* they share (in the worked
example: apparatus, operator, stored substance); the skeleton is the real
target, and any later candidate that reinstates it is dead regardless of how
different its surface is.

```bash
scripts/banlist.py --topic "<topic>" --obvious obvious.txt \
  --extra "<user's own prohibitions>" --out <work>
```

Exit 2 means the dump was too short: the familiar answers are still available to
you. Finish it.

### 2. Excavate premises (hidden)

List ten assumptions the request smuggles in, including the ones nobody states
(that it is an object, that it has a user, that it exists in one place, that it
runs forward in time, that it is one of something). Delete or invert at least
three. Record which.

### 3. Deal the hand

```bash
scripts/draw.py --topic "<topic>" --modes <modes> --run 1 --anchor <n> --out <work>
```

The draw is hash-seeded from the topic, so it is reproducible; domains are
guaranteed to span disjoint top-level categories; and `--run 2`, `--run 3` deal
fresh material for regenerations rather than re-rolling your favourites. Change
`--salt` to redeal the same run. Every card is binding. A card that ends up
mentioned but not answering its probe is a decoration - cut it or make it
load-bearing.

### 4. Diverge (hidden)

Twenty candidates in different directions, deliberately including several you
expect to fail. Do not evaluate while generating.

### 5. Cull (hidden)

Discard on sight anything that: reinstates the stage-1 skeleton; is a known work
with new proper nouns; changes only size, colour, material, or scale; combines
two neighbours from one field; is strange only in appearance; needs a
technology that could be swapped for any other technology; or is incoherent
rather than strange. `references/decks/cliches.json` holds the full move list.

### 6. Hybridize (hidden)

Take the three most distant survivors and find the single mechanism that would
make all three the same thing. If no such mechanism exists, you are holding
three ideas, not one - go back to stage 4. Then derive at least three
consequences of that mechanism you did not intend when you wrote it. Those
consequences are usually the best material in the result.

### 7. Build the law

State the new law and what it forbids. Test it against the world: what job
becomes impossible, what sentence becomes unsayable, what ordinary courtesy
becomes an insult. Strip anything decorative that the law does not entail.

### 8. Gate (hidden)

Write `candidate.json` per `references/candidate.schema.json`, then:

```bash
scripts/score_gate.py --candidate <work>/candidate.json      # --extremal in extremal mode
scripts/score_gate.py --candidate <work>/candidate.json --grounded   # in grounded mode
scripts/cliche_lint.py --banlist <work>/banlist.json --draft <work>/draft.md
```

**`--grounded` is not a discount.** A buildable result cannot score on distance
from human centring - it exists for someone by construction - so that axis is
*replaced* by `translation_integrity`: does the operable path keep the broken
law intact, and is the loss stated? Grounded runs also owe the extra
`operational_path` section. Without the flag a grounded run fails on an axis it
was never able to satisfy, which is a fault in the gate rather than the idea.

Fix by rewriting the idea, not by deleting the flagged word. If the gate fails
twice on the same axis, return to stage 3 with `--run <n+1>`: the material is
wrong, not the phrasing.

### 9. Deliver

Render the sections in the order given by `references/output-template.md`, in
the user's language. Then stop.

## Self-interrogation before delivery

Any yes sends it back to stage 4 or 6.

- Does a specific existing work come to mind within a second of reading it?
- Does it reduce to "known thing A joined to known thing B"?
- Remove the unfamiliar vocabulary: is an ordinary thing left?
- Remove the visual description: is nothing left?
- Does it exist to be useful to a person? (Fatal in `nonhuman` mode.)
- Is the twist the one the reader would predict from the setup?
- Are the rules contradictory rather than merely unfamiliar?
- Is the discomfort coming from the premise, or from content nobody could use?
- Would this survive translation into a language with no word for the thing it
  is named after? If not, the name is doing the work the idea should do.

## Regeneration protocol

When the user says it is still not strange enough, do not add adjectives or
raise the volume. Do exactly this: re-run `draw.py` with `--run <n+1>`, add
every element of the previous answer to the ban list via `--extra`, and if this
is the third attempt, switch to `--modes extremal` and delete one more premise
from stage 2. Tell the user which premise you deleted; it is usually the thing
they were unknowingly protecting.

## References

- `references/output-template.md` - the delivered section contract
- `references/worked-example.md` - one complete run including the hidden stages
- `references/rubric.json` - the eight axes, thresholds, and section minimums
- `references/candidate.schema.json` - the structure `score_gate.py` validates
- `references/example-candidate.json` - a candidate that passes both gates
- `references/decks/` - domains, constraints, senses, perspectives, affects,
  modes, cliches
