# /revisar-retencao

## Propósito

Criar o mapa de retenção dos 15–20 minutos do vídeo, garantindo ritmo de tensão e recompensa
adequado antes de gerar cenas e SEO.

## Pré-condições

- Projeto no estado `script_approved` (cinco blocos escritos, validados por
  `validate_blocks.py` e aprovados pelo usuário).

## Passos

1. A partir de `config/retention-rules.yaml` e do conteúdo real dos cinco blocos, criar
   `projects/<id>/07_retention/retention-map.md` (a partir de `templates/retention-map.md`)
   com marcações aproximadas:

   ```text
   00:00-00:30 — injustiça e promessa
   00:30-01:00 — objeto, marca ou segredo plantado
   01:00-03:00 — consequência e primeira pergunta
   03:00-06:00 — primeira recompensa ou demonstração de poder
   06:00-09:00 — humilhação, descoberta ou risco
   09:00-12:00 — revelação intermediária e aproximação do dragão
   12:00-16:00 — confronto e clímax
   16:00-20:00 — reparação e encerramento, ajustado à duração real
   ```

   Ajustar os tempos à duração real estimada do roteiro (contagem de caracteres/palavras dos
   cinco blocos), mantendo ordem e função de cada trecho.

2. Identificar no mínimo dois microclímax antes do clímax final, e confirmar que não há
   intervalos longos (mais de ~2 minutos) apenas de explicação sem tensão.

3. Se o roteiro não atender a esses critérios, não editar o roteiro automaticamente: reportar
   ao usuário onde o ritmo falha e sugerir ajustes pontuais para aprovação antes de alterar
   qualquer bloco.

4. Após aprovação do usuário, atualizar `project.yaml`: `approved_gates` += `"retention"`,
   `status: retention_approved`.

## O que este comando não deve fazer

- Não gerar cenas ou SEO nesta etapa.
- Não alterar os blocos de roteiro sem aprovação explícita do usuário.
