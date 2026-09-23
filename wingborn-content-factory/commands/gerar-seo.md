# /gerar-seo

## Propósito

Gerar os textos de SEO e o prompt de thumbnail para publicação.

## Pré-condições

- Projeto no estado `scenes_ready` ou posterior (título já aprovado em `title_approved`).

## Passos

1. Criar descrição do vídeo no idioma configurado, entre 120 e 180 palavras
   (`config/default-project.yaml` → `seo.description_min_words`/`max_words`):
   - primeiras duas linhas devem conter a promessa e palavras do título aprovado;
   - resto da descrição pode expandir contexto sem entregar o clímax.

2. Criar três hashtags relevantes.

3. Criar uma call to action calma, sem spoiler (ex.: convite para assistir até o fim, se
   inscrever, comentar — sem revelar a reparação final).

4. Criar de 12 a 15 tags (limite máximo configurável em
   `config/default-project.yaml` → `seo.tags_max`/`tags_hard_limit`).

5. Finalizar o prompt de thumbnail a partir de `09_seo/packaging.yaml → thumbnail.prompt_en`
   (aprovado no gate `packaging`), sem mudar a composição aprovada: protagonista com a aparência
   da ficha, ameaça específica do roteiro, dragão próprio, emoção dominante, iluminação e
   contraste, 16:9, `no text, no logo, no watermark`. Mostrar o problema e sugerir a
   recompensa, nunca o clímax completo. Rodar de novo
   `python3 scripts/validate_packaging_alignment.py projects/<id>` e corrigir qualquer `FAIL`.

6. Salvar em `projects/<id>/09_seo/`:
   - `description.txt` (descrição + CTA + hashtags juntos, como ficaria publicado);
   - `tags.txt` (uma tag por linha);
   - `thumbnail-prompt.txt` (o `prompt_en` final).

7. Atualizar `project.yaml` conforme necessário (nenhuma mudança de `status` obrigatória
   aqui, a menos que o projeto ainda não tivesse `scenes_ready`).

## O que este comando não deve fazer

- Não revelar o clímax ou a reparação final na descrição, hashtags ou thumbnail.
- Não ultrapassar o limite de tags configurado.
