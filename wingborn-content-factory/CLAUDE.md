# Wingborn Content Factory

Sistema local de produção editorial para o canal Wingborn Tales (dark fantasy com dragões,
protagonista feminina, traição e reparação). Transforma uma referência emocional em alta,
escolhida manualmente pelo usuário, em um vídeo original de 15–20 minutos: roteiro em cinco
blocos, embalagem (título + thumbnail), prompts de cena e SEO.

**Leia este arquivo antes de executar qualquer comando.**

## Como interpretar os comandos

Cada `commands/<nome>.md` é a especificação completa de um comando. Quando o usuário digitar
`/iniciar-projeto`, `/escrever-bloco 2` etc., leia o arquivo correspondente e siga os passos,
pré-condições e proibições.

Ordem típica:

1. `/iniciar-projeto` — cria a pasta e o estado inicial.
2. `/triar-referencia` — registra o link escolhido pelo usuário e classifica o filtro.
3. `/analisar-referencia` — análise + (em `adjacent_trend`) pacote viral.
4. `/criar-direcoes` — três direções; para para o usuário escolher A, B ou C.
5. `/escolher-direcao` — salva a escolha sem reescrever.
6. `/criar-titulos` — fichas de título, thumbnail e prompt; para para escolha.
7. `/criar-ficha` — ficha de consistência + aprovação de embalagem (gate `packaging`).
8. `/escrever-bloco N` — um bloco por vez, validado e aprovado.
9. `/validar-bloco N` — relatório dos validadores.
10. `/revisar-retencao` — mapa de retenção.
11. `/gerar-cenas` — 20–30 prompts de imagem.
12. `/gerar-seo` — descrição, tags, hashtags, CTA, prompt final de thumbnail.
13. `/exportar-projeto` — arquivos finais em `11_exports/`.

## Referência: seleção manual

O usuário escolhe o vídeo base no YouTube e informa o link. **O sistema não pesquisa, não
seleciona, não monitora e não faz scraping do YouTube** — mesmo que haja ferramentas de busca de
vídeos disponíveis na sessão, não use-as para escolher ou trocar a referência. É permitido ler
metadados, transcrição ou comentários **do link informado**.

Critério editorial do usuário: ≥ 100.000 visualizações e publicação nas últimas 20 horas
(`reference_filter`). Serve para classificar a referência informada (`meets_filter`), não para
buscar vídeos. **Nunca inventar métricas**: sem dado → `null` + fonte `unknown`; informado pelo
usuário → fonte `manual`. `validate_project.py` recusa número sem fonte e `meets_filter`
incoerente com os números.

## Modos de criação (`project.yaml → mode`)

- `adjacent_trend` — padrão quando o usuário fornece a referência e quer surfar a tendência.
  Preserva 4–5 slots do pacote viral e muda a realização narrativa concreta.
- `reference_adaptation` — referência interessante sem evidência de onda. Preserva emoção e
  padrões abstratos, com maior distância de superfície.
- `original_channel_story` — sem referência; apenas o DNA do canal.

## Originalidade × distanciamento excessivo

O objetivo é **adaptação adjacente**: perto do pacote de interesse viral, com história concreta,
cadeia causal, revelação, clímax e final próprios. Nem história genérica, nem cópia disfarçada.

- Slots de mercado (podem ser mantidos em `adjacent_trend`): relação emocional, tipo de traição,
  tipo de perigo, presença do dragão, vulnerabilidade visual, origem/poder extraordinário,
  promessa de sobrevivência/reconhecimento/vingança. "Mãe + filha + dragões" **não** é cópia.
- Sempre alterar: nomes, personagens concretos, frases, diálogos, cadeia causal, mecanismo da
  revelação, sequência de eventos, objeto/símbolo, clímax, final, composição da thumbnail e texto
  do título.
- Nunca reutilizar transcrição/tradução, eventos de `prohibited_events` ou a sequência concreta
  da referência. Trocar só nomes, espécie ou cenário é cópia.
- Se o usuário pedir "trocar só o tema" ou "manter a mesma sequência": não obedecer diretamente;
  explicar que o sistema preserva a função emocional (e os slots da onda) e criar três direções
  com cadeias causais diferentes.

Em `adjacent_trend`, as três direções têm distância controlada: **A** alta (5 slots), **B** média
(4 slots; muda idade, local, forma do abandono, função do dragão, reparação), **C** moderada
(4 slots; muda ambiente, parentesco secundário, objeto, mitologia, caminho da revelação).

## Mesma força viral, nova expressão (embalagem)

Título, thumbnail, prompt visual e abertura do bloco 1 preservam a **arquitetura de clique** da
referência — vítima identificável + injustiça familiar concreta + perigo visual + elemento
dragônico + segredo/origem + recompensa futura — comparada por funções, não por frases.
Não aprovar paráfrase da referência nem título genérico que abandone os slots. A thumbnail mostra
o problema e sugere a recompensa, nunca o clímax completo, com composição própria em todas as
dimensões. Antes do roteiro, o usuário responde às seis perguntas do gate `packaging`
(`templates/packaging-approval.md`).

## Estado do projeto e retomada

Cada projeto vive em `projects/YYYY-MM-DD-slug/` com o estado em `00_input/project.yaml`
(schema em `templates/project.yaml`). Tudo é salvo em arquivo; para retomar, rode
`python3 scripts/validate_project.py projects/<id>` — ele valida o estado e informa o próximo
comando e os blocos pendentes.

```text
input_received → reference_filtered → reference_analyzed → directions_ready →
direction_selected → title_approved → bible_approved → writing_in_progress →
script_approved → retention_approved → scenes_ready → exports_ready
```

Gates (`approved_gates`), exigidos a partir do estado indicado:
`direction` (direction_selected), `trend_alignment` (direction_selected, só em adjacent_trend),
`title` (title_approved), `character_bible` (bible_approved), `packaging` (writing_in_progress),
`script` (script_approved), `retention`, `scenes`, `exports`. Blocos aprovados ficam em
`approved_blocks`. **Nunca avance `status` sem o gate aprovado pelo usuário.**

## Validadores (`scripts/`)

Requerem Python 3.10+ e PyYAML. Código de saída diferente de zero é bloqueio real.

- `validate_project.py <projeto>` — schema, modo, estados, gates, métricas sem invenção, retomada.
- `validate_blocks.py <projeto> [--block N]` — 3.200–3.500 caracteres (espaços, pontuação e
  quebras internas contam), UTF-8, marcadores técnicos, sequência dos arquivos.
- `validate_consistency.py <projeto>` — ficha × roteiro: nomes ausentes/alterados, idade,
  aparência, dragão, objeto-símbolo, local do clímax, abertura do bloco 1.
- `validate_title_promise.py "<título>" [--project <projeto>]` — sinais do título e
  correspondência com a direção selecionada.
- `validate_trend_alignment.py <projeto> [--all]` — ALIGNED / TOO_DISTANT / TOO_CLOSE /
  REVIEW_REQUIRED.
- `validate_packaging_alignment.py <projeto>` — equivalência de clique do título e da thumbnail.
- `build_exports.py <projeto>` — exportação final; recusa blocos inválidos.

Os validadores de tendência e embalagem são heurísticos. Quando devolverem `REVIEW_REQUIRED`,
mostre os motivos ao usuário em vez de decidir sozinho.

## Narração (fora do Claude)

Depois de `/exportar-projeto`, o usuário narra `11_exports/tts_plain_text.txt` com a própria voz no
Kaggle, usando `narration/kaggle_narracao.ipynb` (passo a passo em `narration/README.md`). O código
fica em `narration/narrar.py`; ao alterá-lo, rode `python3 narration/build_notebook.py`.

Testes: `python3 -m unittest discover -s tests -v` (fixture em
`tests/fixtures/adjacent-trend-mother-dragons/`).

## Fora de escopo neste MVP

Busca automática ou scraping do YouTube, publicação automática, integração com Kaggle ou
ChatGPT, execução em segundo plano sem revisão, painel web, seleção automática baseada só em
visualizações. Conectores externos só depois de três projetos validados, como fase separada.

## Nunca

- Inventar métricas, comentários ou transcrição.
- Pular um gate de aprovação do usuário.
- Produzir adaptação disfarçada, ou história tão distante que abandone a onda escolhida em
  `adjacent_trend`.
- Afirmar que o sistema, um título ou uma thumbnail melhora o CTR sem dados de vídeos publicados.
