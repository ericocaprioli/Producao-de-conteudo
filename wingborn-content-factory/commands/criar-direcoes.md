# /criar-direcoes

## Propósito

Criar exatamente três direções narrativas originais (A, B, C), inspiradas na função emocional
da referência analisada, mas com cadeias causais concretas diferentes — nunca uma reescrita
disfarçada.

## Pré-condições

- Projeto no estado `reference_analyzed` ou posterior.
- `reference-analysis.json`/`.md` existentes.

## Guarda-corpo de originalidade (obrigatório antes de gerar qualquer direção)

Consultar `02_reference_analysis/reference-analysis.json` (`forbidden_specific_elements`) e
`config/channel.yaml` (`overused_combinations_to_avoid`, `used_combinations_log`).

Preservar somente em nível abstrato: emoção desejada, promessa de curiosidade, injustiça
familiar, medo versus verdade, mistério, progressão de revelação, sensação de vingança ou
reparação, função do dragão, ritmo geral de tensão e recompensa.

Nunca reutilizar: nomes, frases, diálogos, transcrição/tradução, personagens equivalentes,
locais específicos, objetos específicos, sequência concreta de eventos, mesma causa da
traição, mesma revelação, mesmo clímax, mesmo final, ou uma simples troca de espécie/nome/
cenário.

**Se o usuário pedir para "trocar só o tema", "manter a mesma sequência" ou uma reescrita muito
próxima da referência**: não obedecer diretamente. Explicar em poucas frases que o sistema
preserva apenas a função emocional, e seguir criando as três direções normalmente.

## Passos

1. Criar exatamente três direções (A, B, C). Cada uma deve alterar **pelo menos seis** dos
   itens a seguir em relação à referência: protagonista, idade ou situação social, parentesco
   do antagonista, causa da injustiça, objeto-símbolo, dragão, local, mentor, segredo,
   objetivo, risco do clímax, tipo de reparação.

2. Cada direção deve seguir a estrutura de `templates/directions.md`:

   ```text
   Logline
   Injustiça
   Objeto-símbolo
   Dom ou poder estigmatizado
   Mentor marginalizado
   Primeiro sinal de poder
   Segredo central
   Virada intermediária
   Clímax público
   Escolha moral
   Reparação final
   Diferenças em relação à referência
   ```

3. Evitar reforçar combinações já saturadas listadas em
   `config/channel.yaml` → `overused_combinations_to_avoid` e `used_combinations_log`
   (ex.: mãe assassina, Tiamat, herdeira, abandono infantil, "o sangue desperta o dragão"),
   a menos que a direção lhes dê um ângulo claramente novo.

4. Salvar `projects/<id>/03_original_directions/directions.md`.

5. Atualizar `project.yaml`: `status: directions_ready`.

6. **Parar** e pedir explicitamente ao usuário para escolher A, B ou C. Não prosseguir para
   `/escolher-direcao` sem essa escolha.

## O que este comando não deve fazer

- Não gerar mais ou menos que três direções.
- Não escrever roteiro.
- Não reutilizar elementos concretos da referência.
