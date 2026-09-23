# /validar-bloco N

## Propósito

Rodar os validadores determinísticos e relatar o resultado do bloco N, sem reescrevê-lo.

## Pré-condições

- `06_script/block-0N.txt` existe.

## Passos

1. Rodar:

   ```bash
   python3 scripts/validate_blocks.py projects/<id> --block N
   python3 scripts/validate_consistency.py projects/<id>
   ```

2. Informar de forma objetiva:
   - número de caracteres e se está entre 3.200 e 3.500 (ou a faixa configurada);
   - marcadores técnicos encontrados;
   - elementos narrativos exigidos: no bloco 1, antagonista em ~30 s e objeto em ~60 s (checados
     pelo `validate_consistency.py`); nos demais, avaliação editorial de ação, revelação, decisão,
     consequência e próxima tensão, deixando claro que essa parte não é verificada por script;
   - contradições (ERRO) e avisos do `validate_consistency.py`;
   - status do gate: bloco em `approved_blocks` ou pendente.

## Não fazer

- Não reescrever o bloco. A correção é feita com `/escrever-bloco N`, após decisão do usuário.
