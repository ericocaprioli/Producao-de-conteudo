# /criar-ficha

## Propósito

Criar a ficha de consistência (`character-bible.yaml`) e, antes de liberar o roteiro, confirmar
que a embalagem aprovada é entregue pela história (gate `packaging`).

## Pré-condições

- `title_approved`.

## Passos

1. A partir de `04_selected_direction/selected-direction.yaml`, preencher
   `templates/character-bible.yaml` de forma concreta:

   ```yaml
   protagonist: {name, age, appearance, wound, strength, desire, fear, climax_choice}
   antagonist: {name, relation, public_power, hidden_motive}
   ally: {name, role, risk_taken}
   dragon: {name_rule, appearance, behavior, bond_rule}
   story: {symbol_object, opening_danger, hidden_truth, first_power_signal, second_power_signal,
           public_revelation, climax_location, final_repair}
   ```

   Nome, idade, aparência (com cores de cabelo/olhos), aparência do dragão (com cor das escamas),
   `antagonist.relation` (ex.: `mother`), `symbol_object` e `climax_location` são usados por
   `validate_consistency.py` — não deixar vagos.

2. Salvar `05_character_bible/character-bible.yaml` e **parar** para aprovação. Após aprovação:
   `approved_gates += character_bible`, `status: bible_approved`.

3. **Aprovação de embalagem (gate `packaging`)** — antes de qualquer bloco:
   - atualizar `thumbnail.prompt_en` em `09_seo/packaging.yaml` com a aparência fixa da ficha;
   - rodar `python3 scripts/validate_packaging_alignment.py projects/<id>`;
   - preencher `10_validation/packaging-approval.md` (de `templates/packaging-approval.md`) e
     perguntar ao usuário:

     ```text
     O novo pacote tem a mesma promessa emocional?
     O novo título tem especificidade e tensão equivalentes?
     A thumbnail é compreensível em um segundo?
     A composição visual é própria?
     O prompt não é uma paráfrase do original?
     A nova história realmente entrega a promessa?
     ```

   - Se alguma resposta for "não", corrigir a embalagem (voltar a `/criar-titulos`) ou a ficha
     antes de escrever. Com tudo "sim" e o validador sem `FAIL`: `approved_gates += packaging`.

4. Rodar `python3 scripts/validate_project.py projects/<id>` e indicar `/escrever-bloco 1`.

## Não fazer

- Não escrever roteiro antes dos gates `character_bible` e `packaging`.
