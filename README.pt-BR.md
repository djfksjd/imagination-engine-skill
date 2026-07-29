<div align="center">

# ✦ Imagination Engine

**Surpresa útil sem perder o briefing.**

[![Tests](https://github.com/djfksjd/imagination-engine-skill/actions/workflows/tests.yml/badge.svg)](https://github.com/djfksjd/imagination-engine-skill/actions/workflows/tests.yml)
![Versão](https://img.shields.io/badge/version-0.5.1-2563eb)
![Preferência](https://img.shields.io/badge/blind_preference-86.7%25-16a34a)
![Licença](https://img.shields.io/badge/license-MIT-0f766e)

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português (Brasil)](README.pt-BR.md)

</div>

---

> [!TIP]
> Para a maioria dos usuários, recomendamos
> [Imagination](https://github.com/djfksjd/imagination), que une este motor ao
> workshop conceitual e mantém a escolha entre as fases com você.

Imagination Engine gera 3–5 ideias diferentes em **mecanismo causal**, não
apenas em nome ou estética. Aderência é critério eliminatório: uma ideia
estranha que enfraquece o briefing não passa.

```text
Briefing e restrições → três buscas → descarte → 3–5 ideias → sua escolha
```

## Exemplo

```text
Use $imagination-engine para propor cinco mecânicas de negociação realmente
diferentes, sem árvores de diálogo nem dados ocultos.
```

## Resultado medido

| Métrica | Contra um prompt forte |
|---|---:|
| Preferência para continuar | **26–4 (86,7%)** |
| Surpresa útil | **+0,90** |
| Diversidade | **+0,47** |
| Aderência | **+0,37** |
| Acabamento | **+0,26** |

É um resultado de juízes-modelo em teste cego pré-registrado, não uma garantia
universal.

## Instalação independente

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-engine-skill/main/install.sh | bash
```

Para desenvolver uma ideia já escolhida, use
[Imagination Brainstorming](https://github.com/djfksjd/imagination-brainstorming-skill).
A arquitetura anterior existe apenas em `legacy/v0.4.0/`. Licença MIT.
