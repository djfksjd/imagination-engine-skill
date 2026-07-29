# Imagination Engine

Imagination Engine v0.5 is a deliberately small experimental skill for
producing a **portfolio of useful, non-obvious ideas** without trading away the
brief.

The previous constraint-heavy pipeline lost two blind comparisons with a plain
prompt. It remains intact under [`legacy/v0.4.0/`](legacy/v0.4.0/) as a research
record; it is no longer the runtime skill. The new version makes no performance
claim until it wins the preregistered holdout evaluation.

## What changed

- One concise runtime `SKILL.md`; no generation scripts or mechanical gates.
- Fit is a veto, not one axis averaged against strangeness.
- Candidates come from direct, mechanism-transfer, and premise-shift passes.
- Ideas stay independent instead of being forced into a hybrid.
- Selection is pairwise and portfolio-level; there are no absolute self-scores.
- Evaluation lives under `evals/` and never enters the creative context.
- Implicit invocation is disabled during incubation. Invoke
  `$imagination-engine` explicitly.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-engine-skill/main/install.sh | bash
```

Manual installation:

```bash
claude plugin marketplace add djfksjd/imagination-engine-skill
claude plugin install imagination-engine@djfksjd

codex plugin marketplace add djfksjd/imagination-engine-skill
codex plugin add imagination-engine@djfksjd
```

Then try:

```text
Use $imagination-engine to propose five genuinely different game mechanics
for negotiation without dialogue trees. The player must understand the
consequences before committing.
```

## Evaluation

[`evals/README.md`](evals/README.md) defines the strong control, development
briefs, blind packet format, metrics, and keep/discard rule. Runtime changes
are accepted one at a time; the confirmation set is evaluated only after the
design is frozen.

The skill is ready for implicit invocation only after:

1. fit is non-inferior to the control;
2. blind judges prefer continuing with its portfolios;
3. set-level diversity improves;
4. the cost ceiling is respected.

## Legacy

`legacy/v0.4.0/` contains the former skill, scripts, decks, examples, translated
documentation, and 300 regression tests. Those tests validate the old
pipeline's internal consistency, not creative quality.
