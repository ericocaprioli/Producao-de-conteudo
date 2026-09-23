# Produção de conteúdo — Wingborn Tales

Sistema que transforma um vídeo do YouTube em alta, escolhido por você, em um vídeo original de
dark fantasy com dragões: roteiro de ~19 min, título, thumbnail, prompts de cena, SEO e narração
com a sua voz.

**Nunca usou? Comece por [GUIA-INICIANTE.md](GUIA-INICIANTE.md).**

Uso rápido, numa sessão do Claude Code aberta neste repositório:

```text
/novo-video <link do YouTube>     # faz o vídeo do começo ao fim, parando nas suas escolhas
/status                           # mostra os projetos e onde cada um parou
```

| Onde | O quê |
|---|---|
| `.claude/skills/wingborn-video/` | a skill que conduz o fluxo inteiro |
| `.claude/commands/` | os comandos `/novo-video`, `/status` e um por etapa |
| `wingborn-content-factory/` | regras, etapas, validadores, templates e projetos |
| `wingborn-content-factory/narration/` | notebook do Kaggle para narrar com a sua voz |
