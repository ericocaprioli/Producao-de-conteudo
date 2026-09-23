# /triar-referencias

## Propósito

Registrar uma ou mais referências candidatas com suas métricas, e classificar sua
compatibilidade com o DNA do canal e o risco de proximidade de uma adaptação.

## Pré-condições

- Projeto criado com `/iniciar-projeto` (estado `input_received` ou posterior).

## Passos

1. Receber do usuário, para cada referência: URL, título original, visualizações, idade em
   horas desde a publicação, e a fonte desses dois últimos números.
   - Filtro de referência (de `config/default-project.yaml` /
     `reference_filter`): visualizações mínimas 100.000, janela máxima 20 horas.
   - **Nunca inventar** visualizações, idade ou comentários. Se o usuário não tiver um
     conector/API confiável para esses dados, aceitar o valor informado manualmente e marcar a
     fonte como `manual` na tabela.

2. Para cada referência, classificar:
   - Tema (traição, abandono, humilhação, família, vingança, reparação, inversão, etc.);
   - Promessa em uma frase;
   - Compatibilidade com o DNA do canal (`config/channel.yaml`): alta, média ou baixa;
   - Risco de proximidade de uma adaptação: baixo, médio ou alto;
   - Motivo da seleção (ou da rejeição, se for o caso).

   Priorizar referências que cumpram o filtro de views/idade, mas não afirmar que o
   desempenho de uma referência foi causado por um único fator (título, thumbnail etc.) sem
   evidência.

3. Criar `projects/<id>/01_reference_triage/reference-triage.md` a partir de
   `templates/reference-triage.md`, preenchendo a tabela com todas as referências avaliadas.

4. Atualizar `00_input/project.yaml`: preencher `reference.url`, `reference.title`,
   `reference.views`, `reference.age_hours`, `reference.views_source` com os dados da referência
   escolhida (a de maior compatibilidade e menor risco, ou a que o usuário indicar). Atualizar
   `status: reference_filtered`.

5. Rodar `python3 scripts/validate_project.py projects/<id>` para confirmar consistência do
   estado.

## O que este comando não deve fazer

- Não escrever análise detalhada da referência (isso é `/analisar-referencia`).
- Não criar roteiro ou direções.
- Não afirmar causalidade de desempenho sem evidência.
