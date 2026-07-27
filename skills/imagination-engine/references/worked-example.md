# Worked example

One complete run, from the request to the delivered answer, including the parts
the user never sees. The machine-readable version of the result is
`references/example-candidate.json`; it is the fixture the test suite gates
against, so if the pipeline ever stops accepting it, the tests fail.

**Request.** "Use the imagination engine on: a machine that separates emotion
from voice. Baby, non-human and affect modes. No neural scanning, no feelings
rendered as colour."

---

## Stage 1 - burn the first instincts (never shown to the user)

Twelve most probable answers, written down precisely so they become unavailable:

```
headset that strips feeling from speech
emotion filter for phone calls
device that stores feelings in vials
voice that becomes flat and robotic
a company selling emotional privacy
government mandate to use the filter
feelings displayed as colour
therapist machine that removes grief
singer who loses their feeling
black market for stolen emotions
child hears parent's flattened voice
machine develops feelings itself
```

```bash
banlist.py --topic "a machine that separates emotion from voice" \
  --obvious obvious.txt --extra "neural scan,emotion meter,feeling as colour" \
  --out ./work
```

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
draw.py --topic "a machine that separates emotion from voice" \
  --modes baby,nonhuman,affect --run 1 --anchor 1 --out ./work
```

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

```bash
score_gate.py --candidate ./work/candidate.json
cliche_lint.py --banlist ./work/banlist.json --draft ./work/draft.md
```

First pass failed: `non_anthropocentrism=5` and `sections.world_effect` too
thin. The fix was not a rewording - the draft still had an operator in it (a
municipal office that managed the layer). Removing the operator raised the axis
to 7 and produced the estate-listing consequence, which is better than what the
operator was doing. The final scores stand at a mean of 8.12 with
non-anthropocentrism the acknowledged weak point, written into `weakest_fix`
rather than quietly rounded up.

## The delivered answer

---

## Flatting

A grade that forms wherever a sentence is said more than once, drawing the
charge out of every earlier saying and leaving it on the surfaces of the room.

### How it exists

Speech carries a charge that is separate from its meaning. The charge belongs
to the utterance rather than to the speaker, and an utterance holds it only
until the same sentence is said again within earshot. The second saying takes
the charge from the first, the third from the second and the first, backwards
without limit. The displaced charge does not move to the new sentence; it
settles on whatever surface the sound reached, in a layer about one saying
thick, and stays there. Meaning is untouched: a flattened sentence still
informs, still instructs, still can be obeyed. What it can no longer do is
arrive. Because the taking runs backwards, this edits what has already
happened - a promise repeated on a Tuesday reaches back and empties every
earlier occasion on which it was made, including the one that mattered.
Reassurance by frequency is therefore impossible here.

### First encounter

She comes back to the kitchen eleven months after the funeral, to sort out the
cupboards, and the room is warm the way a wall is warm after an afternoon of
sun, except that it is February and the heating has been off since spring. She
says her mother's name out loud, once, into the empty room, and the sound does
something it has never done in her flat in the city: it stays. It does not
echo, it lands, and the plaster takes it, and there is a half-second delay
before her throat lets her swallow. Everything her mother said to her only once
is still in that kitchen. Everything her mother said every single day - the
phrases she would have paid to hear again - is gone from the room and gone from
her memory of it. She can recite those sentences accurately. She feels nothing
when she does, and the nothing has an outline, like a tooth that has been out
for a week.

### The strangest thing about it

It is not an object and not a creature; it is a grade, the way a river valley
is a grade. It has no inside, so it cannot be entered, opened, negotiated with
or killed - only re-cut, by refinishing the surfaces, which erases the layer
and starts the grinding from a fresh height. And it acts backwards. Every other
process in the world takes from the present. This one takes from what already
happened, so the danger here is not the future but the accumulated past, which
thins every time anyone opens their mouth.

### What it does to the people near it

The layer is the same feature that makes a room beautiful and the same feature
that indebts anyone standing in it. Rooms with a deep layer are the best places
in the world to speak, and people travel to sit in them. But an utterance whose
charge was taken before it was answered stays outstanding, and being in the
room and speaking is how one is inherited. Nobody has found a way to want the
warmth without picking something up.

### What changes because it exists

Saying a thing once becomes the expensive form and saying it often the cheap,
slightly cruel one, so vows are built to be unrepeatable - anchored to a date,
a weather, a person's exact age - so that the sentence cannot be said a second
time without becoming false. Estate agents list the layer alongside the square
footage, and there is an unresolved legal fight over whether it belongs to the
building or to the people whose sayings are in it. Districts where the grinding
finished centuries ago are called flats: perfectly intelligible, cheap,
favoured by administrators and by people who cannot bear to be reached.
Funerals have inverted - the readings are the things the dead person said
exactly once, usually trivial, often about the weather, because those are the
only sentences of theirs that still carry anything.

### What this is not

The twelve discarded answers were all apparatus: something worn on the head,
something that files feeling into a container, something that shows feeling as
a readout, plus the accompanying story about a state that mandates its use.
Each keeps two premises this deletes - that a builder performs the separation,
and that what is removed is stored somewhere retrievable. Here there is no
builder and no store, what is removed stays where it fell, and the harm lands
on the past rather than on the future. It is closest to ghost-in-the-house
stories, and differs from them in that the grade cannot register that anyone is
present; a radio left on will flatten a house by itself.

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
