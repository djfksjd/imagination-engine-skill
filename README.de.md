<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/brand/imagination-octo-engine-logo-dark.png" />
  <img src="assets/brand/imagination-octo-engine-logo.png" alt="IMAGINATION OCTO ENGINE — Weit ausgreifen" width="380" />
</picture>

# IMAGINATION OCTO ENGINE

**REACH WIDE**

### Die divergente Hälfte von Imagination Octo —<br/>ein kleines Portfolio von Ideen mit unterschiedlichen Mechanismen, Passung ist ein Veto

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português (Brasil)](README.pt-BR.md)

[![Tests](https://img.shields.io/github/actions/workflow/status/djfksjd/imagination-octo-engine/tests.yml?style=flat-square&label=tests)](https://github.com/djfksjd/imagination-octo-engine/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-MIT-1f2937?style=flat-square)](LICENSE)
![Version](https://img.shields.io/badge/version-0.7.1-d69526?style=flat-square)
[![Family](https://img.shields.io/badge/part%20of-Imagination%20Octo-6d5ef5?style=flat-square)](https://github.com/djfksjd/imagination-octo)
![Hosts](https://img.shields.io/badge/hosts-Claude%20Code%20%C2%B7%20Codex-0ea5b7?style=flat-square)

</div>

Imagination Octo Engine liefert drei bis fünf Ideen, die sich im kausalen Mechanismus unterscheiden und nicht nur in Namen oder Ästhetik. Eine ungewöhnliche Idee, die das Briefing schwächt, überlebt nicht, und die Engine wählt nie für dich einen Sieger aus.

> [!TIP]
> **Die meisten sollten [Imagination Octo](https://github.com/djfksjd/imagination-octo) installieren.** Es verbindet diese Engine mit dem Brainstorming-Workshop und lässt die Wahl dazwischen bei dir.

**Dies ist `v0.7.1`.** Wenn der Host Sub-Agenten ausführen kann, läuft jeder Suchdurchgang jetzt in einem eigenen frischen Kontext, was etwa drei- bis viermal so viele Tokens kostet. Die Messwerte unten stammen aus kleinen, von KI bewerteten Vergleichen und sind kein Anspruch auf universelle Kreativität. Der implizite Aufruf bleibt aus: Rufe den Skill mit seinem Namen auf.

## Was es tut

| | |
|---|---|
| **Rahmen** | Ermittelt Ziel, Zielgruppe, Wert und nicht verhandelbare Vorgaben. Stellt höchstens eine Frage. |
| **Suche** | Drei Durchgänge: direkte Antworten, Mechanismen aus fachfremden Bereichen und jeweils eine veränderte versteckte Annahme. |
| **Aussortieren** | Verwirft Verstöße gegen Vorgaben, umbenannte Klischees und Neuheit, die verschwindet, sobald man die Namen entfernt. |
| **Vergleich** | Paarweise und der Reihe nach: Passung, Mechanismus, nützliche Überraschung, Unterschied zum Rest der Auswahl. |
| **Nachweis** | Prüft für jeden Überlebenden privat den Beleg für die Vorgaben, die Kausalkette, die erste Begegnung und die entscheidende Unsicherheit. |
| **Lieferung** | Drei bis fünf unabhängige Richtungen und eine Frage, die bei der Auswahl hilft. |

## So funktioniert es

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

- Wenn der Host Sub-Agenten ausführen kann, geht jeder Durchgang an einen eigenen Worker mit frischem Kontext, damit sich die Kandidaten nicht aneinander ausrichten. Andernfalls laufen die Durchgänge nacheinander.
- Suche und Nachweis bleiben privat. Du bekommst die Ideen, keinen Bericht darüber, dass eine Pipeline lief.
- Zur Laufzeit wird nur eine Markdown-Datei geladen: kein Skript, kein Zufallsdeck, keine Selbstbewertung, kein Gate.

## Ausprobieren

```text
Nutze $imagination-octo-engine, um mehrere wirklich unterschiedliche
Verhandlungsmechaniken ohne Dialogbäume, verdeckte Würfel oder Überzeugungswert vorzuschlagen.
```

Jede Richtung nennt ihren Mechanismus, warum sie passt, und ihr Hauptrisiko. Die Antwort endet mit einer Frage und wartet dann.

## Messwerte

v0.5.3 gegen einen starken einfachen Prompt, präregistriert und verblindet: 10 neue englische und koreanische Briefings, je 5 Läufe, 5 Bewerter (2026-07-30).

| Kennzahl | Engine minus einfacher Prompt |
|---|---:|
| Zur Weiterarbeit bevorzugt | **50–0 (100%)** |
| Nützliche Überraschung | **+0,97** |
| Vielfalt des Portfolios | **+0,66** |
| Passung zum Briefing | **+0,60** |
| Ausarbeitung | **+0,56** |
| Tokens | `1,12×` |

Ehrlich gelesen:

- **Ein einziges Modell hat erzeugt und bewertet.** Nur `gpt-5.4`, mit Bewertern aus derselben Familie. Das 95-%-Wilson-Intervall der Präferenz liegt bei 92,9–100,0 %.
- **v0.7.0 schlug v0.5.3 in einem präregistrierten Lauf, bei 3–4× Tokens.** In [Experiment C](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-07-experiment-c.md) wurde sie mit `gpt-5.5` in 11 von 12 und mit `claude-opus-5-5` in 10 von 12 Briefings bevorzugt, die nützliche Überraschung stieg um +0,44 und +0.29. Nach unserer Kodierung waren ihre Mechanismen nicht seltener als zuvor; der Gewinn liegt also eher in besser gewählten und besser ausgearbeiteten Ideen als in ausgefalleneren. Der Lauf bildete Sub-Agenten mit getrennten Aufrufen nach und wurde von der anderen Modellfamilie bewertet, nicht von Menschen.
- **Ein modellübergreifendes Experiment liegt vor, sein Präferenzergebnis ist vorerst ungültig.** In [Experiment A](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-06-experiment-a.md) wurde die Engine mit `gpt-5.5` in 11 von 12 und mit `claude-opus-5-5` in 10 von 12 Briefings bevorzugt. Die Bewerter erkannten jedoch, welche Seite den Skill benutzt hatte; nach der vorab festgelegten Regel zählen diese Werte daher erst nach einer Neubewertung.
- **Bekannte Schwächen.** Getrennte Läufe teilen weiterhin knapp die Hälfte ihrer Mechanismen (0,47 und 0,48 in Experiment C), und mit Claude liefert sie etwas weniger Ideen als ein einfacher Prompt (4,3 gegenüber 4,6). Eine strengere „mutigere“ Auswahlregel, die zusammen mit v0.7.0 getestet wurde, verfehlte ihre Schwelle und wurde nicht veröffentlicht.
- **Zwei Neuentwürfe sind gescheitert.** Ein [Kandidat v0.6.0](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-06-experiment-b.md) schlug v0.5.3 auf neuen Briefings nicht und wurde nicht veröffentlicht. Die frühere Deck-und-Gate-Pipeline (v0.4.0) verlor 0–30 gegen einen einfachen Prompt bei 48× Kosten; sie liegt als Protokoll unter [`legacy/v0.4.0/`](legacy/v0.4.0/) und wird nie geladen.

Protokoll, Entscheidungsregel und eingefrorene Ergebnisse: [`evals/`](evals/README.md).

## Wann einsetzen, wann nicht

**Nutze sie** für Konzepte, Prämissen, Mechaniken, Produkte, Dienste, Welten und Rituale, wenn nützliche Neuheit zählt oder frühere Ideen generisch wirkten.

**Nutze etwas anderes** für Faktenarbeit, Routineaufgaben mit bekannter Antwort oder eine bereits gewählte Idee. Für den letzten Fall gibt es [Imagination Octo Brainstorming](https://github.com/djfksjd/imagination-octo-brainstorming).

## Umbenannt von `imagination-engine`

Bis v0.5.3 hieß dieses Repository `imagination-engine-skill` und der Skill `$imagination-engine`. GitHub leitet die alte URL weiter, aber Plugin, Marketplace-ID und Befehl haben sich geändert: Installiere `imagination-octo-engine@imagination-octo-engine` und rufe `$imagination-octo-engine` auf.

## Einzelinstallation

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-octo-engine/main/install.sh | bash
```

Zum Aktualisieren denselben Befehl erneut ausführen. Meldet er ältere, einzeln installierte Kopien dieser Skills, den Befehl mit `| bash -s -- --clean-legacy` beenden, um sie beiseitezulegen; gelöscht wird nichts.

```bash
# Claude Code
claude plugin marketplace add djfksjd/imagination-octo-engine
claude plugin install imagination-octo-engine@imagination-octo-engine

# Codex
codex plugin marketplace add djfksjd/imagination-octo-engine
codex plugin add imagination-octo-engine@imagination-octo-engine
```

## Entwicklung

```bash
python3 -m pytest tests/ -q
python3 evals/harness.py --help
bash -n install.sh
```

## Lizenz

[MIT](LICENSE).
