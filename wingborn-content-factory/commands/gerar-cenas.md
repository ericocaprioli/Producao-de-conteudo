# /gerar-cenas

## Propósito

Gerar os prompts de imagem para produção externa, em ordem e com continuidade visual.

## Pré-condições

- Projeto no estado `retention_approved` (cinco blocos, validação de retenção e aprovação do
  roteiro completos). **Não executar antes disso.**

## Passos

1. Determinar a quantidade de cenas: entre 20 e 30 para um vídeo de 15–20 minutos, salvo se o
   usuário pedir explicitamente outra quantidade (`config/default-project.yaml` →
   `scenes.min_count`/`max_count`). Não assumir 65 imagens ou qualquer outro número fixo para
   este formato sem pedido explícito.

2. Distribuir as cenas entre os cinco blocos de forma proporcional ao conteúdo de cada um.

3. Para cada cena, preencher o formato de `templates/scene-prompt.json`:

   ```json
   {
     "scene": 1,
     "block": 1,
     "script_excerpt": "",
     "function": "action|reaction|evidence|relationship|world|reward",
     "characters": [],
     "location": "",
     "emotion": "",
     "continuity_anchor": "",
     "prompt_en": "",
     "negative_prompt": "no text, no logo, no watermark"
   }
   ```

   - `script_excerpt`: trecho curto do bloco correspondente que a cena ilustra.
   - `continuity_anchor`: elemento fixo (objeto-símbolo, marca, cor do dragão etc.) repetido
     entre cenas para dar continuidade visual.
   - `prompt_en`: sempre em inglês, mesmo que o roteiro esteja em outro idioma.
   - Repetir a descrição visual fixa da protagonista e do dragão (da `character-bible.yaml`)
     nos prompts relevantes.
   - Não criar cenas genéricas sem função narrativa — toda cena deve ter uma `function` clara.

4. Salvar a lista completa em `projects/<id>/08_scene_prompts/scenes.json` (array JSON de
   objetos no formato acima, ordenado por `scene`).

5. Atualizar `project.yaml`: `approved_gates` += `"scenes"`, `status: scenes_ready`.

## O que este comando não deve fazer

- Não executar antes da aprovação de retenção.
- Não gerar quantidade de cenas fora de 20–30 sem pedido explícito do usuário.
- Não gerar prompt sem função narrativa definida.
