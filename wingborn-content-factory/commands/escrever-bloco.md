# /escrever-bloco N

## Propósito

Escrever exatamente o bloco N (1 a 5) do roteiro, dentro da faixa de caracteres, em texto
narrativo limpo pronto para narração.

## Pré-condições

- Projeto no estado `bible_approved` ou `writing_in_progress`.
- `character-bible.yaml` aprovado.
- Se N > 1: bloco N-1 já validado e aprovado (não escrever fora de ordem).

## Regras de conteúdo

- Entre 3.200 e 3.500 caracteres, **incluindo espaços** (ou os limites definidos em
  `project.yaml` → `length`, se diferentes do padrão).
- Texto narrativo limpo, no idioma configurado em `project.yaml` → `language`.
- Sem título de bloco dentro do texto final.
- Sem marcadores de produção: nada de `[CENA]`, `[SCENE]`, `[PAUSE]`, `[PAUSA]`, `[MUSIC]`,
  `[SFX]`, `[NOTE]` ou instruções/comentários de produção misturados ao texto.
- Frases naturais para voz humana (evitar construções difíceis de narrar em voz alta).
- Tom calmo, dramático e visual, consistente com `config/channel.yaml`.
- Manter rigorosamente a ficha de consistência (`05_character_bible/character-bible.yaml`):
  nomes, idade, aparência, comportamento do dragão, objeto-símbolo.
- Incluir, dentro do bloco: ação, revelação, decisão, consequência e a próxima tensão (gancho
  para o bloco seguinte).
- Não repetir informação já entregue em blocos anteriores.

## Regras específicas do bloco 1

- Apresentar a injustiça central nos primeiros ~30 segundos de leitura (aproximadamente os
  primeiros parágrafos).
- Identificar o antagonista ou responsável pela injustiça.
- Plantar o objeto-símbolo, marca ou segredo antes de ~60 segundos de leitura.
- Criar uma pergunta urgente que puxe o espectador adiante.
- Entregar a primeira virada cedo (não guardar toda a tensão para o final do bloco).

## Passos

1. Ler `05_character_bible/character-bible.yaml` e os blocos anteriores já aprovados (se
   houver) antes de escrever.

2. Escrever o bloco solicitado como texto corrido, sem marcadores.

3. Salvar em `projects/<id>/06_script/block-0N.txt` (dois dígitos, ex. `block-01.txt`).

4. Rodar:

   ```bash
   python3 scripts/validate_blocks.py projects/<id> --block N
   ```

5. Se o validador falhar (contagem de caracteres fora da faixa, ou marcador técnico
   encontrado), corrigir o bloco e revalidar antes de prosseguir. Não passar ao próximo bloco
   sem validação limpa **e** aprovação explícita do usuário sobre o conteúdo.

6. Ao aprovar o bloco 1, atualizar `project.yaml`: `status: writing_in_progress`.

7. Quando os cinco blocos estiverem escritos, validados e aprovados, o próximo comando é
   `/revisar-retencao`.

## O que este comando não deve fazer

- Não escrever mais de um bloco por chamada.
- Não pular a validação.
- Não avançar para o próximo bloco sem aprovação do usuário no bloco atual.
