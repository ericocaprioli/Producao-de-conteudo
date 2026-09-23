# Guia do iniciante — do link do YouTube ao vídeo publicado

Este guia é para quem **nunca usou o Claude Code**. Siga na ordem. A parte "Uma vez só" leva uns
30 minutos; depois, cada vídeo segue a parte "A cada vídeo".

O que o sistema faz: você escolhe no YouTube um vídeo de história emocionante que esteja indo bem.
O Claude analisa o vídeo e cria uma **história original** de fantasia sombria com dragões, com
roteiro de cerca de 19 minutos, título, thumbnail, prompts de imagem e texto para o YouTube. Depois,
um notebook no Kaggle narra o roteiro com a **sua voz**.

---

## Você vai precisar de

| O quê | Para quê | Custo |
|---|---|---|
| Conta no **GitHub** com acesso a este repositório | guardar o sistema e os projetos | grátis |
| Conta no **Claude** com acesso ao **Claude Code** | o Claude conduz todo o roteiro | plano pago do Claude |
| Conta no **Kaggle** com **telefone verificado** | narrar com a sua voz (GPU grátis) | grátis |
| Uma gravação de **15–30 s** da sua voz | referência de voz | — |
| Uma ferramenta de imagens por IA | gerar as cenas e a thumbnail | varia |
| Um editor de vídeo (CapCut, DaVinci…) | juntar narração e imagens | varia |

---

## Uma vez só

### 1. Acesso ao repositório
- Peça ao dono do repositório para te adicionar como colaborador (GitHub → Settings →
  Collaborators) **ou** faça um *fork* para a sua conta.
- Confira que a branch padrão é **`main`**: no GitHub, **Settings → General → Default branch**.
  Se estiver outra, troque para `main`. Sem isso, o Claude pode abrir uma versão antiga do sistema.

### 2. Claude Code
1. Acesse **claude.ai/code** e entre com a sua conta.
2. Conecte o GitHub quando for pedido e autorize o acesso a este repositório.
3. Crie uma **sessão nova** escolhendo este repositório. Pronto: é aqui que você vai conversar.

### 3. Kaggle (para a narração)
1. Crie a conta em **kaggle.com**.
2. Clique na sua foto → **Settings** → **Phone Verification**. Sem o telefone verificado, o
   Kaggle não libera internet nem GPU, e a narração não funciona.
3. **Create → New Notebook → File → Import Notebook** → envie o arquivo
   `wingborn-content-factory/narration/kaggle_narracao.ipynb`. Peça ao Claude: *"me mande o
   notebook de narração"*. Dê um nome ao notebook e salve; nas próximas vezes é só abri-lo.

### 4. Sua gravação de voz
- 15 a 30 segundos, **sem música, sem eco, sem barulho**, perto do microfone.
- Pode ser **em português**: fale com naturalidade, no tom calmo de quem conta uma história à
  noite. O sistema narra em inglês fluente e usa só o **timbre** da sua voz.

---

## A cada vídeo

### Passo 1 — Escolha o vídeo base
No YouTube, escolha um vídeo de história emocionante (traição, abandono, humilhação, vingança…)
com **mais de 100 mil visualizações nas últimas 20 horas**. Copie o link. Anote as views e há
quantas horas foi publicado, se souber.

### Passo 2 — Comece no Claude Code
Abra uma **sessão nova** no Claude Code com este repositório e digite:

```text
/novo-video https://www.youtube.com/watch?v=XXXXXXXX
```

Se souber os números, acrescente, por exemplo: `— 180 mil views, publicado há 12 horas`.

Para ver projetos já começados, digite `/status`.

### Passo 3 — Responda às pausas
O Claude trabalha sozinho e **para quando precisa de você**. Nas pausas:

| Quando ele parar para… | O que você faz |
|---|---|
| perguntar o modo (se o vídeo tem mais de 20 h) | responda o modo que ele recomendar, ou pergunte a diferença |
| mostrar 3 direções de história (A, B, C) | responda **A**, **B** ou **C** |
| mostrar títulos | responda o número ou cole o título escolhido |
| pedir a thumbnail original | tire um print da thumbnail do vídeo de referência e cole na conversa |
| mostrar a ficha dos personagens e 6 perguntas | responda **"aprovado"** ou diga o que mudar |
| mostrar cada um dos 5 blocos do roteiro | leia e responda **"aprovado"** ou peça ajustes |
| mostrar o mapa de retenção | responda **"aprovado"** |

Em qualquer momento você pode escrever em português normal, como *"quero a protagonista mais
velha"* ou *"não entendi, explica de novo"*.

Tudo fica salvo no repositório. Se a conversa travar ou você fechar a aba, abra uma sessão nova
e digite `/status`: o Claude continua de onde parou.

### Passo 4 — Receba os arquivos
No fim, o Claude envia na conversa:

- `tts_plain_text.txt` — o roteiro para narrar;
- `image-prompts-en.txt` — os prompts das 20–30 cenas, em ordem;
- `thumbnail_prompt_en.txt` — o prompt da thumbnail;
- `youtube_description.txt` e `tags.txt` — para colar na publicação.

Clique em cada cartão para baixar.

### Passo 5 — Narre com a sua voz (Kaggle)
1. Abra o seu notebook no Kaggle.
2. No painel da direita, clique em **Upload** e arraste o `tts_plain_text.txt` e a sua gravação
   de voz. Dê um nome e clique em **Create**.
   - Nos próximos vídeos: em **Input**, passe o mouse sobre o dataset → **⋮** → **New Version** →
     troque só o `tts_plain_text.txt`.
3. Menu **Settings → Accelerator → GPU T4 x2** e **Settings → Internet → On**.
4. Clique em **Run All**. Leva uns 10–15 min instalando na primeira vez e uns 30 min narrando.
   Avisos amarelos na saída são normais.
5. Quando aparecer **"PRONTO"**: painel da direita → **Output → /kaggle/working** → ícone de
   atualizar → baixe `narracao_final.wav`, `narracao.srt` e `relatorio.txt`.
   **Baixe antes de fechar a aba**, porque a sessão apaga os arquivos.
   - Não quer esperar com a aba aberta? Use **Save Version → Save & Run All**: o Kaggle roda
     sozinho e guarda os arquivos na aba **Output** da versão.

### Passo 6 — Imagens, edição e publicação
1. Gere uma imagem por linha do `image-prompts-en.txt`, na ordem, e a thumbnail com o
   `thumbnail_prompt_en.txt`. O texto da thumbnail, se houver, entra depois, na edição.
2. No editor, coloque a `narracao_final.wav` e importe o `narracao.srt` como legenda. Cada cena
   corresponde a um trecho do roteiro, e o `.srt` mostra o tempo de cada trecho.
3. Publique com o título escolhido, a descrição de `youtube_description.txt` e as tags de
   `tags.txt`.

---

## Problemas comuns

| O que aconteceu | O que fazer |
|---|---|
| O Claude não conhece `/novo-video` ou não acha o sistema | confira se a branch padrão do repositório é `main` (Uma vez só, item 1) e abra uma sessão nova |
| Erro `No module named 'yaml'` | diga ao Claude: *"instale pyyaml"* |
| Kaggle: opção **Internet** bloqueada | verifique o telefone na conta do Kaggle |
| Kaggle: "GPU desligada" | **Settings → Accelerator → GPU T4 x2** e **Run All** de novo |
| Kaggle: "Chatterbox não carregou" | rode de novo a célula 1 e depois a 4 |
| Kaggle: "Não achei o roteiro / o áudio" | o dataset não está ligado: painel da direita → **Add Input** → escolha o seu dataset |
| A narração parou no meio | rode a célula 4 de novo: ela continua de onde parou, se a sessão ainda estiver aberta |
| A voz ficou com sotaque | confira se a célula 3 está com `"modo": "nativo"` |
| Um trecho da narração ficou estranho | veja `relatorio.txt`; na célula 3, `"usar_take": {número: 2}`, e rode as células 3 e 4 |
| Os arquivos sumiram do Output | a sessão foi encerrada; rode de novo, ou use **Save Version** da próxima vez |
| Não sabe o que fazer | escreva ao Claude: *"estou perdido, onde estamos e qual é o próximo passo?"* |

---

## Palavras que você vai ver

- **Sessão**: uma conversa com o Claude Code. Pode abrir quantas quiser; o trabalho fica salvo.
- **Repositório / branch / commit**: onde os arquivos ficam guardados no GitHub. O Claude salva
  sozinho; você não precisa mexer.
- **Gate / aprovação**: uma pausa em que o Claude precisa da sua decisão para continuar.
- **Dataset** (Kaggle): a pasta com os arquivos que o notebook lê (roteiro e voz).
- **Take**: uma versão gerada de um trecho da narração.
