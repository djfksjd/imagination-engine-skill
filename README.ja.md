<div align="center">

# ✦ Imagination Engine

**ブリーフを失わない、有用な意外性。**

[![Tests](https://github.com/djfksjd/imagination-engine-skill/actions/workflows/tests.yml/badge.svg)](https://github.com/djfksjd/imagination-engine-skill/actions/workflows/tests.yml)
![Version](https://img.shields.io/badge/version-0.5.3-2563eb)
![Preference](https://img.shields.io/badge/blind_preference-100%25-16a34a)
![License](https://img.shields.io/badge/license-MIT-0f766e)

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português (Brasil)](README.pt-BR.md)

</div>

---

> [!TIP]
> 通常は統合版 [Imagination Octo](https://github.com/djfksjd/imagination-octo) を
> 推奨します。本エンジンとコンセプトワークショップを選択境界つきで提供します。

Imagination Engine は、名前や見た目ではなく **因果メカニズム** が異なる
3〜5案を生成します。適合性は拒否条件であり、ブリーフを弱める奇抜さは
採用しません。

```text
ブリーフと制約 → 3種類の探索 → 失敗候補を除外 → 3〜5案 → あなたが選択
```

## 使用例

```text
$imagination-engine を使って、対話ツリーや隠しダイスなしで動く、
本当に異なる交渉メカニズムを5つ提案して。
```

## 実測結果

| 指標 | 強い通常プロンプトとの差 |
|---|---:|
| 続けて発展させたい結果 | **50–0 (100.0%)** |
| 有用な意外性 | **+0.97** |
| 多様性 | **+0.66** |
| ブリーフ適合性 | **+0.60** |
| 完成度 | **+0.56** |

事前登録したブラインド比較のモデル審査結果です。全タスクでの普遍的優位を
保証するものではありません。

## 単独インストール

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-engine-skill/main/install.sh | bash
```

既に選択した案の具体化には
[Imagination Brainstorming](https://github.com/djfksjd/imagination-brainstorming-skill)
を使用してください。旧アーキテクチャは `legacy/v0.4.0/` にのみ保存され、
実行時には読み込まれません。MIT License.
