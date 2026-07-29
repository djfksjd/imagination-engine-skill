<div align="center">

# ✦ Imagination Engine

**브리프를 잃지 않는 유용한 의외성.**

Codex와 Claude Code를 위한 간결한 아이디어 발산 스킬입니다.

[![테스트](https://github.com/djfksjd/imagination-engine-skill/actions/workflows/tests.yml/badge.svg)](https://github.com/djfksjd/imagination-engine-skill/actions/workflows/tests.yml)
![버전](https://img.shields.io/badge/version-0.5.2-2563eb)
![선호도](https://img.shields.io/badge/blind_preference-83.3%25-16a34a)
![라이선스](https://img.shields.io/badge/license-MIT-0f766e)

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português (Brasil)](README.pt-BR.md)

</div>

---

> [!TIP]
> **대부분의 사용자는 통합 [Imagination](https://github.com/djfksjd/imagination)을
> 권장합니다.** 이 엔진과 컨셉 워크숍을 묶되 두 단계 사이의 선택은
> 사용자에게 남깁니다.

Imagination Engine은 이름이나 외형이 아니라 **인과적 메커니즘**이 다른
아이디어 포트폴리오를 만듭니다. 적합성은 탈락 조건이므로 브리프를 약화하는
낯선 아이디어는 통과하지 않습니다.

```mermaid
flowchart LR
    A[브리프와 제약] --> B[세 가지 탐색]
    B --> C[실패 후보 제거]
    C --> D[생존 아이디어 비공개 증명]
    D --> E[독립적인 아이디어 3–5개]
    E --> F{사용자 선택}
```

## 사용해 보기

```text
$imagination-engine을 사용해서 대화 트리, 숨은 주사위, 설득 능력치 없이
작동하는 서로 다른 협상 메커니즘 다섯 개를 제안해 줘.
```

각 방향에는 핵심 메커니즘, 브리프와의 연결, 가장 중요한 위험이 포함되며,
마지막에는 선택을 돕는 질문 하나가 나옵니다.

## 작동 방식

| 단계 | 하는 일 |
|---|---|
| 프레이밍 | 목표, 사용자, 가치, 비협상 제약을 추출 |
| 탐색 | 직접 답변, 원거리 메커니즘 전이, 전제 변경 |
| 제거 | 제약 위반, 이름만 바꾼 클리셰, 자의적 새로움을 탈락 |
| 비교 | 적합성, 메커니즘, 유용한 의외성, 포트폴리오 차이를 쌍별 비교 |
| 증명 | 제약 근거, 인과 사슬, 첫 사용 장면, 결정적 불확실성을 비공개 검증 |
| 전달 | 사용자를 대신해 고르지 않고 독립 방향 3–5개 제시 |

생성 스크립트, 랜덤 덱, 절대 자기 점수와 기계식 게이트는 창작 문맥에
들어오지 않습니다.

## 측정 결과

강한 일반 프롬프트와 새 사전 등록 블라인드 비교 결과입니다.

| 지표 | 스킬 결과 − 일반 프롬프트 |
|---|---:|
| 계속 발전시키고 싶은 결과 | **25 대 5 (83.3%)** |
| 유용한 의외성 | **+0.98** |
| 포트폴리오 다양성 | **+0.93** |
| 브리프 적합성 | **+0.31** |
| 완성도 | **+0.15** |
| 토큰 비용 | `1.12배` |

선호도의 95% Wilson 구간은 66.4–92.7%입니다. 같은 모델 계열의 독립
호출이 심사했으므로 이 결과는 테스트 분포를 지지하지만 보편적 창의성을
증명하지는 않습니다. 자세한 내용은 [`evals/README.md`](evals/README.md)와
[고정 결과](evals/results/2026-07-30-gpt-5.4-confirmation-v052.json)를
참조하세요.

## 단독 설치

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-engine-skill/main/install.sh | bash
```

```bash
claude plugin marketplace add djfksjd/imagination-engine-skill
claude plugin install imagination-engine@djfksjd
codex plugin marketplace add djfksjd/imagination-engine-skill
codex plugin add imagination-engine@djfksjd
```

## 사용 범위

유용한 새로움이 필요한 컨셉, 전제, 메커니즘, 제품, 서비스, 세계관과
의례에 사용합니다. 사실 조사, 정답이 정해진 작업, 이미 선택한 아이디어의
구체화에는 사용하지 않습니다. 선택안을 발전시킬 때는
[Imagination Brainstorming](https://github.com/djfksjd/imagination-brainstorming-skill)을
사용하세요.

## 개발과 이전 버전

```bash
python3 -m pytest tests/ -q
python3 evals/harness.py --help
```

이전 실험 아키텍처는 연구 목적으로만
[`legacy/v0.4.0/`](legacy/v0.4.0/)에 보존되며 런타임에서는 로드되지
않습니다. MIT 라이선스입니다.
