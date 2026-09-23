# /validar-bloco N

## Propósito

Executar e relatar o resultado da validação determinística do bloco N, sem reescrevê-lo.

## Pré-condições

- `06_script/block-0N.txt` existe.

## Passos

1. Rodar:

   ```bash
   python3 scripts/validate_blocks.py projects/<id> --block N
   ```

2. Rodar também `validate_consistency.py` se todos os blocos escritos até agora estiverem
   presentes (ele compara o roteiro inteiro disponível com a ficha, não apenas um bloco):

   ```bash
   python3 scripts/validate_consistency.py projects/<id>
   ```

3. Informar ao usuário, de forma objetiva:
   - número de caracteres do bloco N;
   - se está dentro de 3.200–3.500 (ou faixa configurada);
   - presença/ausência de marcadores técnicos proibidos;
   - contradições detectadas pelo `validate_consistency.py` (se aplicável);
   - status do gate: aprovado, ou pendente de correção/aprovação do usuário.

## O que este comando não deve fazer

- Não reescrever o bloco automaticamente — apenas relatar. A correção é feita via
  `/escrever-bloco N` novamente, após decisão do usuário.
