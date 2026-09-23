# /escolher-direcao

## Propósito

Registrar a direção (A, B ou C) escolhida pelo usuário, sem reescrevê-la.

## Pré-condições

- Projeto no estado `directions_ready`.
- Usuário informou A, B ou C.

## Passos

1. Copiar o conteúdo exato da direção escolhida de
   `03_original_directions/directions.md` para
   `projects/<id>/04_selected_direction/selected-direction.md`, sem alterar texto, sem
   "melhorar" ou reescrever.

2. Atualizar `project.yaml`:
   - `selected_direction`: a letra escolhida (ex.: `"B"`);
   - `approved_gates`: adicionar `"direction"`;
   - `status: direction_selected`.

3. Registrar em `config/channel.yaml` → `used_combinations_log` um resumo curto das escolhas
   estruturais usadas nesta direção (ex.: tipo de antagonista, tipo de objeto-símbolo, tipo de
   reparação), para apoiar a checagem de saturação em projetos futuros.

4. Rodar `python3 scripts/validate_project.py projects/<id>`.

5. Informar ao usuário que o próximo passo é `/criar-titulos`.

## O que este comando não deve fazer

- Não reescrever ou "melhorar" a direção escolhida.
- Não misturar elementos das direções não escolhidas.
