# Output template

Render the nine sections of `candidate.json` in this order.

**Binding.** Every scored section body goes inside a bind block so the gate
can check that the draft being shown is the one that was scored. This is not
optional for some sections and decorative for others: `score_gate.py` looks
for one `<!-- bind: sections.<id> --> ... <!-- /bind -->` pair per entry in
`references/rubric.json`'s `required_sections`, and a section rendered
without one fails with "no bind block", even if the prose is perfect and even
if every other section is bound correctly. Bind **all nine** ids shown below
(`operational_path` only when its own condition applies - see that section):

```markdown
### First encounter

<!-- bind: sections.first_encounter -->
The body, exactly as it appears in candidate.json.
<!-- /bind -->
```

The comparison is exact after Unicode normalization and whitespace collapse.
Revising the prose means updating `candidate.json` to the final wording and
re-gating - editing one side only fails, which is the point. See
`references/example-draft.md` for a complete one with every id it needs bound.
Headings may be translated into the user's language; the order, the section
ids, and the content contract may not change. Nothing else is added: no
preamble, no summary of the process, no offer to make it stranger.

---

## <!-- bind: sections.name -->Name<!-- /bind -->

*<!-- bind: sections.one_line -->One line. State what it is. Do not describe
it by comparison to anything the reader already knows, and do not use an
adjective in place of a description.<!-- /bind -->*

### How it exists

<!-- bind: sections.principle -->
The law it runs on. Include what that law forbids that the ordinary world
allows. If a reader could not derive at least two of the consequences below
from this section alone, the law is underspecified.
<!-- /bind -->

### First encounter

<!-- bind: sections.first_encounter -->
One scene, one place, one moment, written the way a camera and a body would
take it: what is seen, what is heard, what the air or the skin does, what
someone stops doing mid-gesture. No explanation inside the scene. A reader who
skipped the previous section should still be unsettled by this one.
<!-- /bind -->

### The strangest thing about it

<!-- bind: sections.strangest_property -->
The novelty in its manner of existing, not in its appearance. If this section
can be summarized as "it looks unusual", the result failed and should not have
reached the page.
<!-- /bind -->

### What it does to the people near it

<!-- bind: sections.affect -->
The two conflicting feelings, and the single feature that produces both. Name
the feature explicitly.
<!-- /bind -->

### What changes because it exists

<!-- bind: sections.world_effect -->
Language, manners, law, work, inheritance, architecture, or burial. Three
consequences, at least one of which is administrative or boring, because
extraordinary things become paperwork and that is where they become real.
<!-- /bind -->

### What this is not

<!-- bind: sections.avoided -->
The familiar versions that were discarded and the premise each of them keeps
that this one deletes. Name them plainly. If the result is genuinely close to
an existing known work, say so here rather than hoping the reader has not read
it.
<!-- /bind -->

---

**`operational_path` exists in every candidate.json this template renders,
but it is only *required to be bound* when the run is `grounded` or the
anchor is 3 (`score_gate.py` reads this off `draw.json`, not off a claim).
At any other anchor or mode, leave this whole section out of the delivered
draft - do not bind an empty or invented path just to fill the slot.**

### One path to something real

<!-- bind: sections.operational_path -->
How a person could encounter, stage, prototype, or publish a version of this
under current constraints, and which part of the principle does not survive
the translation. The principle is not edited to fit the path.
<!-- /bind -->
