# Wingborn Content Factory

Sistema local de produção editorial para o canal **Wingborn Tales** (dark fantasy com dragões,
histórias de traição e reparação). A partir de um vídeo em alta que **você escolhe manualmente**
no YouTube, ele ajuda a criar uma **adaptação adjacente**: perto do pacote de interesse viral da
referência, mas com história, cadeia causal, revelação, clímax, final, título e thumbnail próprios.

Não é painel web nem automação em segundo plano: são comandos, templates e validadores
determinísticos usados dentro do Claude Code, com todo o estado salvo em `projects/`.

## Requisitos

- Python 3.10+
- PyYAML (`pip install pyyaml`)

## Estrutura

```text
wingborn-content-factory/
├── CLAUDE.md          # regras que o Claude Code segue ao interpretar os comandos
├── config/            # DNA do canal, padrões, regras de título, retenção e tendência
├── commands/          # especificação de cada /comando
├── scripts/           # validadores determinísticos + exportação
├── templates/         # modelos copiados para cada projeto
├── tests/             # testes + fixture "mãe abandona filha diante dos dragões"
└── projects/          # um diretório por projeto
```

## Como iniciar um projeto real

1. Escolha o vídeo no YouTube (critério editorial: ≥ 100 mil visualizações nas últimas 20 h).
2. Abra o Claude Code dentro de `wingborn-content-factory/` e digite, por exemplo:

   ```text
   /iniciar-projeto https://www.youtube.com/watch?v=SEU_VIDEO — 180 mil views, publicado há 12 h, quero surfar a tendência
   ```

   O sistema cria `projects/AAAA-MM-DD-slug/` no modo `adjacent_trend`, com as métricas
   marcadas como `manual`. O que você não informar fica como `unknown` — nada é inventado.

3. Siga o fluxo; cada etapa para quando precisa de uma decisão sua:

   ```text
   /triar-referencia
   /analisar-referencia     # cole transcrição, descrição e comentários, se tiver
   /criar-direcoes          # escolha A, B ou C
   /escolher-direcao
   /criar-titulos           # escolha o título
   /criar-ficha             # aprove a ficha e as 6 perguntas de embalagem
   /escrever-bloco 1        # ... até 5, aprovando cada bloco
   /revisar-retencao
   /gerar-cenas
   /gerar-seo
   /exportar-projeto
   ```

Para retomar um projeto interrompido:

```bash
python3 scripts/validate_project.py projects/<id>
```

Ele valida o estado e mostra o próximo comando e os blocos pendentes.

## Modos de criação

| Modo | Quando usar | O que preserva |
|---|---|---|
| `adjacent_trend` | a referência está viralizando e você quer surfar a onda | 4–5 slots do pacote viral; muda a realização concreta |
| `reference_adaptation` | referência interessante, sem evidência de onda | emoção e padrões abstratos, com mais distância |
| `original_channel_story` | sem referência | só o DNA do canal |

Em `adjacent_trend`, `/criar-direcoes` gera **A** (proximidade alta, 5 slots), **B** (média, 4) e
**C** (moderada, 4), e o `validate_trend_alignment.py` classifica cada uma.

## Validadores

```bash
python3 scripts/validate_project.py projects/<id>
python3 scripts/validate_blocks.py projects/<id> [--block N]
python3 scripts/validate_consistency.py projects/<id>
python3 scripts/validate_title_promise.py "Título" [--project projects/<id>]
python3 scripts/validate_trend_alignment.py projects/<id> [--all]
python3 scripts/validate_packaging_alignment.py projects/<id> [--title "Título"]
python3 scripts/build_exports.py projects/<id>
```

Todos retornam código diferente de zero quando a validação falha.

| Validador | Resultado |
|---|---|
| `validate_trend_alignment.py` | `ALIGNED`, `TOO_DISTANT`, `TOO_CLOSE`, `REVIEW_REQUIRED` |
| `validate_packaging_alignment.py` | `PROMISE_ALIGNED`, `EMOTION_ALIGNED`, `VISUAL_HOOK_ALIGNED`, `FANTASY_HOOK_ALIGNED`, `CURIOSITY_GAP_ALIGNED`, `TEXT_TOO_CLOSE`, `COMPOSITION_TOO_CLOSE`, `PROMISE_TOO_GENERIC`, `REVIEW_REQUIRED` |
| `validate_title_promise.py` | `PASS`, `REVIEW_REQUIRED`, `FAIL` |

## Testes

```bash
python3 -m unittest discover -s tests -v
```

O fixture `tests/fixtures/adjacent-trend-mother-dragons/` usa a referência hipotética "a mãe
abandonou a filha diante dos dragões, mas a criança possuía uma origem extraordinária" e contém:
pacote viral, três direções (A/B/C `ALIGNED`), casos `TOO_DISTANT` e `TOO_CLOSE`
(`tests/fixtures/trend-negative-cases.yaml`), ficha, títulos, embalagem e cinco blocos de
3.297 a 3.343 caracteres.

## Limitações conhecidas

- **Sem busca no YouTube**, por decisão de produto: métricas vêm de você (`manual`) ou ficam
  `unknown`.
- **Validadores de tendência e embalagem são heurísticos.** Eles comparam palavras de conteúdo
  (ignorando termos de gênero como mãe, filha, dragão e os nomes próprios) e dimensões de
  composição declaradas. Uma paráfrase com vocabulário totalmente novo e a mesma sequência de
  eventos pode escapar; por isso casos ambíguos viram `REVIEW_REQUIRED` e a leitura humana
  continua necessária.
- Os validadores confiam nos campos preenchidos pelo modelo (slots, elementos alterados,
  composição). Slots declarados sem evidência no texto são sinalizados, mas não refutados.
- `validate_consistency.py` detecta idade por extenso só em inglês (em português, apenas dígitos)
  e confere cores de cabelo/olhos/escamas por proximidade de palavras.
- A duração estimada usa 15 caracteres/s (`config/retention-rules.yaml`); ajuste para a sua voz.
- O sistema não afirma e não pode afirmar que um título, thumbnail ou direção melhora o CTR —
  isso só se mede com dados reais de vídeos publicados.
