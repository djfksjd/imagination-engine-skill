<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/brand/imagination-octo-engine-logo-dark.png" />
  <img src="assets/brand/imagination-octo-engine-logo.png" alt="IMAGINATION OCTO ENGINE — 広く伸ばす" width="380" />
</picture>

# IMAGINATION OCTO ENGINE

**REACH WIDE**

### Imagination Octo の発散フェーズ —<br/>メカニズムの異なる少数のアイデア、適合性は足切り条件

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português (Brasil)](README.pt-BR.md)

[![Tests](https://img.shields.io/github/actions/workflow/status/djfksjd/imagination-octo-engine/tests.yml?style=flat-square&label=tests)](https://github.com/djfksjd/imagination-octo-engine/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-MIT-1f2937?style=flat-square)](LICENSE)
![Version](https://img.shields.io/badge/version-0.5.4-d69526?style=flat-square)
[![Family](https://img.shields.io/badge/part%20of-Imagination%20Octo-6d5ef5?style=flat-square)](https://github.com/djfksjd/imagination-octo)
![Hosts](https://img.shields.io/badge/hosts-Claude%20Code%20%C2%B7%20Codex-0ea5b7?style=flat-square)

</div>

Imagination Octo Engine は、名前や雰囲気ではなく因果メカニズムが異なるアイデアを 3〜5 個返します。ブリーフを弱めるアイデアは、どれほど意外でも残りません。エンジンがあなたの代わりにひとつを選ぶこともありません。

> [!TIP]
> **ほとんどの方には [Imagination Octo](https://github.com/djfksjd/imagination-octo) のインストールをおすすめします。** このエンジンとブレインストーミングのワークショップを組み合わせ、その間の選択はあなたに残します。

**現在は `v0.5.4` で、v0.5.3 として評価したランタイムの名前だけを変えたリリースです。** 以下の測定値は AI が審査した小規模な比較によるもので、普遍的な創造性を主張するものではありません。暗黙の呼び出しは無効のままなので、スキル名で呼び出してください。

## できること

| | |
|---|---|
| **フレーミング** | 成果、対象、価値、譲れない制約を取り出します。質問は多くても 1 つです。 |
| **探索** | 3 つのパスで探します。直接的な答え、無関係な分野から借りたメカニズム、隠れた前提を 1 つずつ変えた答え。 |
| **除外** | 制約違反、名前を変えただけの定番、名前を外すと消える新しさを捨てます。 |
| **比較** | ペアごとに順番に比べます。適合性、メカニズム、有用な意外性、ほかの候補との違い。 |
| **証明** | 残った候補ごとに、制約の根拠、因果の連鎖、最初の利用場面、決定的な不確実性を非公開で確認します。 |
| **提示** | 互いに独立した 3〜5 個の方向と、選ぶ助けになる質問を 1 つ返します。 |

## 仕組み

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

- 探索と証明は見えないところで行われます。受け取るのはアイデアであり、パイプラインが動いたという報告ではありません。
- 実行時に読み込むのは Markdown ファイル 1 つだけです。スクリプト、ランダムデッキ、自己採点、ゲートはありません。

## 使ってみる

```text
$imagination-octo-engine を使って、会話ツリー、隠しダイス、説得ステータスなしで
成り立つ、互いに異なる交渉メカニクスをいくつか提案して。
```

各方向には、メカニズム、ブリーフに合う理由、最大のリスクが書かれます。応答は質問 1 つで終わり、そこで待ちます。

## 測定結果

v0.5.3 を強い通常プロンプトと比べた、事前登録のブラインド比較です。新しい英語・韓国語のブリーフ 10 件、各 5 回実行、審査 5 名（2026-07-30）。

| 指標 | エンジン − 通常プロンプト |
|---|---:|
| 続けて発展させたい側 | **50–0 (100%)** |
| 有用な意外性 | **+0.97** |
| ポートフォリオの多様性 | **+0.66** |
| ブリーフ適合性 | **+0.60** |
| 完成度 | **+0.56** |
| トークン | `1.12×` |

正直に読むために:

- **生成も審査もひとつのモデルでした。** `gpt-5.4` のみで、審査も同じ系列です。選好の 95% Wilson 区間は 92.9–100.0% です。
- **モデル横断の実験はありますが、選好結果は現時点で無効です。** [Experiment A](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-06-experiment-a.md) では、エンジンは `gpt-5.5` で 12 件中 11 件、`claude-opus-5-5` で 12 件中 10 件のブリーフで好まれました。しかし審査側がどちらがスキルを使ったかを言い当てたため、事前に定めた規則により、再審査までこの数値は根拠として扱いません。
- **既知の弱点。** Claude では通常プロンプトよりアイデア数が少なく（3.8 個対 4.5 個）、別々に実行してもメカニズムの 40–50% が重なります。
- **再設計は 2 回失敗しました。** [候補 v0.6.0](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-06-experiment-b.md) は新しいブリーフで v0.5.3 を上回れず、出荷していません。それ以前のデッキとゲートのパイプライン（v0.4.0）は、48 倍のコストをかけて通常プロンプトに 0 対 30 で敗れました。記録として [`legacy/v0.4.0/`](legacy/v0.4.0/) に残してあり、実行時には読み込みません。

プロトコル、判定規則、固定された結果: [`evals/`](evals/README.md)。

## 使うとき、使わないとき

**使う場面：** 有用な新しさが必要なコンセプト、前提、メカニクス、製品、サービス、世界観、儀式。あるいは以前の案がありきたりに感じられるとき。

**別のものを使う場面：** 事実調査、答えが決まっている定型作業、すでに選んだアイデア。最後の場合は [Imagination Octo Brainstorming](https://github.com/djfksjd/imagination-octo-brainstorming) を使ってください。

## `imagination-engine` から改名しました

v0.5.3 まで、このリポジトリは `imagination-engine-skill`、スキルは `$imagination-engine` でした。旧 URL は GitHub がリダイレクトしますが、プラグイン名、マーケットプレイス ID、コマンドは変わりました。`imagination-octo-engine@imagination-octo-engine` をインストールし、`$imagination-octo-engine` で呼び出してください。それ以外のランタイムの指示は変わっていません。

## 単独インストール

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-octo-engine/main/install.sh | bash
```

更新するときも同じコマンドを再実行します。以前に個別インストールしたスキルのコピーが報告された場合は、コマンドの末尾を `| bash -s -- --clean-legacy` に変えて実行してください。削除はせず、別の場所へ移します。

```bash
# Claude Code
claude plugin marketplace add djfksjd/imagination-octo-engine
claude plugin install imagination-octo-engine@imagination-octo-engine

# Codex
codex plugin marketplace add djfksjd/imagination-octo-engine
codex plugin add imagination-octo-engine@imagination-octo-engine
```

## 開発

```bash
python3 -m pytest tests/ -q
python3 evals/harness.py --help
bash -n install.sh
```

## ライセンス

[MIT](LICENSE).
