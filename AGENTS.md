# Repository guide

The runtime skill is `skills/imagination-engine/SKILL.md`. Keep it concise,
high-freedom, and free of evaluation implementation details.

- Do not add deterministic gates to the creative runtime.
- Put benchmarks, blind-packet tooling, and scoring under `evals/`.
- Change one creative intervention at a time and compare it with the strong
  plain-prompt control before keeping it.
- Keep implicit invocation disabled until a preregistered holdout evaluation
  passes.
- Treat `legacy/v0.4.0/` as a read-only research record. It documents the
  pipeline that lost two blind evaluations and must not be loaded at runtime.
- Keep plugin versions and descriptions synchronized across all manifests.
- Run `python3 -m pytest tests/ -q` before committing.
