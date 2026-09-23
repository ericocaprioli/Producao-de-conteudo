#!/usr/bin/env python3
"""Valida o arquivo project.yaml de um projeto Wingborn Content Factory.

Uso:
    python3 validate_project.py <caminho-do-projeto>

<caminho-do-projeto> deve ser um diretório como projects/2026-09-23-exemplo,
contendo 00_input/project.yaml (procurado também na raiz do projeto, como
fallback, para compatibilidade).

Saída: relatório humano no stdout. Código de saída 0 se válido, 1 se inválido.
"""

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERRO: PyYAML não está instalado. Instale com: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

ALLOWED_STATES = [
    "input_received",
    "reference_filtered",
    "reference_analyzed",
    "directions_ready",
    "direction_selected",
    "title_approved",
    "bible_approved",
    "writing_in_progress",
    "script_approved",
    "retention_approved",
    "scenes_ready",
    "exports_ready",
]

# Gate que precisa estar em approved_gates antes de um projeto poder estar
# no estado correspondente (ou em qualquer estado posterior).
STATE_REQUIRES_GATE = {
    "direction_selected": "direction",
    "title_approved": "title",
    "bible_approved": "character_bible",
    "script_approved": "script",
    "retention_approved": "retention",
    "scenes_ready": "scenes",
    "exports_ready": "exports",
}

REQUIRED_TOP_LEVEL_KEYS = [
    "id",
    "status",
    "language",
    "channel_mode",
    "blocks",
    "length",
    "reference_filter",
    "reference",
    "approved_gates",
]


def find_project_yaml(project_dir: Path) -> Path | None:
    candidates = [
        project_dir / "00_input" / "project.yaml",
        project_dir / "project.yaml",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def validate(project_dir: Path) -> list[str]:
    errors: list[str] = []

    yaml_path = find_project_yaml(project_dir)
    if yaml_path is None:
        errors.append(
            f"project.yaml não encontrado em {project_dir}/00_input/project.yaml nem em {project_dir}/project.yaml"
        )
        return errors

    try:
        data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        errors.append(f"YAML inválido em {yaml_path}: {exc}")
        return errors

    if not isinstance(data, dict):
        errors.append(f"{yaml_path} não contém um mapeamento YAML válido")
        return errors

    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in data:
            errors.append(f"Campo obrigatório ausente: '{key}'")

    status = data.get("status")
    if status is not None and status not in ALLOWED_STATES:
        errors.append(
            f"status '{status}' não é um estado permitido. Estados válidos: {ALLOWED_STATES}"
        )

    approved_gates = data.get("approved_gates", [])
    if not isinstance(approved_gates, list):
        errors.append("'approved_gates' deve ser uma lista")
        approved_gates = []

    if status in ALLOWED_STATES:
        status_index = ALLOWED_STATES.index(status)
        for gate_state, gate_name in STATE_REQUIRES_GATE.items():
            gate_index = ALLOWED_STATES.index(gate_state)
            if status_index >= gate_index and gate_name not in approved_gates:
                errors.append(
                    f"status '{status}' requer o gate '{gate_name}' em 'approved_gates', "
                    f"mas ele não foi encontrado. Não avance o estado sem aprovação do gate."
                )

    length = data.get("length", {})
    if isinstance(length, dict):
        min_c = length.get("min_per_block")
        max_c = length.get("max_per_block")
        if isinstance(min_c, int) and isinstance(max_c, int) and min_c > max_c:
            errors.append(f"'length.min_per_block' ({min_c}) maior que 'length.max_per_block' ({max_c})")

    reference = data.get("reference", {})
    if isinstance(reference, dict):
        views_source = reference.get("views_source")
        if views_source not in (None, "unknown", "manual") and not isinstance(views_source, str):
            errors.append("'reference.views_source' deve ser uma string ('manual', 'unknown' ou o nome da fonte)")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2

    project_dir = Path(sys.argv[1])
    if not project_dir.exists():
        print(f"ERRO: diretório de projeto não encontrado: {project_dir}", file=sys.stderr)
        return 2

    errors = validate(project_dir)

    if errors:
        print(f"INVÁLIDO: {project_dir}")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"OK: {project_dir} — project.yaml válido")
    return 0


if __name__ == "__main__":
    sys.exit(main())
