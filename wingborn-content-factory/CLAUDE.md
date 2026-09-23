# Wingborn Content Factory

Este diretório é um sistema local de produção editorial para o canal Wingborn Tales
(dark fantasy com dragões, protagonista feminina, traição/reparação emocional). Ele reduz o
tempo entre "encontrar uma referência emocional em alta" e "roteiro + prompts de cena + SEO
prontos para narração e produção".

**Leia este arquivo antes de executar qualquer comando abaixo.** Ele define como interpretar os
comandos, os limites de originalidade e o fluxo de estados.

## Como interpretar os comandos

Cada arquivo em `commands/*.md` é a especificação completa de um comando. Quando o usuário digitar
algo como `/iniciar-projeto`, `/escrever-bloco 2` etc., leia o arquivo `commands/<nome>.md`
correspondente e siga exatamente os passos, pré-condições e proibições descritos nele.

Comandos disponíveis, na ordem típica de uso:

1. `/iniciar-projeto` — cria a pasta do projeto e o estado inicial.
2. `/triar-referencias` — registra referências candidatas com métricas.
3. `/analisar-referencia` — analisa a referência escolhida (sem criar roteiro).
4. `/criar-direcoes` — gera três direções originais; para para escolha do usuário.
5. `/escolher-direcao` — salva a direção escolhida.
6. `/criar-titulos` — gera títulos e conceito de thumbnail; para para escolha do usuário.
7. `/criar-ficha` — gera `character-bible.yaml`; para para aprovação.
8. `/escrever-bloco N` — escreve um bloco do roteiro por vez (N = 1..5).
9. `/validar-bloco N` — roda os validadores e relata o resultado.
10. `/revisar-retencao` — gera o mapa de retenção dos 15–20 minutos.
11. `/gerar-cenas` — gera 20–30 prompts de imagem, só após retenção aprovada.
12. `/gerar-seo` — gera descrição, tags, hashtags, CTA e prompt de thumbnail.
13. `/exportar-projeto` — monta os arquivos finais em `11_exports/`.

## Estado do projeto

Cada projeto vive em `projects/YYYY-MM-DD-slug/` e tem um arquivo de estado em
`00_input/project.yaml`, seguindo o schema de `templates/project.yaml`. **Tudo é salvo em
arquivo, não na memória da conversa** — qualquer projeto pode ser interrompido e retomado
lendo `project.yaml` e as pastas numeradas já preenchidas.

Estados permitidos, em ordem:

```text
input_received → reference_filtered → reference_analyzed → directions_ready →
direction_selected → title_approved → bible_approved → writing_in_progress →
script_approved → retention_approved → scenes_ready → exports_ready
```

**Nunca avance `status` para um estado cujo gate correspondente não esteja em
`approved_gates`.** Os gates são: `direction`, `title`, `character_bible`, `script`,
`retention`, `scenes`, `exports`. Rode `python3 scripts/validate_project.py projects/<id>`
depois de qualquer mudança de estado para confirmar.

## Limites de originalidade (aplicam-se a `/criar-direcoes` e a todo o roteiro)

Preservar apenas em nível abstrato: emoção desejada, promessa de curiosidade, injustiça
familiar, medo versus verdade, mistério, progressão de revelação, sensação de vingança ou
reparação, função do dragão, ritmo geral de tensão e recompensa.

Nunca reutilizar: nomes, frases, diálogos, transcrição/tradução, personagens equivalentes,
locais específicos, objetos específicos, sequência concreta de eventos, mesma causa da
traição, mesma revelação, mesmo clímax, mesmo final, ou simples troca de espécie/nome/cenário.

Se o usuário pedir uma reescrita muito próxima da referência ("trocar só o tema", "manter a
mesma sequência"), **não obedecer diretamente**: explicar brevemente que o sistema preserva
apenas a função emocional, e seguir para três direções com cadeias causais diferentes.

## Filtro de referências e dados

Visualizações mínimas 100.000, janela máxima 20 horas desde a publicação
(`config/default-project.yaml` → `reference_filter`). **Nunca inventar** visualizações, idade
do vídeo ou comentários. Sem API/conector confiável, aceitar entrada manual e marcar o campo
correspondente (`reference.views_source`) como `manual`.

## DNA do canal

Ver `config/channel.yaml` para os elementos centrais (protagonista feminina por padrão,
traição/abandono, dark fantasy, dragão com função dramática, dom inicialmente temido,
revelação gradual, vindicação, reparação, tom calmo e cinematográfico, final fechado).
Protagonista masculina só é permitida quando o projeto for marcado explicitamente como
experimento editorial (`channel_mode: experimental_male_protagonist`).

## Validadores determinísticos

Todos em `scripts/`, executáveis com `python3 scripts/<nome>.py <args>`. Requerem PyYAML
(`pip install pyyaml`). Retornam código de saída diferente de zero quando a validação falha —
trate isso como bloqueio real, não como sugestão.

- `validate_project.py <projeto>` — valida `project.yaml` (schema, estados, gates).
- `validate_blocks.py <projeto> [--block N]` — valida contagem de caracteres (3.200–3.500,
  com espaços) e ausência de marcadores técnicos nos blocos.
- `validate_consistency.py <projeto>` — compara `character-bible.yaml` com o roteiro
  (heurístico: nomes ausentes, idade contraditória, objeto-símbolo desaparecendo etc.).
- `validate_title_promise.py "<título>"` — checagem heurística de sinais no título; pode
  retornar `REVIEW_REQUIRED` em vez de afirmar qualidade sem evidência.
- `build_exports.py <projeto>` — monta os arquivos finais em `11_exports/`, recusa exportar
  blocos inválidos.

## Regras de escrita de bloco (resumo — ver `commands/escrever-bloco.md` para o detalhe)

- 3.200–3.500 caracteres por bloco, incluindo espaços.
- Texto narrativo limpo, sem título de bloco, sem `[CENA]`/`[PAUSE]`/instruções de produção.
- Um bloco por vez; validar e obter aprovação do usuário antes do próximo.
- Bloco 1 deve apresentar a injustiça em ~30s, identificar o antagonista, plantar
  objeto/marca/segredo antes de ~60s, criar pergunta urgente e entregar a primeira virada cedo.

## Fora de escopo neste MVP

Não implementar sem pedido explícito e fora deste fluxo: scraping agressivo do YouTube,
publicação automática, integração automática com Kaggle ou ChatGPT, execução em segundo plano
sem revisão do usuário, painel web, seleção automática definitiva baseada só em visualizações.
Conectores externos são uma fase separada, a considerar somente depois de três projetos
validados manualmente.

## O que nunca fazer

- Nunca inventar métricas de referência (views, idade, comentários).
- Nunca pular um gate de aprovação do usuário.
- Nunca produzir uma adaptação disfarçada da referência.
- Nunca afirmar que o sistema melhora CTR sem dados reais de novos vídeos publicados.
