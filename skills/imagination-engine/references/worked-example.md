# Worked example

One complete run, from the request to the delivered answer, including the parts
the user never sees. Every artefact this run produced is shipped, so the whole
example can be replayed command by command:

| Stage | Artefact |
|---|---|
| 1 | `references/example-obvious.txt` - the twelve first instincts |
| 1 | `references/example-banlist.json` - what `banlist.py` made of them |
| 3 | `references/example-draw.json` - the hand |
| 8 | `references/example-candidate.json` - the scored result |
| 8 | `references/example-draft.md` - the draft that was shown |

The last four are the four inputs `score_gate.py` takes, and they are the test
suite's fixture: if the pipeline ever stops accepting them, the tests fail.

Commands below are written for the skill directory - the one holding this
file's parent, `skills/imagination-engine/` in the repository. Working files
go to a scratch directory; `/tmp/work` here.

**Request.** "Use the imagination engine on: a machine that separates emotion
from voice. Baby, non-human and affect modes. No neural scanning, no feelings
rendered as colour."

---

## Stage 1 - burn the first instincts (never shown to the user)

Twelve most probable answers, written down precisely so they become unavailable.
They go in a file, one per line - this run's is shipped as
`references/example-obvious.txt`:

```
headset that strips feeling
emotion filter for phone calls
feelings stored in glass vials
flat robotic voice
company selling emotional privacy
government mandate on tone
feelings shown as colour
therapy machine for grief
singer who loses their feeling
black market for stolen emotions
neural implant that mutes affect
a machine that turns out to have been feeling everything it removed all along
```

```bash
mkdir -p /tmp/work
python3 scripts/banlist.py --topic "a machine that separates emotion from voice" \
  --obvious references/example-obvious.txt --out /tmp/work
```

Eleven are short enough to be matched literally and become bans. The twelfth is
a whole premise, so it becomes a manual check, and the gate will not pass a
result until `manual_checks_cleared` answers it in writing. Fewer than twelve
usable lines and `banlist.py` exits 2: the familiar answers are still available
to you.

Every one of these is now a failure condition rather than a temptation. Note
what they share: an apparatus, an operator, and a stored substance. That shared
skeleton is the real target - the individual phrasings are only its symptoms.

## Stage 2 - premises

Assumptions the request smuggles in, and the three that were deleted:

| # | Assumption | Verdict |
|---|---|---|
| 1 | Something built performs the separation | **deleted** |
| 2 | The separated feeling goes somewhere and can be recovered | **deleted** |
| 3 | The effect runs forward in time | **deleted** |
| 4 | A voice belongs to a speaker | kept |
| 5 | Feeling and meaning travel together | kept, then split by the new law |

## Stage 3 - the draw

```bash
python3 scripts/draw.py --topic "a machine that separates emotion from voice" \
  --modes baby,nonhuman,affect --run 1 --anchor 1 --out /tmp/work
```

That command reproduces `references/example-draw.json` exactly - the deal is
hashed from the request, so the hand is not something anyone chose.

| Slot | Card | What it had to answer |
|---|---|---|
| domain | `erosion-base-level` | What is the final level this grinds toward? |
| domain | `palimpsest` | What earlier version is still legible underneath? |
| domain | `phantom-limb` | What is felt here that is no longer present? |
| constraint | Information copies without loss | broken and replaced |
| perspective | A surface with no interior at any scale | governs everything |
| sense seed | Sensing unfinished processes nearby | four fields required |
| affect pair | beauty + obligation | both from one feature |

## Stage 4-7 - divergence, cull, hybridization

Twenty candidates, most of which reintroduced an apparatus through a side door
("a room built to do this", "a trained person who does it"). Everything with a
builder was cut on the non-human directive. Three survivors were hybridized on
one mechanism: *copying is subtractive and runs backwards*.

## Stage 8 - the gate

The result is written twice: `candidate.json` for the gate to score, and
`draft.md` for the user to read, with each scored section marked in the draft
inside `<!-- bind: sections.<id> -->` ... `<!-- /bind -->` so the two cannot
drift apart. Then one command takes all four artefacts:

```bash
python3 scripts/score_gate.py \
  --candidate references/example-candidate.json \
  --draw      references/example-draw.json \
  --banlist   references/example-banlist.json \
  --markdown  references/example-draft.md
```

```text
POLICY LOCKED: imagination-engine/0.4.0 default; all eight axes required and argued; no score threshold
mean 8.12 - recorded, not a pass mark
PASSED - the required work is present and the four artefacts are bound to each other. This is not a judgement that the result is good; read it yourself.
```

Swap in your own four and the command is the same. There is no second gate:
`cliche_lint.py --banlist /tmp/work/banlist.json --draft /tmp/work/draft.md` is
a mid-draft diagnostic, and passing it is not clearance.

First pass failed on `sections.world_effect`, which was too thin, and the
self-score put `non_anthropocentrism` at 5. The fix was not a rewording - the
draft still had an operator in it (a municipal office that managed the layer).
Removing the operator raised that axis to 7 and produced the estate-listing
consequence, which is better than what the operator was doing.

Note what did and did not force that rewrite. The *structural* failure did:
a section under its floor is a failure and there is no way around it. The score
did not, and no longer could - there is no threshold in this gate. Twenty
measured runs all self-scored into a 0.25-wide band immediately above the old
bar, so the number never discriminated anything; what it did was let the run
grade itself. The axes stay because answering them changes the work, and the
field that carries the weak point is `weakest_fix`, which is required, floored
and read by a person.

## The delivered answer

This is `references/example-draft.md` verbatim, bindings included. What the user
sees is the prose; the comments are how the gate knows the draft in front of
them is the one that was scored.

---

## <!-- bind: sections.name -->Flatting<!-- /bind -->

*<!-- bind: sections.one_line -->A grade that forms wherever a sentence is said more than once, drawing the charge out of every earlier saying and leaving it on the surfaces of the room.<!-- /bind -->*

### How it exists

<!-- bind: sections.principle -->
Speech carries a charge that is separate from its meaning. The charge is not conserved inside a person: it belongs to the utterance, and an utterance holds it only until the same sentence is said again nearby. The second saying takes the charge from the first, the third from the second and the first, and so on backwards without limit. Displaced charge does not travel to the new sentence. It settles on whatever surface the sound reached, in a layer roughly one saying thick, and stays there. Meaning is untouched throughout; a flattened sentence still informs, still instructs, still can be obeyed. What it can no longer do is arrive. Because the taking runs backwards, the process edits what has already happened rather than what will: a promise repeated on a Tuesday reaches back and empties every earlier occasion on which it was made, including the one that mattered. Nothing in this arrangement is aimed at anyone. Flatting has no interior at any scale, no preference between rooms, and no way to register that a speaker is present rather than a recording.
<!-- /bind -->

### First encounter

<!-- bind: sections.first_encounter -->
She comes back to the kitchen eleven months after the funeral, to sort out the cupboards, and the room is warm in the way that a wall is warm after a whole afternoon of sun, except that it is February and the heating has been off since spring. When she says her mother's name out loud, once, into the empty room, the sound does something it has never done in her flat in the city: it stays. It does not echo, it lands, and the plaster takes it, and there is a half-second delay before her throat lets her swallow. Everything her mother said to her only once is still in that kitchen, in the layer. Everything her mother said every single day, the phrases she would have paid to hear again, is gone from the room and gone from her memory of it, ground off by the last repetition and then by the one before that. She can recite those sentences accurately. She feels nothing when she does, and the nothing has an outline, like a tooth that has been out for a week. She sits on the floor with her back against the cupboard and does not speak again for an hour, because everything she can think of to say she has said in that room before.
<!-- /bind -->

### The strangest thing about it

<!-- bind: sections.strangest_property -->
It is not an object and not a creature. It is a grade, the way a river valley is a grade: a slope down which charge runs, produced by nothing but repetition and gradually flattening whatever produces it. It has no inside, so it cannot be entered, opened, hacked, negotiated with, or killed; it can only be re-cut, by refinishing the surfaces, which erases the layer and starts the grinding from a fresh height. And it acts backwards. Every other process in the world takes from the present. This one takes from what already happened, which means it is not the future that is dangerous here but the accumulated past, which thins every time anyone opens their mouth.
<!-- /bind -->

### What it does to the people near it

<!-- bind: sections.affect -->
The layer is the same feature that makes a room beautiful and the same feature that indebts anyone who stands in it. Rooms with a deep layer are the best places in the world to speak: the charge underfoot and overhead gives even an ordinary greeting a fullness that no new room can produce, and people travel to sit in them. But an utterance that lost its charge before it was answered stays outstanding, and the outstanding ones are all in there, and being in the room and speaking is how one is inherited. You cannot enjoy the warmth without picking something up. Nobody has found a way to want one and not the other.
<!-- /bind -->

### What changes because it exists

<!-- bind: sections.world_effect -->
Saying a thing once becomes the expensive form, and saying it often becomes the cheap and slightly cruel form, so vows are constructed to be unrepeatable: they are built around a date, a weather, a person's exact age, so that the sentence cannot be uttered a second time without becoming false and therefore cannot strip its own original. Households keep an unspoken register of which sentences have been used up. Estate agents list the layer with the square footage, and there is a legal fight, unresolved, over whether the layer belongs to the building or to the people whose sayings are in it. Old districts where the grinding finished centuries ago are called flats: perfectly intelligible places, cheap, favoured by administrators and by people who cannot bear to be reached. Scraping is a trade and a crime depending on the jurisdiction, because raising an old charge off a wall also raises the obligation attached to it, and the scraper is the one standing there when it comes due. Funeral practice has inverted: the readings at a funeral are the things the dead person said exactly once, often trivial, often about the weather, because those are the only sentences of theirs that still carry anything at all.
<!-- /bind -->

### What this is not

<!-- bind: sections.avoided -->
The first twelve answers to this prompt were devices: something worn on the head that strips feeling out of speech, something that files feeling into a container, something that shows feeling as a readout or a colour, and the accompanying story about a state that mandates its use. All of those keep the two premises this result deletes, that the separation is performed by an apparatus somebody built, and that the separated feeling has to be stored somewhere legible and retrievable. Here there is no apparatus and no operator, the separation is a property of terrain that repetition produces, what is removed is deposited where it fell rather than collected, and the harm lands on the past rather than on the future.
<!-- /bind -->

---

## What to copy from this example

- The topic word "machine" was dissolved rather than honoured. The user asked
  for a machine; the engine returned the thing that makes the machine
  unnecessary, and said so plainly in the last section.
- The strangeness is in what is possible, not in what is visible. Nothing here
  looks unusual. A film of it would be a warm kitchen in February.
- Every drawn card is load-bearing. Remove erosion and there is no base level,
  remove the palimpsest and the layer has no readers, remove phantom sensation
  and the loss has no texture.
- The weakest axis was named rather than inflated. That admission is part of
  the output contract, not a lapse in it.
