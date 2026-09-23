---
name: wingborn-video
description: Produz um vídeo completo do canal Wingborn Tales (dark fantasy com dragões) a partir de um link do YouTube escolhido pelo usuário — triagem, análise, 3 direções, título e thumbnail, ficha, 5 blocos de roteiro validados, retenção, cenas, SEO, exportação e narração no Kaggle. Use quando o usuário colar um link do YouTube, pedir um vídeo/roteiro novo, quiser retomar um projeto em projects/, ou perguntar como narrar com a própria voz.
---

# Wingborn Video — do link ao vídeo pronto

Você conduz o usuário por um fluxo com **pausas obrigatórias**. O usuário pode nunca ter usado o
Claude Code: explique cada pausa em português simples, diga exatamente o que ele precisa responder
e nunca avance uma etapa de aprovação sem a resposta dele.

Todo o sistema fica em `wingborn-content-factory/`. Antes de começar, leia
`wingborn-content-factory/CLAUDE.md` (regras de originalidade, métricas e gates). Cada etapa tem a
especificação completa em `wingborn-content-factory/commands/<etapa>.md`: leia o arquivo da etapa
antes de executá-la. Rode os scripts **de dentro de `wingborn-content-factory/`**.

## 0. Antes de tudo

1. Se o usuário não mandou link nem nome de projeto, rode o `/status` (liste `projects/` e rode
   `python3 scripts/validate_project.py projects/<id>` em cada um) e pergunte: novo vídeo ou
   continuar um existente?
2. Projeto existente: rode `validate_project.py` e continue a partir de "próximo comando".
3. Se `import yaml` falhar: `pip install pyyaml`.

## 1. O fluxo (pare nos ⏸)

| # | Etapa (arquivo em commands/) | Pausa para o usuário |
|---|---|---|
| 1 | `iniciar-projeto` — pasta, `project.yaml`, modo | só se faltar dado essencial |
| 2 | `triar-referencia` — métricas lidas do próprio link ou `manual`/`unknown` | ⏸ escolher o modo se o filtro de 20 h/100 mil falhar |
| 3 | `analisar-referencia` — transcrição inteira, comentários, proibidos | — |
| 4 | `criar-direcoes` — exatamente 3 (A, B, C) | ⏸ escolher A, B ou C |
| 5 | `escolher-direcao` — cópia fiel + `used_combinations_log` | — |
| 6 | `criar-titulos` — 3–5 fichas + thumbnail + prompt | ⏸ escolher o título; pedir print da thumbnail original |
| 7 | `criar-ficha` — ficha + 6 perguntas de embalagem | ⏸ aprovar ficha e embalagem |
| 8 | `escrever-bloco N` (N = 1…5) — um por vez | ⏸ aprovar cada bloco |
| 9 | `revisar-retencao` — tempos reais a 15 caracteres/s | ⏸ aprovar o mapa |
| 10 | `gerar-cenas` — 20–30 cenas com aparência fixa | — |
| 11 | `gerar-seo` — descrição 120–180 palavras, 3 hashtags, 12–15 tags | — |
| 12 | `exportar-projeto` — `scripts/build_exports.py` | entregar os arquivos (ver 3) |
| 13 | Narração no Kaggle (ver 4) | guiar o usuário na tela dele |

Depois de **cada** etapa: rode `python3 scripts/validate_project.py projects/<id>`, faça commit
e push (o estado vive nos arquivos, não na conversa) e diga ao usuário em uma frase o que vem
depois.

## 2. Regras que mais causam erro

- **Não buscar vídeos no YouTube.** Só ler metadados/transcrição/comentários do link informado
  (ferramentas NexLev `youtube_video_details`, `get_video_transcript`, `youtube_video_comments`,
  se disponíveis). Métrica sem fonte = `null` + `unknown`. Transcrição grande: salve em
  `02_reference_analysis/transcript.txt` agrupada por minuto e leia **inteira** antes de analisar.
- **Blocos: 3.200–3.500 caracteres.** Escreva, rode `validate_blocks.py --block N` e
  `validate_consistency.py`; ajuste até passar **antes** de mostrar ao usuário. No bloco 1, o
  antagonista (nome ou parentesco) aparece nos primeiros ~450 caracteres e o objeto-símbolo nos
  primeiros ~900.
- **Nomes de parentesco no título** precisam existir na direção (ex.: "stepsister", não "sister",
  se ela é meia-irmã). Título ≤ 100 caracteres.
- **Thumbnail:** mostra o problema, nunca o clímax; composição diferente em todas as dimensões.
- **Nunca** marcar um gate (`approved_gates`) sem a resposta explícita do usuário.

## 3. Entregar os arquivos ao usuário

O usuário não navega em pastas. Ao exportar, envie com a ferramenta de envio de arquivos
(`SendUserFile`) pelo menos: `11_exports/tts_plain_text.txt`, `image-prompts-en.txt`,
`thumbnail_prompt_en.txt`, `youtube_description.txt`, `tags.txt`.

## 4. Narração (fora do Claude, no Kaggle)

Guia completo: `wingborn-content-factory/narration/README.md`. Resumo para conduzir o usuário:

1. Uma vez: conta no Kaggle com **telefone verificado**; *Create → New Notebook → File → Import
   Notebook* com `narration/kaggle_narracao.ipynb` (envie o arquivo a ele).
2. Dataset: no painel da direita do notebook, botão **Upload** → arrastar `tts_plain_text.txt` e
   uma gravação de 15–30 s da voz dele (pode ser em português) → **Create**.
3. **Settings → Accelerator → GPU T4 x2** e **Settings → Internet → On**.
4. **Run All**. Modo padrão `nativo`: inglês fluente convertido para o timbre dele (sem sotaque).
   Leva ~30 min para ~19 min de áudio. Avisos amarelos das bibliotecas são normais.
5. Ao ver "PRONTO": **Output → /kaggle/working** → atualizar → baixar `narracao_final.wav`,
   `narracao.srt`, `relatorio.txt` **antes de fechar a aba**.
6. Ritmo: `"velocidade"` na célula 3 (padrão 0.9, 10% mais lenta que o modelo, escolha do
   usuário; 1.1 = 10% mais rápida). Mudar só ela não regera trechos: as células 3 e 4 remontam
   áudio e legenda em segundos, se a sessão ainda estiver aberta.

Se o usuário colar a saída do Kaggle, leia e diga o que é normal e o que é erro. Se mudar
`narration/narrar.py`, rode `python3 narration/build_notebook.py` e os testes.

## 5. Conferência final

Antes de dizer que terminou: `python3 -m unittest discover -s tests` (em
`wingborn-content-factory/`) passa, `validate_project.py` mostra `exports_ready`, tudo commitado
e enviado, e o usuário recebeu os arquivos e o próximo passo (narrar, gerar imagens, editar,
publicar). Não prometa efeito sobre CTR.
