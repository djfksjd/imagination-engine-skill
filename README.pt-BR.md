<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/brand/imagination-octo-engine-logo-dark.png" />
  <img src="assets/brand/imagination-octo-engine-logo.png" alt="IMAGINATION OCTO ENGINE — Alcance longe" width="380" />
</picture>

# IMAGINATION OCTO ENGINE

**REACH WIDE**

### A metade divergente do Imagination Octo —<br/>um pequeno portfólio de ideias com mecanismos diferentes, em que a aderência é um veto

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português (Brasil)](README.pt-BR.md)

[![Tests](https://img.shields.io/github/actions/workflow/status/djfksjd/imagination-octo-engine/tests.yml?style=flat-square&label=tests)](https://github.com/djfksjd/imagination-octo-engine/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-MIT-1f2937?style=flat-square)](LICENSE)
![Version](https://img.shields.io/badge/version-0.5.4-d69526?style=flat-square)
[![Family](https://img.shields.io/badge/part%20of-Imagination%20Octo-6d5ef5?style=flat-square)](https://github.com/djfksjd/imagination-octo)
![Hosts](https://img.shields.io/badge/hosts-Claude%20Code%20%C2%B7%20Codex-0ea5b7?style=flat-square)

</div>

O Imagination Octo Engine devolve de três a cinco ideias que diferem no mecanismo causal, não em nomes ou estética. Uma ideia incomum que enfraquece o brief não sobrevive, e o motor nunca escolhe uma vencedora por você.

> [!TIP]
> **A maioria das pessoas deve instalar o [Imagination Octo](https://github.com/djfksjd/imagination-octo).** Ele une este motor à oficina de brainstorming e deixa com você a escolha entre os dois.

**Esta é a `v0.5.4`, uma versão que apenas renomeia o runtime avaliado como v0.5.3.** As medições abaixo vêm de comparações pequenas julgadas por IA e não afirmam criatividade universal. A invocação implícita continua desligada: chame a skill pelo nome.

## O que ele faz

| | |
|---|---|
| **Enquadramento** | Extrai o resultado, o público, o valor e o que é inegociável. Faz no máximo uma pergunta. |
| **Busca** | Três passagens: respostas diretas, mecanismos emprestados de domínios sem relação e uma premissa oculta alterada por vez. |
| **Descarte** | Elimina violações de restrições, clichês renomeados e novidade que some quando os nomes são retirados. |
| **Comparação** | Aos pares e em ordem: aderência, mecanismo, surpresa útil, diferença em relação ao resto do conjunto. |
| **Prova** | Verifica em privado, para cada sobrevivente, a evidência das restrições, a cadeia causal, o primeiro contato e a incerteza decisiva. |
| **Entrega** | De três a cinco direções independentes e uma pergunta que ajuda você a escolher. |

## Como funciona

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

- A busca e a prova ficam privadas. Você recebe as ideias, não um relatório de que um pipeline rodou.
- Em tempo de execução só um arquivo Markdown é carregado: sem script, baralho aleatório, autoavaliação ou portão.

## Experimente

```text
Use $imagination-octo-engine para propor várias mecânicas de negociação
realmente diferentes, sem árvores de diálogo, dados ocultos ou atributo de persuasão.
```

Cada direção informa seu mecanismo, por que se encaixa e seu risco principal. A resposta termina com uma pergunta e então espera.

## Medições

v0.5.3 contra um prompt simples forte, pré-registrado e às cegas: 10 briefs novos em inglês e coreano, 5 execuções cada, 5 juízes (2026-07-30).

| Métrica | Motor menos prompt simples |
|---|---:|
| Preferido para continuar | **50–0 (100%)** |
| Surpresa útil | **+0,97** |
| Diversidade do portfólio | **+0,66** |
| Aderência ao brief | **+0,60** |
| Acabamento | **+0,56** |
| Tokens | `1,12×` |

Leia com honestidade:

- **Um único modelo gerou e julgou.** Apenas `gpt-5.4`, com juízes da mesma família. O intervalo de Wilson de 95% para a preferência é 92,9–100,0%.
- **Existe um experimento entre modelos, e o resultado de preferência está anulado por enquanto.** No [Experimento A](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-06-experiment-a.md) o motor foi preferido em 11 de 12 briefs com `gpt-5.5` e em 10 de 12 com `claude-opus-5-5`. Mas os juízes acertavam qual lado usava a skill; pela regra fixada de antemão, esses números não contam até serem julgados de novo.
- **Fraquezas conhecidas.** Com o Claude ele devolve menos ideias que um prompt simples (3,8 contra 4,5), e execuções separadas ainda compartilham 40–50% dos mecanismos.
- **Duas reformulações falharam.** Uma [candidata v0.6.0](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-06-experiment-b.md) não superou a v0.5.3 em briefs novos e não foi lançada. O pipeline anterior de baralho e portões (v0.4.0) perdeu de 0–30 para um prompt simples com 48× o custo; ele fica em [`legacy/v0.4.0/`](legacy/v0.4.0/) como registro e nunca é carregado.

Protocolo, regra de decisão e resultados congelados: [`evals/`](evals/README.md).

## Quando usar e quando não usar

**Use** para conceitos, premissas, mecânicas, produtos, serviços, mundos e rituais quando a novidade útil importa, ou quando as ideias anteriores pareceram genéricas.

**Use outra coisa** para trabalho factual, tarefas rotineiras com resposta conhecida ou uma ideia que você já escolheu. Nesse último caso use o [Imagination Octo Brainstorming](https://github.com/djfksjd/imagination-octo-brainstorming).

## Renomeado de `imagination-engine`

Até a v0.5.3 este repositório era `imagination-engine-skill` e a skill era `$imagination-engine`. O GitHub redireciona a URL antiga, mas o plugin, o id do marketplace e o comando mudaram: instale `imagination-octo-engine@imagination-octo-engine` e chame `$imagination-octo-engine`. No restante, as instruções do runtime não mudaram.

## Instalação independente

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-octo-engine/main/install.sh | bash
```

Para atualizar, execute o mesmo comando de novo. Se ele avisar sobre cópias antigas dessas skills instaladas separadamente, termine o comando com `| bash -s -- --clean-legacy` para movê-las; nada é apagado.

```bash
# Claude Code
claude plugin marketplace add djfksjd/imagination-octo-engine
claude plugin install imagination-octo-engine@imagination-octo-engine

# Codex
codex plugin marketplace add djfksjd/imagination-octo-engine
codex plugin add imagination-octo-engine@imagination-octo-engine
```

## Desenvolvimento

```bash
python3 -m pytest tests/ -q
python3 evals/harness.py --help
bash -n install.sh
```

## Licença

[MIT](LICENSE).
