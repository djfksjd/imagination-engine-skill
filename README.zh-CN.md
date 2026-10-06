<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/brand/imagination-octo-engine-logo-dark.png" />
  <img src="assets/brand/imagination-octo-engine-logo.png" alt="IMAGINATION OCTO ENGINE — 广泛伸展" width="380" />
</picture>

# IMAGINATION OCTO ENGINE

**REACH WIDE**

### Imagination Octo 的发散阶段 —<br/>一小组机制各不相同的想法，契合度是一票否决项

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português (Brasil)](README.pt-BR.md)

[![Tests](https://img.shields.io/github/actions/workflow/status/djfksjd/imagination-octo-engine/tests.yml?style=flat-square&label=tests)](https://github.com/djfksjd/imagination-octo-engine/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-MIT-1f2937?style=flat-square)](LICENSE)
![Version](https://img.shields.io/badge/version-0.5.4-d69526?style=flat-square)
[![Family](https://img.shields.io/badge/part%20of-Imagination%20Octo-6d5ef5?style=flat-square)](https://github.com/djfksjd/imagination-octo)
![Hosts](https://img.shields.io/badge/hosts-Claude%20Code%20%C2%B7%20Codex-0ea5b7?style=flat-square)

</div>

Imagination Octo Engine 会给出三到五个在因果机制上不同的想法，而不是只在名称或风格上不同。削弱简报的想法再新奇也不会保留，引擎也从不替你选出赢家。

> [!TIP]
> **大多数用户建议安装 [Imagination Octo](https://github.com/djfksjd/imagination-octo)。** 它把这个引擎与头脑风暴工作坊组合在一起，并把两者之间的选择留给你。

**当前为 `v0.5.4`，是以 v0.5.3 评估的运行时的仅改名版本。** 下列测量来自由 AI 评审的小规模比较，不代表普遍意义上的创造力。隐式调用保持关闭，请用技能名称调用。

## 功能

| | |
|---|---|
| **定框** | 提取目标、对象、价值和不可让步的约束。最多只问一个问题。 |
| **搜索** | 三轮搜索：直接答案、从无关领域借来的机制、每次只改变一个隐含前提。 |
| **剔除** | 丢弃违反约束的方案、换了名字的陈词滥调，以及去掉名称后就消失的新意。 |
| **比较** | 两两比较并按顺序进行：契合度、机制、有用的意外性、与其余方案的差异。 |
| **证明** | 私下检查每个幸存方案的约束依据、因果链、首次使用场景和决定性的不确定因素。 |
| **交付** | 三到五个相互独立的方向，以及一个帮助你选择的问题。 |

## 工作原理

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

- 搜索和证明在幕后完成。你得到的是想法，而不是一份流水线已运行的报告。
- 运行时只加载一个 Markdown 文件：没有脚本、随机牌组、自评分或闸门。

## 试一试

```text
使用 $imagination-octo-engine，在没有对话树、暗骰和说服属性的前提下，
提出几种真正不同的谈判机制。
```

每个方向都会写明机制、为何契合以及主要风险。回复以一个问题结束，然后等待。

## 测量结果

v0.5.3 与强普通提示的预注册盲测比较：10 份全新的英文和韩文简报，每份运行 5 次，5 名评审（2026-07-30）。

| 指标 | 引擎 − 普通提示 |
|---|---:|
| 更愿意继续发展的一方 | **50–0 (100%)** |
| 有用的意外性 | **+0.97** |
| 方案组合多样性 | **+0.66** |
| 简报契合度 | **+0.60** |
| 完成度 | **+0.56** |
| 令牌 | `1.12×` |

请如实解读：

- **生成和评审都只有一个模型。** 仅 `gpt-5.4`，评审也来自同一系列。偏好的 95% Wilson 区间为 92.9–100.0%。
- **已有跨模型实验，但其偏好结果目前无效。** 在 [Experiment A](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-06-experiment-a.md) 中，引擎在 `gpt-5.5` 的 12 份简报中有 11 份、在 `claude-opus-5-5` 的 12 份中有 10 份更受青睐。但评审能猜出哪一方使用了技能，因此按事先确定的规则，在重新评审前这些数字不作为依据。
- **已知弱点。** 在 Claude 上它给出的想法比普通提示少（3.8 个对 4.5 个），多次运行之间仍有 40–50% 的机制重合。
- **两次重新设计都失败了。** [候选版本 v0.6.0](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-06-experiment-b.md) 在新简报上未能胜过 v0.5.3，没有发布。更早的牌组与闸门流水线（v0.4.0）以 48 倍成本对普通提示 0 比 30 落败；它作为记录保留在 [`legacy/v0.4.0/`](legacy/v0.4.0/)，运行时从不加载。

协议、判定规则与冻结的结果：[`evals/`](evals/README.md)。

## 何时使用，何时不用

**适合使用：** 需要有用新意的概念、前提、机制、产品、服务、世界观和仪式，或者之前的想法显得平庸时。

**请改用其他方式：** 事实性工作、答案已知的常规任务，或你已经选定的想法。最后一种情况请使用 [Imagination Octo Brainstorming](https://github.com/djfksjd/imagination-octo-brainstorming)。

## 由 `imagination-engine` 更名而来

在 v0.5.3 之前，本仓库名为 `imagination-engine-skill`，技能名为 `$imagination-engine`。GitHub 会重定向旧地址，但插件名、市场 ID 和命令已更改：请安装 `imagination-octo-engine@imagination-octo-engine`，并使用 `$imagination-octo-engine` 调用。除此之外运行时指令没有变化。

## 单独安装

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-octo-engine/main/install.sh | bash
```

更新时再次运行同一条命令即可。如果提示存在以前单独安装的技能副本，请把命令结尾改为 `| bash -s -- --clean-legacy` 再运行；它只会把这些副本移走，不会删除。

```bash
# Claude Code
claude plugin marketplace add djfksjd/imagination-octo-engine
claude plugin install imagination-octo-engine@imagination-octo-engine

# Codex
codex plugin marketplace add djfksjd/imagination-octo-engine
codex plugin add imagination-octo-engine@imagination-octo-engine
```

## 开发

```bash
python3 -m pytest tests/ -q
python3 evals/harness.py --help
bash -n install.sh
```

## 许可证

[MIT](LICENSE).
