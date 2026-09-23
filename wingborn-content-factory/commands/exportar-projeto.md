# /exportar-projeto

## Propósito

Montar os arquivos finais de produção em `11_exports/`, prontos para narração (TTS), geração
de imagens e publicação.

## Pré-condições

- Cinco blocos escritos e válidos (`06_script/block-01.txt` .. `block-05.txt`).
- Idealmente `scenes_ready` e SEO gerado, mas o script de exportação funciona mesmo que
  cenas/SEO ainda não existam (avisa e pula essas partes).

## Passos

1. Rodar:

   ```bash
   python3 scripts/build_exports.py projects/<id>
   ```

   Este script:
   - valida os cinco blocos antes de exportar (recusa exportar se inválidos);
   - normaliza quebras de linha e remove marcadores de produção residuais;
   - gera `script_full.txt`, `block-01.txt`..`block-05.txt`, `tts_plain_text.txt`,
     `image-prompts.json`, `image-prompts-en.txt`, `thumbnail_prompt_en.txt`,
     `youtube_description.txt`, `tags.txt` e `production_manifest.json` em
     `projects/<id>/11_exports/`.

2. Confirmar que `tts_plain_text.txt` contém somente o texto narrado dos cinco blocos, na
   ordem, sem marcadores ou notas de produção.

3. Atualizar `project.yaml`: `approved_gates` += `"exports"`, `status: exports_ready`.

4. Informar ao usuário o caminho final: `projects/<id>/11_exports/`.

## O que este comando não deve fazer

- Não exportar blocos que falharem em `validate_blocks.py`.
- Não deixar marcadores de produção nos arquivos exportados.
