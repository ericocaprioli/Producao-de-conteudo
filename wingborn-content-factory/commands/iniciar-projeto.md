# /iniciar-projeto

## Propósito

Criar um novo projeto em `projects/YYYY-MM-DD-slug/` com o estado inicial `input_received`.
Não escreve roteiro e não avança além da coleta de dados iniciais.

## Pré-condições

Nenhuma.

## Passos

1. Perguntar somente o que faltar (não repetir o que já foi dito na conversa nem o que tem
   padrão em `config/default-project.yaml`):
   - slug curto (ex.: `mae-abandona-filha-dragoes`);
   - idioma do roteiro (padrão `en`);
   - premissa nova, se já existir (`new_premise`, pode ficar vazio);
   - modo de protagonista: `core_female_protagonist` (padrão) ou `experimental_male_protagonist`
     — o segundo só se o usuário marcar o projeto como experimento editorial;
   - unidade e faixa por bloco — manter 3.200–3.500 caracteres com espaços se não houver pedido;
   - link da referência escolhida manualmente pelo usuário no YouTube, e as métricas que ele
     tiver (visualizações, idade em horas).
   - modo de criação (`mode`), decidido assim, perguntando só se ficar ambíguo:
     - usuário forneceu referência e quer surfar a tendência → `adjacent_trend`;
     - referência interessante, mas sem evidência de onda → `reference_adaptation`;
     - sem referência → `original_channel_story`.

2. **Não pesquisar vídeos.** O sistema não busca, seleciona, monitora nem faz scraping do
   YouTube. Ele trabalha só com o link e os materiais que o usuário fornece.

3. Criar as pastas:

   ```text
   projects/YYYY-MM-DD-slug/
   ├── 00_input/  01_reference_triage/  02_reference_analysis/  03_original_directions/
   ├── 04_selected_direction/  05_character_bible/  06_script/  07_retention/
   └── 08_scene_prompts/  09_seo/  10_validation/  11_exports/
   ```

4. Copiar `templates/project.yaml` para `00_input/project.yaml` e preencher:
   - `id`, `mode`, `language`, `channel_mode`, `length`, `new_premise`;
   - `reference.url` e `reference.title`, se informados;
   - métricas: valor informado pelo usuário → número + fonte `manual`;
     não informado → `null` + fonte `unknown`. **Nunca inventar números.**
   - `status: input_received`, `approved_gates: []`, `approved_blocks: []`.

5. Rodar `python3 scripts/validate_project.py projects/YYYY-MM-DD-slug` e corrigir até passar.

6. Informar o caminho criado e o próximo comando (`/triar-referencia`, ou `/criar-direcoes`
   em `original_channel_story`).

## Não fazer

- Não escrever roteiro, direções, título ou ficha.
- Não avançar `status` além de `input_received`.
- Não buscar vídeos nem inventar métricas.
