<div align="center">

# Imagination Engine

**Estranheza por subtração.**

Uma skill de agente que faz uma IA produzir ideias realmente estranhas — não pedindo mais imaginação,<br>mas *removendo os caminhos que levam à resposta óbvia*.

[![tests](https://github.com/djfksjd/imagination-engine-skill/actions/workflows/tests.yml/badge.svg)](https://github.com/djfksjd/imagination-engine-skill/actions/workflows/tests.yml)
[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-D97757)](#instalação)
[![Codex](https://img.shields.io/badge/Codex-plugin-1f2328)](#instalação)
[![Python](https://img.shields.io/badge/python-3.11%2B_só_stdlib-3776AB)](#por-dentro)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · **Português**

</div>

---

> Pedir a um modelo que "seja criativo" faz com que ele amostre as continuações mais prováveis da palavra *criativo*. É por isso que os resultados convergem: de novo as redes de micélio, de novo a cidade de neon sob a chuva, de novo a máquina que descobre ter sentimentos.
>
> **Insistir mais não move a distribuição. Remover opções, sim.**

## Como funciona

```mermaid
flowchart LR
    A["Seu pedido"] --> B["<b>1 · Queimar</b><br/>as 12 respostas mais<br/>prováveis → lista de vetos"]
    B --> C["<b>2 · Distribuir</b><br/>mão semeada por hash:<br/>3 domínios distantes ·<br/>uma lei a quebrar ·<br/>uma postura não humana ·<br/>um sentido · duas emoções"]
    C --> D["<b>3 · Construir</b><br/>20 candidatos → poda →<br/>hibridar os 3 mais distantes<br/>em um único mecanismo"]
    D --> E{"<b>4 · Portão</b><br/>rubrica de 8 eixos<br/>+ linter de clichês"}
    E -- falha --> C
    E -- passa --> F["Resposta no<br/>seu idioma"]
```

|  | O que acontece | Por que funciona |
|---|---|---|
| **1** | **Queima os primeiros impulsos.** Antes de gerar qualquer coisa, o modelo escreve as doze respostas que mais provavelmente daria; elas viram uma lista de vetos conferida mecanicamente contra o rascunho final. | Ele também nomeia o *esqueleto* que elas compartilham (no exemplo: um aparelho, um operador, uma substância armazenada). O esqueleto é o alvo real — toda variante repaginada cai junto com o original. |
| **2** | **Distribui uma mão que o modelo não escolheu.** Um sorteio semeado por hash entrega três domínios conceituais de categorias comprovadamente disjuntas, uma lei da realidade a quebrar, uma postura não humana, um sentido a inventar e duas emoções que precisam coexistir. | Deixado por conta própria, um modelo associa para os próprios favoritos. O sorteio é externo, reprodutível, e refazê-lo dá cartas *novas*. |
| **3** | **Exige substituir a lei quebrada.** Cada supressão instala uma lei nova, e essa lei precisa proibir algo que o mundo comum permite. | Um mundo em que uma regra apenas falta não é estranho: é vazio. A restrição é o que torna a invenção legível. |
| **4** | **Passa a saída por portões.** Uma rubrica de oito eixos e um linter de frases rodam antes de o usuário ver qualquer coisa. | Portão reprovado significa regerar — não reenviar com as notas arredondadas para cima. |

## Instalação

Roda no **Claude Code** e no **Codex**. Apenas biblioteca padrão do Python 3: nada a instalar, sem chave de API, sem acesso à rede.

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-engine-skill/main/install.sh | bash
```

<details>
<summary><b>Instalação manual</b></summary>

```bash
# Claude Code
claude plugin marketplace add djfksjd/imagination-engine-skill
claude plugin install imagination-engine@djfksjd

# Codex
codex plugin marketplace add djfksjd/imagination-engine-skill
codex plugin add imagination-engine@djfksjd
```

Uma única árvore serve os dois hosts: o corpo da skill fica em `skills/imagination-engine/`, e `AGENTS.md` é carregado como contexto compartilhado.
</details>

## Como usar

Descreva o que você quer. A skill dispara em pedidos de algo estranho ou quando você reclama que as ideias até aqui são genéricas. Prompts funcionam em qualquer idioma, e a resposta volta no idioma que você usou.

```text
Use o motor de imaginação em: uma máquina que separa emoção da voz.
Modos bebê, não humano e afeto. Nada de escaneamento neural, nada de emoções como cores.
```

```text
Projete uma criatura para o meu jogo que não se pareça com nada do gênero.
Modo extremal, âncora 2 — eu preciso conseguir construir de verdade.
```

> [!TIP]
> A coisa mais valiosa que você pode acrescentar é **a sua própria lista de vetos**. "Outro X não" vale mais do que qualquer adjetivo — e se você não der uma, a skill vai pedir.

### Modos · até três empilhados

| Modo | O que remove |
|---|---|
| `baby` | A função aprendida, os nomes corretos e a ordem de causa e efeito. Lógica de bebê, execução adulta — um resultado fofo é um fracasso. |
| `nonhuman` | A utilidade para pessoas. Aqui nada existe para ninguém; se o resultado for um produto, está desclassificado. |
| `alien-physics` | A aparência como lugar da novidade. Mudam a física, o tempo ou o self. |
| `affect` | Os cinco sentidos e as emoções nomeadas. Exige um sentido inventado e totalmente especificado — incluindo a nova injustiça que ele cria. |
| `extremal` | Todo candidato seguro. Os limiares sobem para média 9,0, nenhum eixo abaixo de 8. |
| `grounded` | Nada. Acrescenta um caminho até algo real sem editar o princípio. |

### Âncoras · quão alcançável o resultado precisa continuar

| | Nível | Requisito |
|---|---|---|
| `0` | **Sem amarras** | Coerência interna é a única obrigação |
| `1` | **Legível** | Explicável em três frases sem analogia a uma obra conhecida |
| `2` | **Encenável** | Uma cena ou objeto concreto que uma equipe conseguiria produzir |
| `3` | **Operável** | Um caminho real até um protótipo, com as perdas dessa tradução declaradas |

## O que sai

Oito seções fixas, no seu idioma: o nome · uma definição de uma linha que não se apoia em comparações · a lei pela qual existe · uma cena de primeiro encontro · sua propriedade mais estranha · os sentimentos conflitantes que provoca · o que muda no mundo por ele existir · e, obrigatório, **quais versões familiares foram descartadas e de qual obra conhecida o resultado é mais próximo**.

<details open>
<summary>Do exemplo completo — tema: <i>"uma máquina que separa emoção da voz"</i></summary>

> ### Flatting
>
> Um declive que se forma onde quer que uma frase seja dita mais de uma vez, puxando a carga de cada enunciação anterior e deixando-a nas superfícies do cômodo.
>
> […] Como a retirada corre para trás, ela edita o que já aconteceu: uma promessa repetida numa terça-feira alcança e esvazia todas as ocasiões anteriores em que foi feita, inclusive aquela que importava. Aqui é impossível tranquilizar alguém pela repetição.
>
> […] Os funerais se inverteram — lê-se o que a pessoa morta disse exatamente uma vez, quase sempre trivial, quase sempre sobre o tempo, porque são as únicas frases dela que ainda carregam alguma coisa.

</details>

Repare no que *não* está ali: nenhum aparelho, nenhum dispositivo luminoso, nada de aparência esquisita. **A estranheza está no que se tornou impossível.** A execução completa, com as etapas ocultas, está em [`worked-example.md`](skills/imagination-engine/references/worked-example.md).

## O que ela não vai fazer

> [!IMPORTANT]
> - **Afirmar que ninguém jamais pensou nisso.** Isso é inverificável, então a skill está proibida de dizer. Em vez disso, nomeia as obras conhecidas mais próximas e declara a diferença — sempre, dentro da saída.
> - **Usar choque como substituto.** Crueldade, gore, violência sexual e degradação de grupos reais são a rota mais barata ao desconforto e ficam proibidas como atalho. O desconforto precisa vir da premissa.
> - **Fingir que passar no linter significa boa ideia.** O linter prova que certos movimentos conhecidos estão *ausentes*; não prova a presença de nada. A rubrica é autoavaliada e a skill diz isso. O que os dois portões realmente impõem é que o trabalho não foi pulado.
> - **Encolher seu pedido em silêncio.** Se você precisa de algo construível, sobe-se a âncora em vez de amolecer a premissa. E quando a resposta convencional é a correta, a skill deve dizer isso e responder normalmente.

## Por dentro

| Script | Papel | Saída ≠ 0 |
|---|---|---|
| `draw.py` | Distribui a mão de restrições a partir de sete baralhos | `1` erro de uso ou de baralho |
| `banlist.py` | Funde o despejo de impulsos com o baralho de clichês em uma lista verificável | `2` despejo curto demais |
| `cliche_lint.py` | Aponta frases proibidas, adjetivos ocos e frases de folheto, com número de linha | `3` material proibido presente |
| `score_gate.py` | Valida o candidato contra a rubrica, fail-closed | `2` portão reprovado |

**Tudo é reproduzível.** O sorteio é semeado por um hash do tema, então o mesmo pedido distribui a mesma mão e qualquer resultado pode ser reproduzido e auditado. `--run 2` distribui material novo e ainda disjunto para uma regeração; `--salt` redistribui o mesmo sorteio.

```text
skills/imagination-engine/
├── SKILL.md                    # o fluxo de trabalho autoritativo
├── references/
│   ├── output-template.md      # o contrato das seções entregues
│   ├── worked-example.md       # uma execução completa, com as etapas ocultas
│   ├── rubric.json             # oito eixos · limiares · mínimos por seção
│   ├── candidate.schema.json   # o que score_gate.py valida
│   ├── example-candidate.json  # um candidato que passa nos dois portões (e serve de fixture)
│   └── decks/                  # domínios · restrições · sentidos · perspectivas
│                               # afetos · modos · clichês
└── scripts/                    # draw · banlist · cliche_lint · score_gate
```

## Testes

```bash
python3 -m pytest tests/ -q
```

Offline: integridade dos baralhos, determinismo e disjunção do sorteio, os dois portões, e o exemplo incluído passando no próprio linter.

## Contribuindo

Os baralhos são o ponto mais fácil para ajudar — um domínio genuinamente distante dos demais, uma lei da realidade que valha a pena quebrar, um sentido que valha a pena inventar. Toda entrada precisa ser respondível: um domínio exige uma pergunta que o resultado tenha de responder, e uma restrição exige seu requisito de lei substituta. Rode os testes antes de abrir um PR.

<div align="center">
<sub>Licença MIT · construído para <a href="https://claude.com/claude-code">Claude Code</a> e Codex</sub>
</div>
