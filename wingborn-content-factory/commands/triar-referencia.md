# /triar-referencia

## Propósito

Registrar a referência que o usuário escolheu manualmente no YouTube, classificar se ela cumpre
o filtro editorial informado e confirmar o modo de criação.

## Pré-condições

- Projeto criado (`input_received`), com `mode` diferente de `original_channel_story`.

## Passos

1. Receber o link escolhido pelo usuário e, se ele tiver, as métricas:

   ```yaml
   reference:
     url: ""
     title: ""
     views: null
     age_hours: null
     views_source: manual   # ou unknown se não informado
     age_source: manual     # ou unknown se não informado
   ```

   - **Não pesquisar nem selecionar vídeos automaticamente.** Não usar ferramentas de busca do
     YouTube para escolher ou trocar a referência.
   - Pode-se ler metadados, transcrição ou comentários **do link informado**, se houver
     ferramenta disponível; nesse caso a fonte é o nome da ferramenta, não `manual`.
   - Métrica não fornecida → `null` e fonte `unknown`. **Nunca inventar números.**

2. Calcular `reference.meets_filter` com os critérios de `reference_filter`
   (≥ 100.000 visualizações e publicação nas últimas 20 horas):
   - `false` se algum dado conhecido reprova o filtro;
   - `true` se os dois dados são conhecidos e aprovam;
   - `unknown` nos demais casos.
   O filtro serve para classificar a referência informada, não para buscar vídeos.
   `validate_project.py` recusa um `meets_filter` que não bata com os números.

3. Classificar: tema, promessa em uma frase, compatibilidade com o DNA do canal
   (`config/channel.yaml`: alta/média/baixa), risco de proximidade (baixo/médio/alto).

4. Confirmar o modo:
   - `adjacent_trend` se o usuário quer surfar a tendência (idealmente com evidência de que outras
     versões da mesma onda também recebem views — registrar em `reference.wave_evidence`);
   - `reference_adaptation` se a referência é interessante mas não há evidência de onda.

5. Criar `01_reference_triage/reference-triage.md` a partir de `templates/reference-triage.md`,
   incluindo o aviso: a métrica alta indica uma hipótese de embalagem ou emoção que merece estudo;
   não prova que a história deve ser reescrita nem que o vídeo continuará viral.

6. Atualizar `project.yaml` (campos de `reference`, `mode`) e `status: reference_filtered`.

7. Rodar `python3 scripts/validate_project.py projects/<id>`.

## Não fazer

- Não buscar vídeos, não trocar a referência escolhida pelo usuário.
- Não afirmar que o desempenho foi causado por um único fator.
- Não analisar a fundo (isso é `/analisar-referencia`) nem criar direções.
