<div align="center">

# ✦ Imagination Engine

**不牺牲需求契合度的有用惊喜。**

[![Tests](https://github.com/djfksjd/imagination-engine-skill/actions/workflows/tests.yml/badge.svg)](https://github.com/djfksjd/imagination-engine-skill/actions/workflows/tests.yml)
![Version](https://img.shields.io/badge/version-0.5.1-2563eb)
![Preference](https://img.shields.io/badge/blind_preference-86.7%25-16a34a)
![License](https://img.shields.io/badge/license-MIT-0f766e)

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português (Brasil)](README.pt-BR.md)

</div>

---

> [!TIP]
> 大多数用户建议安装整合版
> [Imagination](https://github.com/djfksjd/imagination)，在发散与深化之间
> 保留用户选择。

Imagination Engine 生成 3–5 个在 **因果机制** 上真正不同的方向，而非只
更换名称或外观。契合度是淘汰条件：削弱需求的怪异创意不会通过。

```text
需求与约束 → 三路搜索 → 淘汰失败候选 → 3–5 个方向 → 你来选择
```

## 使用示例

```text
使用 $imagination-engine 提出五种真正不同、且不依赖对话树或隐藏骰子的谈判机制。
```

## 实测结果

| 指标 | 相对强普通提示词 |
|---|---:|
| 后续开发偏好 | **26–4（86.7%）** |
| 有用的意外性 | **+0.90** |
| 组合多样性 | **+0.47** |
| 需求契合度 | **+0.37** |
| 完成度 | **+0.26** |

这是预注册盲测中的模型评审结果，并不保证对所有任务普遍占优。

## 单独安装

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-engine-skill/main/install.sh | bash
```

深化已选方向请使用
[Imagination Brainstorming](https://github.com/djfksjd/imagination-brainstorming-skill)。
旧架构仅保存在 `legacy/v0.4.0/`，运行时不会加载。MIT License.
