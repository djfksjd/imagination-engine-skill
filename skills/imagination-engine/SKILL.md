---
name: imagination-engine
description: "Radical idea generation that blocks the obvious answer instead of asking for a better one. Use when the user wants something genuinely strange - creature, world, premise, product concept, story seed, mechanic, ritual, form of life - or says the ideas so far are generic, predictable, or 'AI-sounding', or asks to think outside genre conventions. The engine burns its own first instincts into a ban list, deals a hash-seeded hand of distant domains and a reality rule to break, and gates the result on a rubric before it is shown. Works in any language. Not for factual questions, naming, or normal brainstorming where a conventional answer is the correct answer."
---

# Imagination Engine

An idea pipeline built on one observation: a model asked to "be creative" samples
from the most probable continuations of the word *creative*, which is why the
results converge on briefs that have an obvious answer to converge on.
Instructing harder does not change the distribution. Removing paths moves it -
which is measurably not the same as flattening it, and *What this is measured to
do* below says exactly how far that goes and where it stops.

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
7. **Honest gates.** A failed gate means regenerate, not resubmit with the
   flagged field padded out. The gate has no score threshold and nothing to
   round up to; what fails is structural, and structural failures are fixed by
   rewriting the idea. If a run cannot be made to clear it, say that and show
   the closest failure with the reason it failed.

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
| `scripts/banlist.py` | Turns the stage-1 instinct dump plus the cliche deck into a machine-checkable ban list | 2 if the dump is too short or is one line with a number changed |
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

Stack up to three. `draw.py --list-modes` prints all of this;
`references/decks/modes.json` is authoritative. **A mode removes something, so
every mode has a brief it is wrong for.** Read the third column before choosing.

| Mode | What it removes | Suits / destroys |
|---|---|---|
| `baby` | Learned function, correct names, and the order of cause and effect. Infant logic, adult execution - a cute result is a failed one. | **Suits** origins, first contact, a rite whose reason was forgotten. **Destroys** anything with a specification: a tool, a workflow, a mechanic that has to resolve. It discards learned function, so it discards the requirement with it. |
| `nonhuman` | Human benefit. Nothing here is for anyone; if the result is a product, it is disqualified. | **Suits** a creature, a world rule, a form of life - subjects where nobody has to want the result. The strongest mode in the deck at what it does. **Destroys any brief with a person in it.** It dissolves the asker out of the answer by construction: asked for a ritual a community performs, it returns a process observed by nobody. If the brief names a user, player, reader, congregation, customer or patient, this mode removes them and the result will not answer the question. |
| `alien-physics` | Appearance as the site of novelty. Physics, time, or selfhood changes instead. | **Suits** almost everything: it changes what is possible rather than what is visible, so the subject and its audience survive. **Weakest** where the brief is about a feeling rather than a rule - pair it with `affect` there. |
| `affect` | The five senses and the named emotions. Requires an invented sense with all four fields answered. | **Suits** interior states, senses, relationships, grief, etiquette. **Expensive**: the four required fields spend a large part of the result on one card, and on a brief that is really about a mechanism they crowd the mechanism out. |
| `extremal` | Every safe candidate. Widens the hand, deals two rules to break, and raises the discard bar - it does not raise a score bar, because there is no score bar. | **Suits** the third attempt, after two rounds the user has rejected. **Wrong on a first attempt**: it spends the widest material in the deck before the ordinary hand has been tried, and there is nothing wider to escalate to afterwards. |
| `grounded` | Nothing. Adds one `operational_path` section without editing the principle, and substitutes the rubric axis `translation_integrity` for `non_anthropocentrism`. Cannot stack with `nonhuman`. | **Suits** anything that has to exist afterwards, with anchor 2-3. **Not a rescue**: choosing it mid-run re-seeds the deal and throws away the hand and everything written against it. Choose it at stage 3, not at stage 8. |

**Default when the user does not choose: `alien-physics` at anchor 1.** The
default used to be `nonhuman,alien-physics`, and a controlled experiment
measured what that cost - see *What this is measured to do* below. `nonhuman`
is still here and still worth choosing; it is no longer applied to briefs
nobody chose it for.

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

Pass the user's list through `--extra` exactly as they gave it, including
anything the bundled deck already names - `banlist.py` records the prohibitions
in the file and the gate replays with them, so a user exclusion that collides
with a deck entry is a promotion rather than a conflict. `no dragons` turns a
deck `warn` into a `ban` and the draft is held to it.

Exit 2 has two causes and the message says which. Either the dump is too short -
fewer than twelve usable lines, so the familiar answers are still available to
you; finish it - or the dump is one line with a number changed. Twelve variants
of a template are one instinct written twelve times, and because they are all
short they all become matchable bans, which empties the manual checks the long
instincts would have produced. Write the twelve answers you would actually have
given.

`--allow <cliche id>` releases a deck phrase when the user genuinely asked for
that genre. **Read the honest limit before using it:** `cliche_lint.py` honours
the release and `score_gate.py` does not. The gate reads `allowed` off the ban
list, which is one of the artefacts it is verifying, so honouring it there would
let the run release its own bans at verdict time - the same objection that
deleted `--min-mean` and `--rubric`. The release therefore explains why a deck
phrase is absent from the file, and does not decide what the draft is linted
against. If a deck phrase genuinely does not belong in your work, the supported
route is a fork that edits `references/decks/cliches.json`, which is a
distribution decision rather than a per-run one.

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

- **replays the draw** from its own request against the bundled decks, card by
  card and not by id, so neither a card swapped after it was dealt nor a card
  whose probe, stance or replacement requirement was rewritten in place still
  follows from the request that produced it. This is a consistency boundary, not
  an authenticity one - it cannot show that the topic came from the user, that
  this was the first draw, or that a salt was not retried until the hand was
  agreeable. Say so rather than implying more.
- **binds the candidate to that draw.** Topic, run, anchor and modes must match;
  `domains_used` must be the exact set of drawn domains; `broken_rule.constraint_ids`
  the exact set of drawn constraints, each accounted for in `how_each_is_broken`;
  and `perspective_id`, `sense_seed_id`, `affect_pair_id` must be the drawn ones.
  Every drawn component is binding, so a card that did no work is not dropped -
  it is replaced by redealing.
- **reads the policy off the run.** There is no `--extremal`, no `--grounded`,
  no `--min-mean`, no `--min-axis`, no `--rubric`. A threshold asserted at
  verdict time is asserted by the same party the verdict is about. `grounded`
  in the drawn modes substitutes the rubric axis `translation_integrity` for
  `non_anthropocentrism` and requires the `operational_path` section; the
  bundled rubric is the policy, and a fork edits it rather than passing one.
  The verdict records which policy ran, with its hash.
- **requires the eight axes, and compares none of them.** Every axis has to be
  present, scored as an integer 1-10, and argued in at least forty units of
  writing; the scores and their mean are recorded in the verdict. **No score
  decides the verdict.** Twenty gated runs across four unrelated briefs were
  measured and every self-score landed in [8.00, 8.25], fourteen of them on
  exactly 8.125, against the old threshold of 8.0 - including runs blind judges
  ranked last in their pile. A number with no observed variance separates
  nothing, and comparing it left the party the verdict is about writing the
  verdict, which is the hole `--min-mean` was deleted to close, one level down.
  Answering the axes still changes the work, so they stay; an honestly low axis
  is a warning, and the field that carries the weak point is `weakest_fix`.
  Score low where it is low.
- **recomputes the ban list, and enforces what it recomputed.** The dump the file
  records is read back out of it, `banlist.py` is run again over that dump and the
  bundled deck, and the draft is linted against *that* - severities, structural
  patterns and manual checks included. The supplied file may only add: entries
  beyond the recomputed set are kept, because adding a ban cannot relax a
  verdict. Checking only that expected phrases were present, as an earlier
  version did, was much weaker than it read as - demoting one instinct from
  `ban` to `warn` left its phrase present and let the draft print it.
  This proves the file is internally consistent with a run of `banlist.py`; it
  does not prove the dump was the model's genuine first instincts. Twelve
  distinct throwaway lines still recompute cleanly. What it removes is the free
  edit after the fact.
- **enforces the burnt instincts and your own exclusions by content.** Everything
  above reads *something the run wrote about a rule* - its id, its group, its
  tier, its membership of `extra` - to decide what the contract is, and each of
  those readings was a way to leave a protected phrase sitting in the file while
  it stopped being enforced. Five were found and are now closed: emptying
  `extra` while keeping its row, demoting that row to `warn`, relabelling it with
  a bundled deck id, retyping an instinct's group as `deck`, and adding a
  structural pattern whose regex never finishes. So a second pass takes the union
  of every location that records a burnt instinct or an `--extra` exclusion and
  lints the draft against those statements as bans, reading no id, no tier, no
  group and no release. Only the bundled `structural_patterns` are compiled, and
  a pattern supplied in `banlist.json` is **refused by name** rather than run: a
  regex that does not finish leaves this gate with no verdict, and a verdict is
  what the caller reads. Refused rather than ignored because the first version of
  that fix ignored it in silence, and `{"id": "mine", "regex": "\bcheese\b"}`
  with cheese in the draft printed PASSED - a ban that quietly stops firing is
  worse than the hang it replaced. Put the pattern in a forked
  `references/decks/cliches.json` and the gate compiles it like any other.
  **The limit, exactly:** a statement deleted from *every* row that records
  it is gone. Deleting one row now leaves `counts` disagreeing with the contents,
  which catches the cheap version and not a thorough one - the gate holds no copy
  of the ban list that the run did not write.
- **says out loud everything it read and did not act on.** A field a user can
  write into that the gate silently discards is the same defect as a ban that
  stops firing: the reader believes their rule was applied. A release recorded in
  `allowed` is now reported as a warning naming the ids, on the pass path too -
  it is read, and deliberately not honoured, and that is said by the run rather
  than only by `README.md`. A `forbidden_moves` list that differs from the deck's
  is reported the same way: the moves are prose for you to obey, no lint can
  check "do not explain the strangeness away", and nothing here enforces them
  either way. Two requirements that were stated and never checked now are:
  drawing `affect` requires `invented_sense` with all four fields answered, and
  every field of `draw.json` is recomputed - `notes` and the self-reported counts
  included - not only the ones an earlier version thought mattered.

**On supplied patterns, this skill and `imagination-brainstorming` disagree, and
the disagreement is deliberate.** The sibling accepts a supplied
`structural_patterns` entry and defends it with a structural scan and a timer;
this gate refuses it. Both are answers to the same hang. This one is chosen
because refusing run-supplied policy is what the rest of this gate already does -
there is no `--rubric`, no `--min-mean`, no honoured `--allow` - and because a
timer makes what got linted depend on how fast the host is, which is a verdict
that varies by machine. A refusal that names the pattern and says where to put it
costs one line of work and cannot vary. If you move between the two skills, this
is the field to expect a different answer on.
- **requires every manual ban answered.** Long entries from stage 1 cannot be
  phrase-matched, so they land in `manual_checks` - and used to be printed and
  forgotten. Each needs a written answer of at least thirty units in
  `manual_checks_cleared`, **which is an object keyed by the check id, not a
  list**:

  ```json
  "manual_checks_cleared": {
    "obvious-01": "how the result avoids this one, in a sentence or two",
    "obvious-02": "..."
  }
  ```

  Expect twelve of these on a story, world, ritual or mechanic brief, and none
  on a product brief. The split is not about the subject, it is about sentence
  length: an instinct of more than six words cannot be matched literally, and a
  narrative instinct is naturally a clause while a product instinct is naturally
  a noun phrase. The shipped example is a product-shaped brief and clears one,
  which is why it does not look like the normal case. It is not the normal case.
- **binds the draft to the candidate.** Each scored section appears in the
  markdown inside `<!-- bind: sections.<id> -->` ... `<!-- /bind -->`, matching
  exactly. Editing one side only fails; update `candidate.json` to the final
  wording and re-gate.

`operational_path` is required whenever the run is `grounded` **or** the anchor
is 3. Both of those reach the deal: the anchor, `grounded`, `extremal` and the
requested domain count seed the shuffle, so lowering one of them in `draw.json`
afterwards deals a different hand rather than relaxing the verdict. If you need
a different setting, redeal and do the work for it.

Each seed field is normalized and then length-prefixed before it is hashed, so
no value of `--salt` can spell another field's contribution. The order matters
and getting it wrong is how this was open twice: measuring the raw field and
normalizing afterwards left the prefix describing a string that no longer
existed, so `--anchor 1` with a salt of the right raw length reproduced the
anchor-3 hand byte for byte, exactly as `--salt $'\x1fanchor=3'` had before it.
What the seeding still cannot do is tell a downgraded run from an honest one
dealt at the lower setting from the start, or stop a hand being redealt until it
suits. It raises the cost of a downgrade to a redraw and the work already
written; it is not a forgery barrier.

Length floors count **content units**: letters and digits, with a wide letter
counting two so that CJK is not penalised, plus combining marks on a letter or
digit, capped at two per base. Spaces, punctuation and symbols count zero and do
not open a new base for marks. Both halves are load-bearing. Counting spaces was
how padding cleared every floor - `"Sound"` plus two hundred spaces plus
`"stays"` measured 210 units at a perfect distinctness score - and discarding
marks was how a Devanagari, Hebrew or Thai author came to be held to roughly
twice the floor an English author cleared with the same argument. Not resetting
the cap on punctuation is what stops stacked accents buying units back. A field
with no length floor is checked for being a stand-in but not for repetition,
because there is nothing to pad towards - a title may be "Run Run Run".

Fix by rewriting the idea, not by deleting the flagged word. If the gate fails
twice on the same structural check, return to stage 3 with `--run <n+1>`: the
material is wrong, not the phrasing.

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

**One untested worry about that instruction.** Adding every element of the
previous answer pushes the next answer further along the same axis, which may
deepen the attractor described below rather than escape it. This is a
hypothesis. It has not been tested: the measurement below ran twenty
*independent* runs, not a sequential chain, so it says nothing about what
regeneration does. Stated here because it follows from the finding, not because
it is known.

## What this is measured to do, and what it is not

A controlled experiment was run on this skill in July 2026: four briefs in four
unrelated domains, five plain-prompt control runs and five full-pipeline engine
runs each, twenty disjoint dealt hands, coded blind by agents who were never
told two conditions existed. It found one thing the skill claims and one thing
it does not, and both belong here rather than in a report nobody reads.

**Confirmed, conditionally: a plain prompt does converge, when the brief has an
attractor.** Asked for an estuary creature, five independent control runs
produced five versions of one organism, and a sixth run later produced it again.
Asked for a premise set in one building, five control runs produced five
unrelated ideas. So the opening claim of this file is a description of what
happens to some briefs, not a general law. It is worth acting on where it
applies.

**Not demonstrated: that removing paths decorrelates repeated answers.** Twenty
engine runs, with twenty disjoint hands, converged on one shape - a bodiless
process rather than an entity, a subtractive obligation usually framed as a
debt, an administrative consequence, a closing move repudiating the first twelve
answers. Pooled, the engine's runs were *more* alike than the control's on both
coded measures and produced fewer distinct shapes. And the cards were not bolted
on: most left no lexical trace at all, so they were genuinely absorbed and the
outputs converged anyway. The honest reading is that removing the first-order
attractor works - the engine's answers really are unlike the control's - but
removal does not produce a uniform distribution over what is left. **It
relocates the mode.** What the twenty runs share is the most probable
continuation of *this pipeline's* instructions, in the same way the generic
answer is the most probable continuation of "be creative".

This is not fixed. Do not claim it is. What follows from it in practice:

- The skill reliably moves the output away from the obvious answer. That is a
  real capability and often the one the user wants.
- It does not guarantee that two runs on one brief will differ in shape. If the
  user needs genuinely different options, give them different *briefs* or
  different modes, not two runs of the same one.
- Watch for the house shape in your own output. If the result is a bodiless
  process that levies an obligation and produces paperwork, you have arrived
  where the last twenty runs arrived, and the self-interrogation list should
  send it back to stage 4.

**What the gate establishes.** That the required work is present and that the
four artefacts are bound to each other: the hand was dealt by the decks and not
edited afterwards, the candidate uses every card, the ban list is the one this
run's dump implies, every long instinct has a written answer, and the draft
about to be shown is the text that was checked. That is all. It does not
establish that the result is good, and there is no number in it that claims to.
Read the result yourself.

## References

- `references/output-template.md` - the delivered section contract
- `references/worked-example.md` - one complete run including the hidden stages
- `references/rubric.json` - the eight axes and the section minimums. No thresholds:
  the axes are a self-interrogation aid and no score decides a verdict
- `references/candidate.schema.json` - the structure `score_gate.py` validates
- `references/example-obvious.txt` - the twelve instincts that run burned
- `references/example-banlist.json` - the ban list built from them
- `references/example-draw.json` - the hand that run was dealt
- `references/example-candidate.json` - the candidate that passed the gate
- `references/example-draft.md` - the draft that was shown, with its bindings
- `references/decks/` - domains, constraints, senses, perspectives, affects,
  modes, cliches
