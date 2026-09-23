# /escrever-bloco N

## Propósito

Escrever exatamente o bloco N (1 a 5), dentro da faixa de caracteres, em texto narrativo limpo
pronto para a narração com a voz do usuário.

## Pré-condições

- Gates `character_bible` e `packaging` aprovados (`bible_approved` ou `writing_in_progress`).
- Se N > 1: bloco N−1 em `approved_blocks` (não escrever fora de ordem).

## Regras

- Entre 3.200 e 3.500 caracteres, contando espaços, pontuação e quebras de linha internas
  (ou a faixa de `project.yaml → length`).
- Texto narrativo limpo no idioma de `project.yaml → language`.
- Sem título de bloco, sem `[CENA]`, `[PAUSE]`, cabeçalhos `#`, instruções ou comentários.
- Frases naturais para voz humana; tom calmo, dramático e visual.
- Manter a ficha: nomes, idade, aparência, dragão, objeto-símbolo.
- Incluir ação, revelação, decisão, consequência e a próxima tensão.
- Não repetir informação já entregue.

### Bloco 1 (obrigatório)

A abertura tem a mesma **função de viralidade** da embalagem aprovada (vítima identificável,
injustiça familiar concreta, perigo, sinal dragônico, segredo, promessa), sem copiar a abertura
da referência:

- injustiça nos primeiros ~30 s;
- antagonista ou responsável identificado (nome ou parentesco) nos primeiros ~30 s;
- objeto, marca ou segredo plantado antes de ~60 s;
- uma pergunta urgente;
- a primeira virada cedo.

A conversão de tempo usa `config/retention-rules.yaml → narration_chars_per_second`
(padrão 15 caracteres/s: 30 s ≈ 450 caracteres, 60 s ≈ 900).

## Passos

1. Ler a ficha, `09_seo/packaging.yaml`, a direção escolhida e os blocos já aprovados.
2. Escrever o bloco e salvar em `06_script/block-0N.txt`.
3. Rodar:

   ```bash
   python3 scripts/validate_blocks.py projects/<id> --block N
   python3 scripts/validate_consistency.py projects/<id>
   ```

4. Se falhar, corrigir e revalidar antes de mostrar ao usuário. Informar a contagem final.
5. **Parar** para aprovação. Com aprovação: `approved_blocks += N`; no bloco 1,
   `status: writing_in_progress`.
6. Depois do bloco 5 aprovado: rodar `validate_blocks.py` (todos) e `validate_consistency.py`;
   se passarem, `approved_gates += script` e `status: script_approved`. Próximo:
   `/revisar-retencao`.

## Não fazer

- Não escrever mais de um bloco por chamada nem pular a validação.
- Não avançar sem aprovação do bloco atual.
