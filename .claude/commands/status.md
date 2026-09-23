---
description: Mostra os projetos existentes, em que etapa cada um parou e o próximo passo
---
Dentro de `wingborn-content-factory/`, para cada pasta em `projects/`, rode
`python3 scripts/validate_project.py projects/<pasta>` (instale `pyyaml` se faltar).

Mostre ao usuário uma tabela curta: projeto, estado, próximo passo. Depois pergunte se ele quer
continuar algum deles ou começar um vídeo novo com `/novo-video <link>`.
