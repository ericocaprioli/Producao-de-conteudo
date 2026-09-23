# /escolher-direcao

## Propósito

Registrar a direção (A, B ou C) escolhida pelo usuário, sem reescrevê-la.

## Pré-condições

- `directions_ready` e escolha explícita do usuário.

## Passos

1. Copiar sem alterar:
   - a entrada escolhida de `03_original_directions/directions.yaml` para
     `04_selected_direction/selected-direction.yaml` (o mapeamento da direção, com `id`);
   - o trecho correspondente de `directions.md` para `04_selected_direction/selected-direction.md`.

2. Em `adjacent_trend`, rodar:

   ```bash
   python3 scripts/validate_trend_alignment.py projects/<id>
   ```

   - `ALIGNED` → adicionar o gate `trend_alignment`.
   - `REVIEW_REQUIRED` → mostrar os pontos ao usuário; o gate `trend_alignment` só entra com a
     confirmação explícita dele.
   - `TOO_CLOSE` ou `TOO_DISTANT` → não aprovar; voltar a `/criar-direcoes`.

3. Atualizar `project.yaml`: `selected_direction`, `approved_gates += direction`
   (e `trend_alignment` quando aplicável), `status: direction_selected`.

4. Registrar em `config/channel.yaml → used_combinations_log` um resumo curto da combinação
   estrutural (traidor, forma da traição, objeto-símbolo, mecanismo de revelação, reparação),
   para evitar saturação em projetos futuros.

5. Rodar `python3 scripts/validate_project.py projects/<id>` e indicar `/criar-titulos`.

## Não fazer

- Não reescrever nem "melhorar" a direção escolhida.
- Não misturar elementos das direções não escolhidas.
