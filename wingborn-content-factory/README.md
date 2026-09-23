# Wingborn Content Factory

Sistema local de produção editorial para o canal **Wingborn Tales** (dark fantasy com dragões,
histórias de traição/reparação emocional). Reduz o tempo entre encontrar uma referência
emocional em alta e ter um roteiro original de 15–20 minutos, prompts de cena e SEO prontos
para produção.

Não é um painel web nem uma automação em segundo plano: é um conjunto de comandos, templates e
validadores determinísticos usados dentro do Claude Code, com todo o estado salvo em arquivos
em `projects/`.

## Requisitos

- Python 3.10+
- PyYAML (`pip install pyyaml`)

## Estrutura

```text
wingborn-content-factory/
├── CLAUDE.md              # instruções para o Claude Code interpretar os comandos
├── config/                # DNA do canal, padrões de projeto, regras de título e retenção
├── commands/               # especificação de cada comando /nome-do-comando
├── scripts/                 # validadores determinísticos (Python, sem dependência de rede)
├── templates/               # templates copiados para cada novo projeto
└── projects/                 # um diretório por projeto, criado por /iniciar-projeto
```

## Como iniciar um projeto

Dentro de uma sessão do Claude Code, com este diretório como contexto, digite:

```text
/iniciar-projeto
```

O Claude Code vai ler `commands/iniciar-projeto.md`, perguntar somente os dados que faltarem
(slug, idioma, premissa, modo de protagonista, faixa de caracteres, dados da referência se já
existirem) e criar `projects/YYYY-MM-DD-slug/` com o estado inicial `input_received`.

Fluxo completo, comando a comando:

```text
/iniciar-projeto
/triar-referencias
/analisar-referencia
/criar-direcoes        # para para você escolher A, B ou C
/escolher-direcao
/criar-titulos          # para para você escolher o título
/criar-ficha            # para para aprovação da ficha de consistência
/escrever-bloco 1       # repetir para 2, 3, 4, 5 — um bloco por vez, com validação e aprovação
/validar-bloco N        # a qualquer momento, para checar um bloco já escrito
/revisar-retencao
/gerar-cenas
/gerar-seo
/exportar-projeto
```

Cada comando só avança o estado do projeto (`status` em `project.yaml`) quando o gate
correspondente é aprovado. É seguro interromper a qualquer momento: o próximo comando lê o
`project.yaml` e as pastas já preenchidas para retomar de onde parou.

## Validadores

Rodar diretamente com Python, sem precisar do Claude Code:

```bash
python3 scripts/validate_project.py projects/<id>
python3 scripts/validate_blocks.py projects/<id> [--block N]
python3 scripts/validate_consistency.py projects/<id>
python3 scripts/validate_title_promise.py "Título candidato"
python3 scripts/build_exports.py projects/<id>
```

Todos retornam código de saída diferente de zero quando a validação falha.

## Limitações conhecidas

- Não há integração com nenhuma API do YouTube: visualizações, idade do vídeo e comentários
  são sempre entrada manual do usuário, marcados como `views_source: manual` quando não vierem
  de um conector confiável. O sistema nunca inventa esses números.
- `validate_consistency.py` é heurístico (busca por nome/idade/palavras-chave), não uma
  verificação semântica completa — ele aponta candidatos a revisão, não substitui leitura
  humana do roteiro.
- `validate_title_promise.py` usa listas de palavras-chave configuráveis
  (`config/title-rules.yaml`); quando a evidência é insuficiente ele retorna
  `REVIEW_REQUIRED` em vez de aprovar ou reprovar sem base.
- O sistema não afirma e não pode afirmar que qualquer escolha (título, thumbnail, direção)
  vai melhorar o CTR — isso só pode ser avaliado com dados reais de vídeos publicados.
- Fases futuras (fora deste MVP): conectores para métricas do YouTube, geração automática de
  imagens, publicação automática. Ver `CLAUDE.md` → "Fora de escopo neste MVP".
