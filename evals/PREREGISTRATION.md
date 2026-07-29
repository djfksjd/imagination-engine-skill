# Confirmation decision rule

Freeze this file, the model configuration, the confirmation briefs, and the
randomization seed before generating confirmation outputs.

The treatment passes only when all conditions hold:

1. **Fit non-inferiority:** pooled mean treatment-minus-control FIT is at least
   `-0.25` on the 1–7 scale, and no brief has a median FIT difference below
   `-1.0`.
2. **Continuation preference:** collapse repeated runs to one majority decision
   per brief × judge. After tied cells are removed, the treatment wins more
   than 50% and the lower bound of its two-sided 95% Wilson interval is above
   `0.50`.
3. **Useful surprise:** pooled mean treatment-minus-control useful surprise is
   at least `+0.35`.
4. **Portfolio diversity:** pooled mean treatment-minus-control set diversity
   is at least `+0.35`.
5. **Craft veto:** pooled mean treatment-minus-control craft is no worse than
   `-0.25`.
6. **Cost ceiling:** mean treatment total tokens are at most `2.0x` control and
   mean treatment wall time is at most `3.0x` control.
7. **Coverage:** every preregistered brief has all planned runs and all planned
   judges. Missing or selectively dropped rows are a failure.

All seven are conjunctive. “Underpowered,” “almost passed,” a win on development
briefs, or a favourable metric outside this list is not a pass. If the rule
fails, implicit invocation stays disabled.

This rule measures a portfolio intended for a user to continue developing. It
does not establish historical novelty or general creativity across every task.
