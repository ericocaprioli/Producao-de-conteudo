# Producao-de-conteudo

Este repositório contém o **Wingborn Content Factory**, sistema de produção de vídeos do canal Wingborn Tales.

- **Qualquer tarefa de vídeo:** siga a skill `.claude/skills/wingborn-video/SKILL.md`. Ela conduz o fluxo
  inteiro (link → roteiro → exportação → narração no Kaggle) com as pausas de aprovação.
- **Usuário iniciante:** o usuário pode nunca ter usado o Claude Code. Explique cada pausa em português simples
  e indique o próximo passo. O guia dele é `GUIA-INICIANTE.md`.
- **Comandos:** `/novo-video <link>`, `/status` e um comando por etapa em `.claude/commands/`. Cada um aponta
  para a especificação em `wingborn-content-factory/commands/`.
- **Regras:** leia `wingborn-content-factory/CLAUDE.md` antes de qualquer etapa. Caminhos e scripts são
  relativos a `wingborn-content-factory/`.
- **Retomar um projeto:** rode `python3 scripts/validate_project.py projects/<id>` dentro de
  `wingborn-content-factory/` e continue a partir do próximo comando indicado.
- **Salvar sempre:** ao fim de cada etapa aprovada, faça commit e push, porque o estado vive nos arquivos, não na
  conversa.
- **Ao mudar a skill, os comandos ou as etapas:** rode `python3 -m unittest discover -s tests` em
  `wingborn-content-factory/` (há testes que conferem se os três estão em sincronia).
