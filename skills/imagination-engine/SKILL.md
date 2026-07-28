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
| `scripts/cliche_lint.py` | Mid-draft diagnostic only. Scans a draft for banned phrases, hollow adjectives, and pitch-shaped sentences | 3 if banned material is present |
| `scripts/score_gate.py` | **The only gate.** Replays the draw, binds the candidate to it, scores it, answers the ban list, and binds the draft that will be shown | 2 if the gate fails |

`cliche_lint.py` passing is not clearance. Two gates that never meet are one
gate: while `score_gate.py` read `candidate.json` and `cliche_lint.py` read
`draft.md`, nothing tied the candidate that passed to the draft that was shown.
`score_gate.py` now takes all four artefacts and is the only command that can
return "passed".

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
| `grounded` | Nothing. Adds one operational path without editing the principle, and swaps one rubric axis (below). Use with anchor 2-3. Cannot stack with `nonhuman`. |

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

Write `candidate.json` per `references/candidate.schema.json` and `draft.md`
per `references/output-template.md`, then run the one gate:

```bash
scripts/score_gate.py --candidate <work>/candidate.json --draw <work>/draw.json \
  --banlist <work>/banlist.json --markdown <work>/draft.md
```

All four are required and must belong to each other. The gate:

- **replays the draw** from its own request against the bundled decks, so a card
  swapped after it was dealt no longer follows from the request that produced
  it. This is a consistency boundary, not an authenticity one - it cannot show
  that the topic came from the user, that this was the first draw, or that a
  salt was not retried until the hand was agreeable. Say so rather than implying
  more.
- **binds the candidate to that draw.** Topic, run, anchor and modes must match;
  `domains_used` must be the exact set of drawn domains; `broken_rule.constraint_ids`
  the exact set of drawn constraints, each accounted for in `how_each_is_broken`;
  and `perspective_id`, `sense_seed_id`, `affect_pair_id` must be the drawn ones.
  Every drawn component is binding, so a card that did no work is not dropped -
  it is replaced by redealing.
- **reads the policy off the run.** There is no `--extremal`, no `--grounded`,
  no `--min-mean`, no `--min-axis`, no `--rubric`. A threshold asserted at
  verdict time is asserted by the same party the verdict is about. `extremal`
  in the drawn modes raises the thresholds; `grounded` substitutes the axis;
  the bundled rubric is the policy, and a fork edits it rather than passing one.
  The verdict records which policy ran, with its hash.
- **requires every manual ban answered.** Long entries from stage 1 cannot be
  phrase-matched, so they land in `manual_checks` - and used to be printed and
  forgotten. Each now needs a written answer in `manual_checks_cleared`.
- **binds the draft to the candidate.** Each scored section appears in the
  markdown inside `<!-- bind: sections.<id> -->` ... `<!-- /bind -->`, matching
  exactly. Editing one side only fails; update `candidate.json` to the final
  wording and re-gate.

`operational_path` is required whenever the run is `grounded` **or** the anchor
is 3.

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
- `references/example-obvious.txt` - the twelve instincts that run burned
- `references/example-banlist.json` - the ban list built from them
- `references/example-draw.json` - the hand that run was dealt
- `references/example-candidate.json` - the candidate that passed the gate
- `references/example-draft.md` - the draft that was shown, with its bindings
- `references/decks/` - domains, constraints, senses, perspectives, affects,
  modes, cliches
