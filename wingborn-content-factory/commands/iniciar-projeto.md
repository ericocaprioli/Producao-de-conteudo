# /iniciar-projeto

## Propósito

Criar um novo projeto editorial na pasta `projects/YYYY-MM-DD-slug/`, com o estado inicial
`input_received`. Este comando NÃO escreve roteiro e NÃO avança além da coleta de dados iniciais.

## Pré-condições

Nenhuma. Este é o primeiro comando de um novo projeto.

## Passos

1. Pergunte ao usuário somente os dados que faltarem (não repita perguntas cujo valor já foi
   fornecido na conversa ou pode ser assumido do padrão em `config/default-project.yaml`):
   - slug curto para o projeto (ex.: `traida-pelo-irmao`);
   - idioma do roteiro (padrão: `en`, conforme `config/default-project.yaml`);
   - premissa nova, se o usuário já tiver uma (campo `new_premise`, pode ficar vazio);
   - modo de protagonista: `core_female_protagonist` (padrão) ou `experimental_male_protagonist`
     — só usar o segundo se o usuário marcar explicitamente o projeto como experimento editorial;
   - unidade e faixa de caracteres por bloco, mantendo o padrão (3200–3500, incluindo espaços)
     se o usuário não pedir para alterar;
   - dados da referência, se já existirem: URL, título, visualizações, idade em horas, e a fonte
     desses números. **Nunca inventar visualizações, idade ou comentários.** Se o usuário informar
     os números manualmente (sem link de uma API/conector confiável), marcar
     `reference.views_source: manual`. Se nada for informado, deixar `null` e `views_source: unknown`.

2. Criar a estrutura de pastas do projeto:

   ```text
   projects/YYYY-MM-DD-slug/
   ├── 00_input/
   ├── 01_reference_triage/
   ├── 02_reference_analysis/
   ├── 03_original_directions/
   ├── 04_selected_direction/
   ├── 05_character_bible/
   ├── 06_script/
   ├── 07_retention/
   ├── 08_scene_prompts/
   ├── 09_seo/
   ├── 10_validation/
   └── 11_exports/
   ```

   Use a data de hoje para `YYYY-MM-DD`.

3. Copiar `templates/project.yaml` para `projects/YYYY-MM-DD-slug/00_input/project.yaml` e
   preencher os campos com os dados coletados no passo 1. Definir `status: input_received`,
   `approved_gates: []`.

4. Rodar `python3 scripts/validate_project.py projects/YYYY-MM-DD-slug` para confirmar que o
   `project.yaml` criado é válido. Corrigir e repetir se houver erro.

5. Confirmar ao usuário o caminho do projeto criado e o próximo comando esperado
   (`/triar-referencias`, se ainda não houver referência definida, ou `/analisar-referencia` se
   a referência já foi informada).

## O que este comando não deve fazer

- Não escrever roteiro, direções, título ou ficha de personagens.
- Não avançar `status` além de `input_received`.
- Não inventar dados de referência que o usuário não forneceu.
