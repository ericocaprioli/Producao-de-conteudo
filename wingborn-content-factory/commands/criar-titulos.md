# /criar-titulos

## Propósito

Criar título, conceito de thumbnail e prompt visual com a mesma **função de viralidade** da
referência, sem copiar sua expressão. Preservar a arquitetura de clique:

```text
vítima facilmente identificável
+ injustiça familiar concreta
+ perigo visual forte
+ elemento dragônico/fantástico
+ segredo ou origem extraordinária
+ recompensa futura clara
```

A comparação com a referência é por funções, não por frases.

## Pré-condições

- `direction_selected` (e gate `trend_alignment` em `adjacent_trend`).

## Passos

1. Criar de 3 a 5 títulos em inglês, até ~100 caracteres, em ângulos diferentes (injustiça
   familiar, vulnerabilidade, dragão, segredo/herança, vingança ou reparação). Cada título deixa
   claro quem sofreu, quem causou o dano, qual evento ocorreu e qual inversão será entregue.

   Manter: intensidade emocional, nível de especificidade, relação de causa e consequência, tipo
   de curiosidade, promessa de inversão, linguagem natural.
   Alterar: redação, ordem das palavras, nomes próprios, detalhes concretos, mecanismo da virada,
   evento específico e, se necessário, a estrutura sintática.
   Evitar: "they" sem antecedente claro; promessa abstrata; título sobre a mãe quando a
   traidora real é outra pessoa; dragão ou vingança sem plantio na direção.

2. Para cada título, preencher a ficha em `09_seo/title-options.yaml`
   (de `templates/title-options.yaml`): `text`, `angle`, `viral_slots_preserved`,
   `concrete_details_changed`, `emotional_promise`, `curiosity_gap`,
   `reference_phrase_overlap` (`low` | `review_required`) e `promise_delivered_by`.

3. Criar `09_seo/packaging.yaml` (de `templates/packaging.yaml`):
   - `functional_tags` da proposta (mesmo vocabulário da referência);
   - `thumbnail.concept`: mostra o problema e sugere a recompensa, **nunca o clímax completo**;
     vulnerabilidade legível em um segundo, ameaça compreensível, dragão ou sinal fantástico
     reconhecível, contraste forte, uma pergunta visual sem resposta, espaço para texto curto;
   - `thumbnail.composition`: pose, enquadramento, ângulo de câmera, posição do dragão, cenário,
     objeto-símbolo, paleta/luz, expressão corporal, texto e layout — **todos diferentes** da
     thumbnail de referência;
   - `thumbnail.prompt_en`: protagonista e aparência consistente, ação/ameaça específica do novo
     roteiro, dragão ou sinal fantástico próprio, emoção dominante, composição original,
     iluminação e contraste, **16:9**, e `no text, no logo, no watermark` (salvo
     `text_intended: true`).

4. Rodar:

   ```bash
   python3 scripts/validate_title_promise.py --project projects/<id>
   python3 scripts/validate_packaging_alignment.py projects/<id>
   ```

   - Descartar ou reescrever títulos com `FAIL` (paráfrase da referência = `TEXT_TOO_CLOSE`;
     título genérico que abandona os slots = `PROMISE_TOO_GENERIC`).
   - `COMPOSITION_TOO_CLOSE` → refazer a composição da thumbnail.
   - `REVIEW_REQUIRED` → mostrar os pontos ao usuário junto com as opções.
   Dividir "mulher + dragão" com a referência é gênero, não cópia; o validador só conta
   dimensões específicas de composição.

5. Apresentar as opções com o resultado dos validadores e **parar** para a escolha do usuário.

6. Após a escolha: `selected_title` no `project.yaml`, rodar de novo
   `validate_packaging_alignment.py` (agora só o título escolhido), `approved_gates += title`,
   `status: title_approved`.

## Não fazer

- Não aprovar paráfrase da referência nem título genérico.
- Não afirmar que um título ou thumbnail vai melhorar o CTR.
