# Producao-de-conteudo

Este repositório contém o **Wingborn Content Factory**, sistema de produção de vídeos do canal Wingborn Tales.

Antes de qualquer tarefa de vídeo, leia `wingborn-content-factory/CLAUDE.md` e siga as regras de lá. Todos os
comandos (`/iniciar-projeto`, `/escrever-bloco N` etc.), caminhos e scripts são relativos a
`wingborn-content-factory/`.

- **Novo vídeo:** quando o usuário mandar um link do YouTube, siga `wingborn-content-factory/commands/iniciar-projeto.md`.
- **Retomar um projeto:** rode `python3 scripts/validate_project.py projects/<id>` dentro de
  `wingborn-content-factory/` e continue a partir do próximo comando indicado.
- **Salvar sempre:** ao fim de cada etapa aprovada, faça commit e push, porque o estado vive nos arquivos, não na conversa.
