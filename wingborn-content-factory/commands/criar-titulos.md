# /criar-titulos

## Propósito

Criar de três a cinco opções de título em inglês, alinhadas à direção escolhida, e um conceito
de thumbnail correspondente.

## Pré-condições

- Projeto no estado `direction_selected`.

## Passos

1. Criar de 3 a 5 títulos, cada um com até ~100 caracteres (`config/title-rules.yaml` →
   `max_length_chars`), cobrindo ângulos diferentes:
   - injustiça familiar;
   - vulnerabilidade;
   - dragão;
   - segredo/herança;
   - vingança ou reparação.

   Cada título deve declarar ou sugerir claramente: quem sofreu, quem causou o dano, qual
   evento ocorreu, e qual inversão será entregue.

2. Evitar:
   - "they" sem antecedente claro;
   - promessa abstrata sem sujeito nem evento;
   - títulos que falem da mãe quando a protagonista real da direção escolhida é outra pessoa;
   - dragão ou vingança mencionados no título sem terem sido plantados na direção escolhida.

3. Rodar, para cada título candidato:

   ```bash
   python3 scripts/validate_title_promise.py "<título>"
   ```

   Descartar ou corrigir títulos com veredito `FAIL`. Um veredito `REVIEW_REQUIRED` não é
   reprovação automática — revisar manualmente se o sinal ausente está implícito no título.

4. Criar um conceito de thumbnail (descrição textual, em inglês) que corresponda ao gancho do
   título escolhido, sem revelar o clímax inteiro.

5. Salvar `projects/<id>/09_seo/title-options.md` com as opções, o veredito de cada uma, e o
   conceito de thumbnail proposto.

6. **Parar** e pedir ao usuário para escolher um dos títulos.

7. Após a escolha, atualizar `project.yaml`: `selected_title`, `approved_gates` +=
   `"title"`, `status: title_approved`.

## O que este comando não deve fazer

- Não aprovar título automaticamente sem a escolha do usuário.
- Não afirmar qualidade do título sem evidência (usar `REVIEW_REQUIRED` quando a checagem por
  regras não for conclusiva).
