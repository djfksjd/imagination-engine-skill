---
name: imagination-engine
description: "Generate several non-obvious, useful ideas without sacrificing the user's brief. Use only when the user explicitly invokes imagination-engine while v0.5 is being evaluated, especially for concepts, premises, mechanics, products, services, worlds, rituals, or when previous ideas feel generic. Not for factual work, routine tasks with a known conventional answer, or developing an idea the user has already selected."
---

# Imagination Engine

Produce **useful surprise**: an idea should feel non-obvious after it is
understood, yet clearly serve the brief. Treat fit as a veto. Randomness,
strangeness, invented vocabulary, and distance from the obvious are not goals
by themselves.

Work in the user's language. Keep the search private unless the user asks to
see it.

## Frame the search

Extract:

- the outcome and audience;
- the non-negotiable constraints;
- what would make an idea valuable rather than merely unusual;
- examples or mechanisms the user has already rejected.

Ask at most one concise question when a missing answer would materially change
the search. Otherwise proceed. Do not require the user to construct a ban list
or choose a mode.

If a conventional answer is clearly the best fit, say so and give it. Do not
manufacture novelty where novelty has no value.

## Generate independent candidates

Search in three passes. Scale the number of rough candidates to the task; three
to five per pass is usually enough.

1. **Direct pass:** Generate strong, concrete, high-fit answers without trying
   to be strange. This protects the brief from being lost during divergence.
2. **Mechanism-transfer pass:** Borrow causal mechanisms from unrelated
   domains, not their nouns or aesthetics. Ask what the source mechanism does,
   why it works there, and what would play the same functional roles here.
3. **Premise-shift pass:** Change one hidden assumption at a time while
   preserving every non-negotiable. Prefer shifts in actor, ownership, timing,
   unit, information flow, or incentive over arbitrary world changes.

When field-relative novelty matters and research tools are available, inspect
the nearest existing approaches and a few remote domains before the transfer
pass. Use retrieved material as raw material, not as authority. Never delay a
simple creative request with unnecessary research.

Keep the candidates independent. Do not force unrelated survivors into one
hybrid. Combine ideas only when a single causal mechanism genuinely supports
both.

## Cull by failure, then compare

Reject a candidate when:

- it violates or quietly weakens a non-negotiable;
- its novelty disappears when names, visuals, or invented terminology are
  removed;
- it is a familiar mechanism with a new theme;
- it combines distant elements without a causal bridge;
- it needs a long explanation before anyone can see why it serves the brief;
- it differs from another survivor only in presentation.

Compare survivors pairwise rather than assigning absolute self-scores. Use this
order:

1. **Fit:** Does it answer the actual brief? A loss here eliminates it.
2. **Mechanism:** Is there a specific reason it could work or remain coherent?
3. **Useful surprise:** Does understanding the mechanism make the idea more
   interesting rather than reveal it as random?
4. **Portfolio difference:** Does it add a genuinely different causal shape to
   the set?

Do not select one winner internally and fill the remaining slots with weaker
decoys. If fewer than three ideas survive, search again from a new mechanism
family.

## Deliver a portfolio

Return three to five ideas by default, ordered for the user's decision rather
than from safest to strangest. Adapt the presentation to the task. A compact
default for each idea is:

- the idea in one or two sentences;
- the mechanism that makes it work;
- why it fits this brief;
- the most important risk, tension, or unknown.

Keep the first response easy to scan. Do not add a universal lore section,
scene, administrative consequence, novelty claim, scoring rubric, or account of
the hidden process unless the task actually needs it.

End with one discriminating question that helps the user choose among the
surviving directions. When the user chooses, deepen that direction instead of
regenerating the whole portfolio. If they want a full concept review, hand off
to `imagination-brainstorming` when it is available.

## Regenerate without creating a house style

When the user rejects the set:

1. identify the rejected mechanisms, not every word or surface element;
2. preserve the brief and its non-negotiables;
3. switch the search basis: use a different source domain, actor, time horizon,
   or premise;
4. generate a new independent portfolio;
5. state in one sentence what changed in the search.

Do not merely add more constraints, increase weirdness, invert everything, or
repeat one signature move such as bodiless processes, debts, retroactive laws,
or bureaucratic consequences.

## Guardrails

- Never claim that an idea is unprecedented. When that distinction matters,
  name the closest known approach and state the operational difference.
- Do not use cruelty, degradation, or shock as shortcuts to originality.
- Do not treat the model's first associations as authoritative evidence about
  what is obvious to the user or the field.
- Do not let a method become the product. The user should receive better ideas,
  not proof that a pipeline ran.
