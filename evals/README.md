# Blind A/B evaluation

This directory evaluates the creative result, not whether the runtime followed
a pipeline. Keep it out of the model context during generation.

## Conditions

- **Control:** use `prompts/control.md` in a clean, tool-less context with no
  installed imagination skill.
- **Treatment:** use `prompts/treatment.md` in a clean context that can load
  only the current `imagination-engine` skill.
- Pin the model, model version, temperature, reasoning setting, maximum output
  tokens, and number of runs. Record them before generation.
- Use five independent runs per brief for confirmation. Development pilots may
  use fewer.
- Do not make outputs artificially identical after generation. Both prompts
  already request the same portfolio shape; process-revealing prose is a
  treatment failure.

`briefs.dev.jsonl` is for iteration. Do not tune on the confirmation set. Keep
the real confirmation briefs outside the repository until the design and
decision rule are frozen; `briefs.holdout.template.jsonl` defines their schema
and coverage.

## Output rows

Save one JSON object per model response:

```json
{"brief_id":"game-negotiation","condition":"control","run":1,"text":"...","input_tokens":900,"output_tokens":700,"wall_seconds":12.4}
```

Use `condition: "treatment"` for the skill arm. Token and time fields are
optional for packet construction but required for the cost rule.

## Blind packet

```bash
python3 evals/harness.py packet \
  --briefs evals/briefs.dev.jsonl \
  --outputs /path/to/outputs.jsonl \
  --packet /path/to/packet.jsonl \
  --key /path/to/answer-key.jsonl \
  --seed preregistered-seed \
  --expected-runs 5
```

Give judges `packet.jsonl` and `prompts/judge.md`, never the answer key. Each
judge writes:

```json
{
  "comparison_id": "0123456789abcdef",
  "judge_id": "judge-1",
  "ratings": {
    "left": {"fit": 6, "useful_surprise": 5, "set_diversity": 6, "craft": 5},
    "right": {"fit": 5, "useful_surprise": 4, "set_diversity": 3, "craft": 5}
  },
  "want": "left"
}
```

Use at least three blind judges per brief in development and five in
confirmation. Domain users are preferable to generic judges when the brief has
a real audience.

## Score

```bash
python3 evals/harness.py score \
  --votes /path/to/votes.jsonl \
  --key /path/to/answer-key.jsonl \
  --outputs /path/to/outputs.jsonl \
  --report /path/to/report.json \
  --expected-judges 5
```

The report gives treatment-minus-control differences, per-brief differences,
the treatment WANT win rate with a Wilson interval, and mean token/time costs.
For WANT, repeated runs are collapsed into one majority decision per
brief × judge before the interval is computed; model runs are not treated as
independent judges. Apply the frozen rule in `PREREGISTRATION.md`. Do not change
thresholds after opening the answer key.

## Iteration rule

Start with the current minimal skill. Add only one intervention per experiment:

1. current three-pass search;
2. sequential generation conditioned on prior candidates;
3. optional retrieval for mechanism transfer;
4. independent pairwise critic.

Keep an intervention only when it improves the development result without
breaking the fit or cost veto. Revert otherwise. Run the confirmation set once.
