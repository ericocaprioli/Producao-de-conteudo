# /criar-ficha

## Propósito

Criar a ficha de consistência (`character-bible.yaml`) que servirá de referência obrigatória
durante a escrita dos cinco blocos.

## Pré-condições

- Projeto no estado `title_approved`.

## Passos

1. A partir da direção selecionada (`04_selected_direction/selected-direction.md`), preencher
   `templates/character-bible.yaml`:

   ```yaml
   protagonist: {name, age, appearance, wound, strength, desire, fear, climax_choice}
   antagonist: {name, relation, public_power, hidden_motive}
   ally: {name, role, risk_taken}
   dragon: {name_rule, appearance, behavior, bond_rule}
   story:
     {symbol_object, opening_danger, hidden_truth, first_power_signal, second_power_signal,
      public_revelation, climax_location, final_repair}
   ```

   Todos os campos devem ser preenchidos de forma concreta e específica — evitar deixar campos
   vagos ou genéricos, já que esta ficha é a base da checagem de consistência automática.

2. Salvar `projects/<id>/05_character_bible/character-bible.yaml`.

3. **Parar** para aprovação explícita do usuário. Não escrever nenhum bloco de roteiro antes
   deste gate ser aprovado.

4. Após aprovação, atualizar `project.yaml`: `approved_gates` += `"character_bible"`,
   `status: bible_approved`.

## O que este comando não deve fazer

- Não escrever roteiro antes da aprovação da ficha.
- Não deixar campos-chave (nome, objeto-símbolo, aparência do dragão) vazios — eles são usados
  por `validate_consistency.py`.
