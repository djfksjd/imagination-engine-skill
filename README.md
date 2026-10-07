<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/brand/imagination-octo-engine-logo-dark.png" />
  <img src="assets/brand/imagination-octo-engine-logo.png" alt="IMAGINATION OCTO ENGINE — Reach wide" width="380" />
</picture>

# IMAGINATION OCTO ENGINE

**REACH WIDE**

### The divergence half of Imagination Octo —<br/>a small portfolio of ideas that differ in mechanism, with fit as a veto

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português (Brasil)](README.pt-BR.md)

[![Tests](https://img.shields.io/github/actions/workflow/status/djfksjd/imagination-octo-engine/tests.yml?style=flat-square&label=tests)](https://github.com/djfksjd/imagination-octo-engine/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-MIT-1f2937?style=flat-square)](LICENSE)
![Version](https://img.shields.io/badge/version-0.7.0-d69526?style=flat-square)
[![Family](https://img.shields.io/badge/part%20of-Imagination%20Octo-6d5ef5?style=flat-square)](https://github.com/djfksjd/imagination-octo)
![Hosts](https://img.shields.io/badge/hosts-Claude%20Code%20%C2%B7%20Codex-0ea5b7?style=flat-square)

</div>

Imagination Octo Engine returns three to five ideas that differ in causal mechanism, not in names or aesthetics. An unusual idea that weakens the brief does not survive, and the engine never picks a winner for you.

> [!TIP]
> **Most users should install [Imagination Octo](https://github.com/djfksjd/imagination-octo).** It pairs this engine with the brainstorming workshop and keeps your choice between the two.

**This is `v0.7.0`.** When the host can run sub-agents, each search pass now runs in its own fresh context, which costs about three to four times the tokens. The measurements below come from small AI-judged comparisons and are not a claim of universal creativity. Implicit invocation stays off: call the skill by name.

## What it does

| | |
|---|---|
| **Frame** | Extracts the outcome, audience, value, and non-negotiables. Asks at most one question. |
| **Search** | Three passes: direct answers, mechanisms borrowed from unrelated domains, and one hidden premise changed at a time. |
| **Cull** | Drops constraint violations, renamed clichés, and novelty that vanishes once the names are removed. |
| **Compare** | Pairwise and in order: fit, mechanism, useful surprise, difference from the rest of the set. |
| **Prove** | Privately checks each survivor's constraint evidence, causal chain, first encounter, and decisive uncertainty. |
| **Deliver** | Three to five independent directions and one question that helps you choose. |

## How it works

```text
 your brief ──► ┌────────── search · three private passes ───────────┐
                │    direct · mechanism transfer · premise shift     │
                └──────────────────────────┬─────────────────────────┘
                                           ▼
                ┌────────────── cull · compare · prove ──────────────┐
                │        fit is a veto · pairwise comparison         │
                │        one private proof card per survivor         │
                └──────────────────────────┬─────────────────────────┘
                                           ▼
                              3–5 independent directions
                                           ▼
                                    ◆ YOU CHOOSE ◆        the engine never picks for you
```

- When the host can run sub-agents, each pass goes to its own worker with a fresh context, so candidates do not anchor on each other. Otherwise the passes run one after another.
- Search and proof stay private. You get the ideas, not a report that a pipeline ran.
- Nothing but one Markdown file is loaded at run time: no script, random deck, self-score, or gate.

## Try it

```text
Use $imagination-octo-engine to propose several genuinely different negotiation
mechanics without dialogue trees, hidden dice, or a persuasion stat.
```

Each direction states its mechanism, why it fits, and its main risk. The reply ends with one question, then waits.

## Measured

v0.5.3 against a strong plain prompt, preregistered and blind: 10 fresh English and Korean briefs, 5 runs each, 5 judges (2026-07-30).

| Metric | Engine minus plain prompt |
|---|---:|
| Preferred to continue | **50–0 (100%)** |
| Useful surprise | **+0.97** |
| Portfolio diversity | **+0.66** |
| Brief fit | **+0.60** |
| Craft | **+0.56** |
| Tokens | `1.12×` |

Read these honestly:

- **One model generated and judged.** `gpt-5.4` only, with judges from the same family. The 95% Wilson interval for preference is 92.9–100.0%.
- **v0.7.0 beat v0.5.3 in a preregistered run, at 3–4× the tokens.** In [Experiment C](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-07-experiment-c.md) it was preferred on 11 of 12 briefs with `gpt-5.5` and 10 of 12 with `claude-opus-5-5`, with useful surprise up +0.44 and +0.29. By our coding its mechanisms were no rarer than before, so the gain is better-chosen, better-worked ideas more than stranger ones. The run emulated sub-agents with separate calls and was judged by the other model family, not by people.
- **A cross-model run exists, and its preference result is void for now.** In [Experiment A](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-06-experiment-a.md) the engine was preferred on 11 of 12 briefs with `gpt-5.5` and 10 of 12 with `claude-opus-5-5`. But judges could tell which side used the skill, so under the rule fixed in advance those numbers do not count until they are re-judged.
- **Known weaknesses.** Separate runs still share close to half of their mechanisms (0.47 and 0.48 in Experiment C), and on Claude it returns slightly fewer ideas than a plain prompt (4.3 against 4.6). A stricter "bolder" selection rule tested alongside v0.7.0 failed its gate and was not shipped.
- **Two redesigns failed.** A [candidate v0.6.0](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-06-experiment-b.md) did not beat v0.5.3 on fresh briefs and was not shipped. The earlier deck-and-gate pipeline (v0.4.0) lost 0–30 to a plain prompt at 48× the cost; it is kept under [`legacy/v0.4.0/`](legacy/v0.4.0/) as a record and is never loaded.

Protocol, decision rule, and frozen results: [`evals/`](evals/README.md).

## When to use it, and when not

**Use it** for concepts, premises, mechanics, products, services, worlds, and rituals when useful novelty matters, or when earlier ideas felt generic.

**Use something else** for factual work, routine tasks with a known answer, or an idea you have already chosen. For that last case use [Imagination Octo Brainstorming](https://github.com/djfksjd/imagination-octo-brainstorming).

## Renamed from `imagination-engine`

Up to v0.5.3 this repository was `imagination-engine-skill` and the skill was `$imagination-engine`. GitHub redirects the old URL, but the plugin, the marketplace id, and the command changed: install `imagination-octo-engine@imagination-octo-engine` and call `$imagination-octo-engine`.

## Standalone install

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-octo-engine/main/install.sh | bash
```

Run the same command again to update. If it reports older standalone copies of these skills, end the command with `| bash -s -- --clean-legacy` to move them aside; nothing is deleted.

```bash
# Claude Code
claude plugin marketplace add djfksjd/imagination-octo-engine
claude plugin install imagination-octo-engine@imagination-octo-engine

# Codex
codex plugin marketplace add djfksjd/imagination-octo-engine
codex plugin add imagination-octo-engine@imagination-octo-engine
```

## Development

```bash
python3 -m pytest tests/ -q
python3 evals/harness.py --help
bash -n install.sh
```

## License

[MIT](LICENSE).
