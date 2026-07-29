<div align="center">

# ✦ Imagination Engine

**Une surprise utile sans perdre le brief.**

[![Tests](https://github.com/djfksjd/imagination-engine-skill/actions/workflows/tests.yml/badge.svg)](https://github.com/djfksjd/imagination-engine-skill/actions/workflows/tests.yml)
![Version](https://img.shields.io/badge/version-0.5.3-2563eb)
![Préférence](https://img.shields.io/badge/blind_preference-100%25-16a34a)
![Licence](https://img.shields.io/badge/license-MIT-0f766e)

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português (Brasil)](README.pt-BR.md)

</div>

---

> [!TIP]
> Pour la plupart des usages, installez
> [Imagination](https://github.com/djfksjd/imagination), qui réunit ce moteur et
> l’atelier conceptuel tout en conservant votre choix entre les deux phases.

Imagination Engine produit 3 à 5 idées différentes par **mécanisme causal**,
pas seulement par nom ou esthétique. L’adéquation au brief est éliminatoire :
une étrangeté qui affaiblit les contraintes est rejetée.

```text
Brief et contraintes → trois recherches → élimination → 3 à 5 idées → votre choix
```

## Exemple

```text
Utilise $imagination-engine pour proposer cinq mécanismes de négociation
réellement différents, sans arbre de dialogue ni dés cachés.
```

## Résultat mesuré

| Mesure | Face à un prompt fort |
|---|---:|
| Préférence pour poursuivre | **50–0 (100,0 %)** |
| Surprise utile | **+0,97** |
| Diversité | **+0,66** |
| Adéquation | **+0,60** |
| Finition | **+0,56** |

Résultat de juges modèles dans un test aveugle préenregistré, sans garantie
universelle.

## Installation autonome

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-engine-skill/main/install.sh | bash
```

Pour approfondir une idée choisie, utilisez
[Imagination Brainstorming](https://github.com/djfksjd/imagination-brainstorming-skill).
L’ancienne architecture reste uniquement dans `legacy/v0.4.0/`. Licence MIT.
