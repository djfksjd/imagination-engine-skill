<div align="center">

# ✦ Imagination Engine

**Sorpresa útil sin perder el brief.**

[![Tests](https://github.com/djfksjd/imagination-engine-skill/actions/workflows/tests.yml/badge.svg)](https://github.com/djfksjd/imagination-engine-skill/actions/workflows/tests.yml)
![Versión](https://img.shields.io/badge/version-0.5.1-2563eb)
![Preferencia](https://img.shields.io/badge/blind_preference-86.7%25-16a34a)
![Licencia](https://img.shields.io/badge/license-MIT-0f766e)

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português (Brasil)](README.pt-BR.md)

</div>

---

> [!TIP]
> Para la mayoría recomendamos
> [Imagination](https://github.com/djfksjd/imagination), que une este motor y el
> taller conceptual manteniendo tu elección entre ambas fases.

Imagination Engine produce 3–5 ideas distintas por **mecanismo causal**, no solo
por nombre o estética. El ajuste al brief es un veto: la rareza que debilita los
requisitos queda descartada.

```text
Brief y restricciones → tres búsquedas → descarte → 3–5 ideas → tú eliges
```

## Ejemplo

```text
Usa $imagination-engine para proponer cinco mecanismos de negociación realmente
distintos, sin árboles de diálogo ni dados ocultos.
```

## Resultado medido

| Métrica | Frente a un prompt fuerte |
|---|---:|
| Preferencia para continuar | **26–4 (86,7 %)** |
| Sorpresa útil | **+0,90** |
| Diversidad | **+0,47** |
| Ajuste al brief | **+0,37** |
| Acabado | **+0,26** |

Es un resultado de jueces modelo en una prueba ciega prerregistrada, no una
garantía universal.

## Instalación independiente

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-engine-skill/main/install.sh | bash
```

Para desarrollar una idea ya elegida, usa
[Imagination Brainstorming](https://github.com/djfksjd/imagination-brainstorming-skill).
La arquitectura anterior solo se conserva en `legacy/v0.4.0/`. Licencia MIT.
