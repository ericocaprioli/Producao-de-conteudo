# Narração com a sua voz (Kaggle + Chatterbox)

Transforma o `11_exports/tts_plain_text.txt` de um projeto em `narracao_final.wav`, usando uma
gravação curta da sua voz como referência.

## Como a voz é gerada (modo `nativo`, o padrão)

1. Cada trecho é narrado em **inglês fluente** pela voz padrão do Chatterbox, que é nativa.
2. Em seguida é **convertido para o seu timbre** (conversão de voz do próprio Chatterbox), usando a
   sua gravação como referência.

A pronúncia e o ritmo vêm da voz nativa, e o timbre é o seu. Por isso a sua gravação **pode ser
em português**: 15–30 s, voz limpa, no tom calmo de narrador. Só cerca de 10 s são aproveitados;
mais áudio não melhora esse modo.

Opcional: para outra voz base em inglês, adicione ao dataset um arquivo chamado `voz_base`
(`.wav`, `.mp3` etc.), **somente com licença de uso**; nunca a voz de outra pessoa sem autorização.
Com `"modo": "clonagem"` o notebook volta a imitar a sua gravação direto, herdando o sotaque dela.

## Uma vez só

1. Crie uma conta no Kaggle e **verifique o telefone** (sem isso não há internet nem GPU).
2. **Create → New Notebook → File → Import Notebook** e envie `narration/kaggle_narracao.ipynb`.
   Salve o notebook: da próxima vez é só abri-lo.

## A cada vídeo

1. **Datasets → New Dataset** com dois arquivos:
   - o `tts_plain_text.txt` do projeto (`projects/<id>/11_exports/`);
   - um áudio da sua voz de 15–30 s (limpo, sem música, sem eco).

   Para o próximo vídeo, basta **atualizar o arquivo de texto** desse mesmo dataset (New Version).
2. No notebook: **Add Input** → o dataset. **Settings → Accelerator → GPU** e **Internet → On**.
3. Clique em **Run All**. Não há "Restart session" em nenhum momento.
   - Para testar a voz antes: na célula 3, `"so_primeiros": 3`.
   - Para fechar o navegador enquanto gera: **Save Version → Save & Run All (Commit)**. O resultado
     fica guardado na aba **Output** daquela versão.
4. Baixe em **Output**:
   - `narracao_final.wav` — a narração, com volume no padrão do YouTube;
   - `narracao.srt` — legenda com o tempo de cada trecho (use para posicionar as cenas e como legenda do vídeo);
   - `relatorio.txt` — duração total e os trechos que merecem ser ouvidos.

## Se um trecho ficar ruim

O script mede a duração de cada trecho e refaz sozinho os que saem muito longos (alucinação) ou
muito curtos (corte). Os que continuarem estranhos aparecem em `relatorio.txt` e na célula 5,
onde dá para ouvir as takes. Para escolher outra take: na célula 3, `"usar_take": {12: 2}`, e
rode as células 3 e 4 de novo. Só aquele trecho é refeito.

Mudar uma frase do roteiro também refaz só aquele trecho. Mudar a voz ou os ajustes de emoção
refaz tudo.

## Para quem mantém o projeto

`narrar.py` é a única fonte do código. Depois de alterá-lo, rode
`python3 narration/build_notebook.py` para regenerar o `.ipynb`; os testes acusam se os dois
estiverem diferentes.
