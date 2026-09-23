# /analisar-referencia

## Propósito

Analisar a referência (título, thumbnail, descrição, transcrição e comentários disponíveis),
separada de qualquer criação de roteiro. Em `adjacent_trend`, também extrair o pacote viral.

## Pré-condições

- `reference_filtered`, com `reference.url` preenchido.

## Passos

1. Reunir os materiais fornecidos pelo usuário (ou lidos do próprio link informado) e salvar os
   brutos em `02_reference_analysis/` (`transcript.txt`, `comments.txt`, `description.txt`,
   `thumbnail-description.txt`). Preencher os caminhos em `reference.*_file`. Material ausente é
   registrado como ausente — nunca inventado.

2. Produzir a análise com: promessa; emoção principal; público acionado; mecanismo dos primeiros
   30 s; objeto ou segredo plantado; perguntas abertas; beats abstratos; pontos de mudança; riscos
   de retenção; motivos visuais; comentários positivos, negativos e pedidos; **lista de elementos
   específicos proibidos de reutilizar** (nomes, frases, diálogos, locais, objetos, sequência
   concreta, causa da traição, revelação, clímax, final).

3. Salvar:
   - `02_reference_analysis/reference-analysis.md` (de `templates/reference-analysis.md`);
   - `02_reference_analysis/reference-analysis.json` com as chaves `promise`, `main_emotion`,
     `audience_trigger`, `first_30s_mechanism`, `planted_object_or_secret`, `open_questions`,
     `abstract_beats`, `turning_points`, `retention_risks`, `visual_motifs`, `comments_positive`,
     `comments_negative`, `comments_requests`, `forbidden_specific_elements`.

4. **Somente em `adjacent_trend`:** criar `02_reference_analysis/viral-wave-package.yaml` a
   partir de `templates/viral-wave-package.yaml`:
   - `viral_wave`: papéis de vítima e traidor, tipo de traição, tipo de perigo, espetáculo visual,
     valor oculto, promessa emocional, recompensa futura, padrão de título e de thumbnail,
     `preserved_slots` (ids de `config/trend-rules.yaml → slots` que a onda vende) e
     `prohibited_events` (eventos concretos que nenhuma direção pode repetir);
   - `reference_surface`: título, nomes próprios, cadeia causal concreta em ordem, mecanismo de
     revelação, clímax, final e a thumbnail (descrição, texto e composição por dimensão);
   - `functional_tags`: promessa, emoção, gancho visual, gancho fantástico e lacuna de curiosidade
     da embalagem, no vocabulário de `config/trend-rules.yaml → packaging.functional_vocabulary`.

   Exemplo: para "a mãe abandonou a filha diante dos dragões, mas a criança possuía uma origem
   extraordinária", os slots são filha vulnerável, mãe traidora, abandono deliberado, dragões
   como perigo, espetáculo visual da criança diante da criatura, origem extraordinária e promessa
   de sobrevivência, reconhecimento ou vingança. Ver o fixture em
   `tests/fixtures/adjacent-trend-mother-dragons/`.

5. Atualizar `status: reference_analyzed` e rodar `python3 scripts/validate_project.py projects/<id>`.

## Não fazer

- Não escrever roteiro, cenas, diálogos ou direções.
- Não copiar trechos da transcrição para fora da pasta de análise.
