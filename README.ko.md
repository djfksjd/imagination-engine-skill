<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/brand/imagination-octo-engine-logo-dark.png" />
  <img src="assets/brand/imagination-octo-engine-logo.png" alt="IMAGINATION OCTO ENGINE — 넓게 뻗는다" width="380" />
</picture>

# IMAGINATION OCTO ENGINE

**REACH WIDE**

### Imagination Octo의 발산 단계 —<br/>메커니즘이 서로 다른 아이디어 몇 개, 그리고 적합성은 탈락 조건

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português (Brasil)](README.pt-BR.md)

[![Tests](https://img.shields.io/github/actions/workflow/status/djfksjd/imagination-octo-engine/tests.yml?style=flat-square&label=tests)](https://github.com/djfksjd/imagination-octo-engine/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-MIT-1f2937?style=flat-square)](LICENSE)
![Version](https://img.shields.io/badge/version-0.7.1-d69526?style=flat-square)
[![Family](https://img.shields.io/badge/part%20of-Imagination%20Octo-6d5ef5?style=flat-square)](https://github.com/djfksjd/imagination-octo)
![Hosts](https://img.shields.io/badge/hosts-Claude%20Code%20%C2%B7%20Codex-0ea5b7?style=flat-square)

</div>

Imagination Octo Engine은 이름이나 분위기가 아니라 인과적 메커니즘이 서로 다른 아이디어를 3~5개 돌려줍니다. 브리프를 약하게 만드는 아이디어는 아무리 낯설어도 살아남지 못하고, 엔진이 사용자 대신 하나를 고르는 일은 없습니다.

> [!TIP]
> **대부분의 사용자에게는 [Imagination Octo](https://github.com/djfksjd/imagination-octo) 설치를 권합니다.** 이 엔진과 브레인스토밍 워크숍을 묶고, 두 단계 사이의 선택은 사용자에게 남깁니다.

**현재 `v0.7.1`입니다.** 호스트가 서브에이전트를 돌릴 수 있으면 탐색 단계마다 별도의 새 컨텍스트에서 실행하며, 그만큼 토큰을 3~4배 정도 씁니다. 아래 측정값은 AI가 심사한 소규모 비교에서 나왔고, 보편적 창의성을 주장하지 않습니다. 자동 호출은 꺼져 있으니 스킬 이름으로 직접 호출하세요.

## 하는 일

| | |
|---|---|
| **프레이밍** | 목표, 대상, 가치, 양보할 수 없는 제약을 뽑아냅니다. 질문은 많아야 하나만 합니다. |
| **탐색** | 세 갈래로 찾습니다. 직접적인 답, 무관한 분야에서 빌려 온 메커니즘, 숨은 전제를 하나씩 바꾼 답. |
| **제거** | 제약 위반, 이름만 바꾼 클리셰, 이름을 떼면 사라지는 새로움을 버립니다. |
| **비교** | 쌍으로, 순서대로 비교합니다. 적합성, 메커니즘, 유용한 의외성, 나머지 후보와의 차이. |
| **증명** | 살아남은 후보마다 제약 근거, 인과 사슬, 첫 사용 장면, 결정적 불확실성을 비공개로 확인합니다. |
| **전달** | 서로 독립적인 방향 3~5개와 선택을 돕는 질문 하나를 돌려줍니다. |

## 작동 방식

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

- 호스트가 서브에이전트를 돌릴 수 있으면 탐색 단계마다 새 컨텍스트의 작업자에게 따로 맡겨, 후보들이 서로에게 끌려가지 않게 합니다. 그렇지 않으면 단계를 차례로 실행합니다.
- 탐색과 증명은 보이지 않게 진행됩니다. 받는 것은 아이디어이지, 파이프라인이 돌았다는 보고서가 아닙니다.
- 실행 시 불러오는 것은 Markdown 파일 하나뿐입니다. 스크립트, 랜덤 덱, 자기 채점, 게이트가 없습니다.

## 사용해 보기

```text
$imagination-octo-engine을 사용해서 대화 트리, 숨은 주사위, 설득 능력치 없이
작동하는 서로 다른 협상 메커니즘을 여러 개 제안해 줘.
```

각 방향에는 메커니즘, 브리프에 맞는 이유, 가장 큰 위험이 담깁니다. 응답은 질문 하나로 끝나고, 거기서 기다립니다.

## 측정 결과

v0.5.3을 강한 일반 프롬프트와 비교한 사전 등록 블라인드 결과입니다. 새 영어·한국어 브리프 10개, 각 5회 실행, 심사자 5명 (2026-07-30).

| 지표 | 엔진 − 일반 프롬프트 |
|---|---:|
| 계속 발전시키고 싶은 쪽 | **50–0 (100%)** |
| 유용한 의외성 | **+0.97** |
| 포트폴리오 다양성 | **+0.66** |
| 브리프 적합성 | **+0.60** |
| 완성도 | **+0.56** |
| 토큰 | `1.12×` |

정직하게 읽는 법:

- **생성도 심사도 모델 하나였습니다.** `gpt-5.4`뿐이고 심사자도 같은 계열입니다. 선호도의 95% Wilson 구간은 92.9–100.0%입니다.
- **v0.7.0은 사전 등록 실험에서 v0.5.3을 이겼고, 토큰은 3~4배 듭니다.** [Experiment C](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-07-experiment-c.md)에서 `gpt-5.5`로는 브리프 12개 중 11개, `claude-opus-5-5`로는 12개 중 10개에서 선호됐고, 유용한 의외성은 +0.44, +0.29 올랐습니다. 다만 우리 코딩 기준으로 메커니즘이 전보다 더 드물어지지는 않았으므로, 이득은 더 낯선 아이디어보다는 더 잘 고르고 더 잘 다듬은 아이디어에 가깝습니다. 서브에이전트는 별도 호출로 흉내 냈고, 심사는 사람이 아니라 다른 모델 계열이 했습니다.
- **교차 모델 실험이 있지만, 선호도 결과는 현재 무효입니다.** [Experiment A](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-06-experiment-a.md)에서 엔진은 `gpt-5.5`로 브리프 12개 중 11개, `claude-opus-5-5`로 12개 중 10개에서 선호됐습니다. 그러나 심사자가 어느 쪽이 스킬을 썼는지 알아맞혔기 때문에, 미리 정한 규칙에 따라 재심사 전까지 이 수치는 근거로 쓰지 않습니다.
- **알려진 약점.** 따로 실행해도 메커니즘의 절반 가까이가 겹치고(Experiment C에서 0.47, 0.48), Claude에서는 일반 프롬프트보다 아이디어 수가 조금 적습니다(4.3개 대 4.6개). v0.7.0과 함께 시험한 더 엄격한 "과감" 선택 규칙은 관문을 통과하지 못해 출시하지 않았습니다.
- **재설계가 두 번 실패했습니다.** [후보 v0.6.0](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-06-experiment-b.md)은 새 브리프에서 v0.5.3을 이기지 못해 출시하지 않았습니다. 그 전의 덱·게이트 파이프라인(v0.4.0)은 48배 비용을 쓰고도 일반 프롬프트에 0 대 30으로 졌습니다. 기록으로 [`legacy/v0.4.0/`](legacy/v0.4.0/)에 남겨 두었고 실행 시에는 불러오지 않습니다.

프로토콜, 판정 규칙, 고정된 결과 파일: [`evals/`](evals/README.md).

## 쓸 때와 쓰지 않을 때

**쓰세요:** 유용한 새로움이 필요한 컨셉, 전제, 메커니즘, 제품, 서비스, 세계관, 의식. 또는 이전 아이디어가 뻔하게 느껴질 때.

**다른 것을 쓰세요:** 사실 조사, 정답이 정해진 일상 작업, 이미 고른 아이디어. 마지막 경우에는 [Imagination Octo Brainstorming](https://github.com/djfksjd/imagination-octo-brainstorming)을 쓰세요.

## `imagination-engine`에서 이름이 바뀌었습니다

v0.5.3까지 이 저장소는 `imagination-engine-skill`, 스킬은 `$imagination-engine`이었습니다. 예전 URL은 GitHub가 리다이렉트하지만 플러그인 이름, 마켓플레이스 ID, 명령은 바뀌었습니다. `imagination-octo-engine@imagination-octo-engine`을 설치하고 `$imagination-octo-engine`으로 호출하세요.

## 단독 설치

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-octo-engine/main/install.sh | bash
```

업데이트할 때도 같은 명령을 다시 실행하면 됩니다. 예전에 따로 설치한 스킬 복사본이 있다고 나오면 명령 끝을 `| bash -s -- --clean-legacy`로 바꿔 실행하세요. 삭제하지 않고 옮겨 둡니다.

```bash
# Claude Code
claude plugin marketplace add djfksjd/imagination-octo-engine
claude plugin install imagination-octo-engine@imagination-octo-engine

# Codex
codex plugin marketplace add djfksjd/imagination-octo-engine
codex plugin add imagination-octo-engine@imagination-octo-engine
```

## 개발

```bash
python3 -m pytest tests/ -q
python3 evals/harness.py --help
bash -n install.sh
```

## 라이선스

[MIT](LICENSE).
