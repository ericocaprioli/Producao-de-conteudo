# /analisar-referencia

## Propósito

Produzir uma análise estrutural da referência selecionada — título, thumbnail, descrição,
transcrição e comentários disponíveis — separada de qualquer criação de roteiro.

## Pré-condições

- Projeto no estado `reference_filtered` ou posterior.
- `reference.url` (ou dados manuais equivalentes) preenchidos em `project.yaml`.

## Passos

1. Reunir os materiais disponíveis da referência: título, thumbnail (imagem ou descrição dela),
   descrição do vídeo, transcrição e comentários. Se algum material não estiver disponível,
   registrar isso explicitamente na análise em vez de inventar conteúdo. Salvar os materiais
   brutos fornecidos pelo usuário em `projects/<id>/02_reference_analysis/` (ex.:
   `transcript.txt`, `comments.txt`, `thumbnail-description.txt`) e referenciar os caminhos em
   `reference.thumbnail_file`, `reference.description_file`, `reference.transcript_file`,
   `reference.comments_file` no `project.yaml`.

2. Produzir a análise cobrindo:
   - promessa;
   - emoção principal;
   - público acionado;
   - mecanismo dos primeiros 30 segundos;
   - objeto ou segredo plantado;
   - perguntas abertas;
   - beats abstratos (função narrativa, não conteúdo específico);
   - pontos de mudança;
   - riscos de retenção;
   - motivos visuais;
   - comentários positivos, negativos e pedidos do público;
   - **lista explícita de elementos específicos proibidos de reutilizar**: nomes, frases,
     diálogos, personagens equivalentes, locais específicos, objetos específicos, sequência
     concreta de eventos, causa da traição, revelação, clímax e final.

3. Salvar:
   - `projects/<id>/02_reference_analysis/reference-analysis.md` (a partir de
     `templates/reference-analysis.md`), legível por humano;
   - `projects/<id>/02_reference_analysis/reference-analysis.json`, mesma informação em formato
     estruturado, com pelo menos as chaves: `promise`, `main_emotion`, `audience_trigger`,
     `first_30s_mechanism`, `planted_object_or_secret`, `open_questions`, `abstract_beats`,
     `turning_points`, `retention_risks`, `visual_motifs`, `comments_positive`,
     `comments_negative`, `comments_requests`, `forbidden_specific_elements`.

4. Atualizar `project.yaml`: `status: reference_analyzed`.

5. Rodar `python3 scripts/validate_project.py projects/<id>`.

## O que este comando não deve fazer

- Não escrever roteiro, cenas ou diálogos originais nesta etapa.
- Não propor direções novas (isso é `/criar-direcoes`).
- Não inventar transcrição, comentários ou métricas que não foram fornecidos.
