# /criar-direcoes

## Propósito

Criar exatamente três direções (A, B, C). Em `adjacent_trend`, elas ficam próximas do pacote
viral (mesma onda) e têm realização narrativa própria (nova cadeia causal, revelação, clímax e
final). O objetivo é produzir **adaptações adjacentes** — nem histórias genéricas, nem cópias
disfarçadas.

## Pré-condições

- `reference_analyzed` (ou `input_received` em `original_channel_story`).
- Em `adjacent_trend`: `02_reference_analysis/viral-wave-package.yaml` existe.

## Originalidade × distanciamento excessivo

Sempre proibido: nomes, frases, diálogos, transcrição/tradução, personagens equivalentes, locais
e objetos específicos, sequência concreta de eventos, mesma causa da traição, mesma revelação,
mesmo clímax, mesmo final, e simples troca de espécie/nome/cenário.

**Não** rejeitar uma história só porque ela mantém "mãe + filha + dragões": isso são slots de
mercado. Rejeitar quando a nova história repete a **sequência concreta** da referência.

Se o usuário pedir "trocar só o tema", "manter a mesma sequência" ou reescrita muito próxima:
não obedecer diretamente; explicar em poucas frases que o sistema preserva apenas a função
emocional (e, em `adjacent_trend`, os slots da onda) e seguir com três direções de cadeias causais
diferentes.

Consultar também `config/channel.yaml` (`overused_combinations_to_avoid`, `used_combinations_log`).

## Passos por modo

### `adjacent_trend`

1. Gerar três direções com distância controlada:
   - **A — proximidade alta e segura** (`proximity_level: high`): manter **5** slots; alterar
     profundamente cadeia causal, revelação, clímax e final.
   - **B — proximidade média** (`medium`): manter **4** slots; alterar idade, local, forma do
     abandono, função do dragão e reparação.
   - **C — proximidade moderada** (`moderate`): manter **4** slots; alterar ambiente, parentesco
     secundário, objeto, mitologia e caminho até a revelação.

2. Cada direção apresenta: logline; slots preservados; elementos concretos alterados; cadeia
   causal nova em **7–10 passos**; mecanismo novo da revelação; clímax novo; final novo; risco de
   proximidade; justificativa de por que ainda pertence à mesma onda; título provisório; conceito
   de thumbnail. Mais os campos editoriais: injustiça, objeto-símbolo, dom estigmatizado, mentor
   marginalizado, primeiro sinal de poder, segredo central, virada intermediária, escolha moral.

   Alterar obrigatoriamente nomes, personagens concretos, frases, diálogos, cadeia causal,
   mecanismo da revelação, sequência de eventos, objeto/símbolo, clímax, final, composição da
   thumbnail e texto do título.

3. Salvar `03_original_directions/directions.yaml` (de `templates/directions.yaml`; é a fonte
   de verdade dos validadores) e `directions.md` (versão legível, de `templates/directions.md`).

4. Rodar:

   ```bash
   python3 scripts/validate_trend_alignment.py projects/<id> --all
   ```

   - `TOO_CLOSE` → refazer a direção com outra cadeia causal/revelação/clímax/final.
   - `TOO_DISTANT` → recolocar slots da onda (mínimo 4) sem copiar eventos.
   - `REVIEW_REQUIRED` → completar os campos apontados ou explicar ao usuário por que a decisão
     precisa de julgamento humano.
   Repetir até as três ficarem `ALIGNED`, ou até restar apenas `REVIEW_REQUIRED` justificado.
   Incluir a classificação de cada direção no `directions.md`.

### `reference_adaptation`

Três direções preservando emoção e padrões abstratos, com maior distância de superfície: cada
uma altera pelo menos seis itens (protagonista, idade/situação social, parentesco do antagonista,
causa da injustiça, objeto-símbolo, dragão, local, mentor, segredo, objetivo, risco do clímax,
tipo de reparação). O validador de tendência não se aplica.

### `original_channel_story`

Três direções apenas a partir do DNA do canal (`config/channel.yaml`), sem referência.

## Final (todos os modos)

- Atualizar `status: directions_ready`.
- **Parar** e pedir ao usuário para escolher A, B ou C.

## Não fazer

- Não gerar mais nem menos que três direções.
- Não escrever roteiro.
- Não apresentar como `ALIGNED` uma direção que o validador não classificou assim.
