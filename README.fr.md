<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/brand/imagination-octo-engine-logo-dark.png" />
  <img src="assets/brand/imagination-octo-engine-logo.png" alt="IMAGINATION OCTO ENGINE — Voir large" width="380" />
</picture>

# IMAGINATION OCTO ENGINE

**REACH WIDE**

### La moitié divergente d'Imagination Octo —<br/>un petit portefeuille d'idées aux mécanismes différents, où l'adéquation est un veto

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português (Brasil)](README.pt-BR.md)

[![Tests](https://img.shields.io/github/actions/workflow/status/djfksjd/imagination-octo-engine/tests.yml?style=flat-square&label=tests)](https://github.com/djfksjd/imagination-octo-engine/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-MIT-1f2937?style=flat-square)](LICENSE)
![Version](https://img.shields.io/badge/version-0.5.4-d69526?style=flat-square)
[![Family](https://img.shields.io/badge/part%20of-Imagination%20Octo-6d5ef5?style=flat-square)](https://github.com/djfksjd/imagination-octo)
![Hosts](https://img.shields.io/badge/hosts-Claude%20Code%20%C2%B7%20Codex-0ea5b7?style=flat-square)

</div>

Imagination Octo Engine renvoie de trois à cinq idées qui diffèrent par leur mécanisme causal, et non par leur nom ou leur esthétique. Une idée inhabituelle qui affaiblit le brief ne survit pas, et le moteur ne choisit jamais une gagnante à votre place.

> [!TIP]
> **La plupart des utilisateurs devraient installer [Imagination Octo](https://github.com/djfksjd/imagination-octo).** Il associe ce moteur à l'atelier de brainstorming et vous laisse le choix entre les deux.

**Ceci est la `v0.5.4`, une version qui ne fait que renommer le runtime évalué en v0.5.3.** Les mesures ci-dessous proviennent de petites comparaisons jugées par IA et ne prétendent pas à une créativité universelle. L'invocation implicite reste désactivée : appelez la skill par son nom.

## Ce qu'il fait

| | |
|---|---|
| **Cadrage** | Extrait le résultat visé, le public, la valeur et les contraintes non négociables. Pose au plus une question. |
| **Recherche** | Trois passes : réponses directes, mécanismes empruntés à des domaines sans rapport, et une prémisse cachée modifiée à la fois. |
| **Élimination** | Écarte les violations de contraintes, les clichés rebaptisés et la nouveauté qui disparaît quand on retire les noms. |
| **Comparaison** | Par paires et dans l'ordre : adéquation, mécanisme, surprise utile, différence avec le reste de l'ensemble. |
| **Preuve** | Vérifie en privé, pour chaque survivante, la preuve des contraintes, la chaîne causale, la première rencontre et l'incertitude décisive. |
| **Livraison** | De trois à cinq directions indépendantes et une question qui vous aide à choisir. |

## Fonctionnement

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

- La recherche et la preuve restent privées. Vous recevez les idées, pas un rapport indiquant qu'un pipeline a tourné.
- À l'exécution, un seul fichier Markdown est chargé : ni script, ni jeu de cartes aléatoire, ni auto-notation, ni barrière.

## Essayer

```text
Utilise $imagination-octo-engine pour proposer plusieurs mécaniques de négociation
vraiment différentes, sans arbre de dialogue, dés cachés ni statistique de persuasion.
```

Chaque direction indique son mécanisme, pourquoi elle convient et son risque principal. La réponse se termine par une question, puis attend.

## Mesures

v0.5.3 face à un prompt simple solide, préenregistré et à l'aveugle : 10 briefs inédits en anglais et en coréen, 5 exécutions chacun, 5 juges (2026-07-30).

| Mesure | Moteur moins prompt simple |
|---|---:|
| Préféré pour continuer | **50–0 (100%)** |
| Surprise utile | **+0,97** |
| Diversité du portefeuille | **+0,66** |
| Adéquation au brief | **+0,60** |
| Facture | **+0,56** |
| Tokens | `1,12×` |

À lire honnêtement :

- **Un seul modèle a généré et jugé.** Uniquement `gpt-5.4`, avec des juges de la même famille. L'intervalle de Wilson à 95 % pour la préférence est de 92,9–100,0 %.
- **Une expérience entre modèles existe, et son résultat de préférence est annulé pour l'instant.** Dans l'[Expérience A](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-06-experiment-a.md), le moteur a été préféré sur 11 briefs sur 12 avec `gpt-5.5` et 10 sur 12 avec `claude-opus-5-5`. Mais les juges devinaient quel côté utilisait la skill ; selon la règle fixée à l'avance, ces chiffres ne comptent donc pas tant qu'ils n'ont pas été rejugés.
- **Faiblesses connues.** Avec Claude, il renvoie moins d'idées qu'un prompt simple (3,8 contre 4,5), et des exécutions séparées partagent encore 40 à 50 % de leurs mécanismes.
- **Deux refontes ont échoué.** Une [candidate v0.6.0](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-06-experiment-b.md) n'a pas battu la v0.5.3 sur des briefs inédits et n'a pas été publiée. L'ancien pipeline à cartes et barrières (v0.4.0) a perdu 0–30 face à un prompt simple pour 48× le coût ; il est conservé dans [`legacy/v0.4.0/`](legacy/v0.4.0/) à titre d'archive et n'est jamais chargé.

Protocole, règle de décision et résultats figés : [`evals/`](evals/README.md).

## Quand l'utiliser, et quand s'en passer

**À utiliser** pour des concepts, prémisses, mécaniques, produits, services, mondes et rituels quand la nouveauté utile compte, ou quand les idées précédentes semblaient génériques.

**Utilisez autre chose** pour le travail factuel, les tâches courantes à réponse connue, ou une idée déjà choisie. Dans ce dernier cas, utilisez [Imagination Octo Brainstorming](https://github.com/djfksjd/imagination-octo-brainstorming).

## Anciennement `imagination-engine`

Jusqu'à la v0.5.3, ce dépôt s'appelait `imagination-engine-skill` et la skill `$imagination-engine`. GitHub redirige l'ancienne URL, mais le plugin, l'identifiant du marketplace et la commande ont changé : installez `imagination-octo-engine@imagination-octo-engine` et appelez `$imagination-octo-engine`. Les instructions du runtime sont par ailleurs inchangées.

## Installation autonome

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-octo-engine/main/install.sh | bash
```

Pour mettre à jour, relancez la même commande. Si elle signale d'anciennes copies de ces skills installées séparément, terminez la commande par `| bash -s -- --clean-legacy` pour les mettre de côté ; rien n'est supprimé.

```bash
# Claude Code
claude plugin marketplace add djfksjd/imagination-octo-engine
claude plugin install imagination-octo-engine@imagination-octo-engine

# Codex
codex plugin marketplace add djfksjd/imagination-octo-engine
codex plugin add imagination-octo-engine@imagination-octo-engine
```

## Développement

```bash
python3 -m pytest tests/ -q
python3 evals/harness.py --help
bash -n install.sh
```

## Licence

[MIT](LICENSE).
