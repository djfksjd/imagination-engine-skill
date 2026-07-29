<div align="center">

# ✦ Imagination Engine

**Nützliche Überraschung, ohne das Briefing zu verlieren.**

[![Tests](https://github.com/djfksjd/imagination-engine-skill/actions/workflows/tests.yml/badge.svg)](https://github.com/djfksjd/imagination-engine-skill/actions/workflows/tests.yml)
![Version](https://img.shields.io/badge/version-0.5.1-2563eb)
![Präferenz](https://img.shields.io/badge/blind_preference-86.7%25-16a34a)
![Lizenz](https://img.shields.io/badge/license-MIT-0f766e)

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português (Brasil)](README.pt-BR.md)

</div>

---

> [!TIP]
> Für die meisten Nutzer empfehlen wir
> [Imagination](https://github.com/djfksjd/imagination). Es verbindet diesen
> Motor mit dem Konzept-Workshop und lässt die Auswahl bei dir.

Imagination Engine erzeugt 3–5 Ideen, die sich im **kausalen Mechanismus**
unterscheiden, nicht nur im Namen oder Aussehen. Passung ist ein Ausschlusskriterium:
Ungewöhnliches, das das Briefing schwächt, wird verworfen.

```text
Briefing und Vorgaben → drei Suchen → Aussortieren → 3–5 Ideen → deine Wahl
```

## Beispiel

```text
Nutze $imagination-engine für fünf wirklich unterschiedliche
Verhandlungsmechaniken ohne Dialogbäume oder verdeckte Würfel.
```

## Messergebnis

| Kennzahl | Gegenüber starkem Prompt |
|---|---:|
| Präferenz zur Weiterarbeit | **26–4 (86,7 %)** |
| Nützliche Überraschung | **+0,90** |
| Vielfalt | **+0,47** |
| Passung | **+0,37** |
| Ausarbeitung | **+0,26** |

Das ist ein Modellrichter-Ergebnis aus einem vorregistrierten Blindtest, keine
universelle Garantie.

## Einzelinstallation

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-engine-skill/main/install.sh | bash
```

Für eine bereits gewählte Idee nutze
[Imagination Brainstorming](https://github.com/djfksjd/imagination-brainstorming-skill).
Die alte Architektur liegt nur unter `legacy/v0.4.0/`. MIT-Lizenz.
