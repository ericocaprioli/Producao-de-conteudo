#!/usr/bin/env python3
"""Valida o arquivo de estado project.yaml de um projeto Wingborn Content Factory.

Uso:
    python3 scripts/validate_project.py <caminho-do-projeto>

Verifica schema, modo de criação, estados, gates aprovados, coerência das métricas da
referência (nada inventado) e blocos aprovados. Ao final sugere o próximo comando, para
permitir retomar um projeto interrompido apenas pelo arquivo de estado.

Código de saída 0 se válido, 1 se inválido, 2 em erro de uso.
"""

import sys
from pathlib import Path

from wb_common import MODES, find_project_yaml, load_yaml

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

ALLOWED_GATES = {
    "direction", "trend_alignment", "title", "character_bible", "packaging",
    "script", "retention", "scenes", "exports",
}

# Gates exigidos a partir de cada estado (inclusive estados posteriores).
STATE_REQUIRES_GATES = {
    "direction_selected": ["direction"],
    "title_approved": ["title"],
    "bible_approved": ["character_bible"],
    "writing_in_progress": ["packaging"],
    "script_approved": ["script"],
    "retention_approved": ["retention"],
    "scenes_ready": ["scenes"],
    "exports_ready": ["exports"],
}

NEXT_COMMAND = {
    "input_received": "/triar-referencia (ou /criar-direcoes em original_channel_story)",
    "reference_filtered": "/analisar-referencia",
    "reference_analyzed": "/criar-direcoes",
    "directions_ready": "/escolher-direcao (usuário escolhe A, B ou C)",
    "direction_selected": "/criar-titulos",
    "title_approved": "/criar-ficha",
    "bible_approved": "aprovação de embalagem em /criar-ficha, depois /escrever-bloco 1",
    "writing_in_progress": "/escrever-bloco N (próximo bloco não aprovado)",
    "script_approved": "/revisar-retencao",
    "retention_approved": "/gerar-cenas",
    "scenes_ready": "/gerar-seo e depois /exportar-projeto",
    "exports_ready": "nenhum — projeto exportado",
}

REQUIRED_TOP_LEVEL_KEYS = [
    "id", "status", "mode", "language", "channel_mode", "blocks", "length",
    "reference_filter", "reference", "approved_gates",
]

CHANNEL_MODES = ("core_female_protagonist", "experimental_male_protagonist")


def expected_meets_filter(views, age_hours, min_views, window_hours):
    """true/false quando decidível pelos dados fornecidos; 'unknown' caso contrário."""
    if isinstance(views, int) and views < min_views:
        return False
    if isinstance(age_hours, (int, float)) and age_hours > window_hours:
        return False
    if isinstance(views, int) and isinstance(age_hours, (int, float)):
        return True
    return "unknown"


def validate_metric(ref: dict, value_key: str, source_key: str, errors: list[str]) -> None:
    value = ref.get(value_key)
    source = ref.get(source_key, "unknown")
    if value is None and source not in ("unknown", None):
        errors.append(
            f"reference.{value_key} está vazio, então reference.{source_key} deve ser 'unknown' (está '{source}')"
        )
    if value is not None and source in ("unknown", None, ""):
        errors.append(
            f"reference.{value_key} = {value} sem fonte. Informe reference.{source_key} "
            f"('manual' se veio do usuário) ou remova o valor — métricas nunca são inventadas"
        )
    if value is not None and not isinstance(value, (int, float)):
        errors.append(f"reference.{value_key} deve ser número ou null (recebido: {value!r})")


def validate(project_dir: Path) -> tuple[list[str], dict]:
    errors: list[str] = []

    yaml_path = find_project_yaml(project_dir)
    if yaml_path is None:
        return [f"project.yaml não encontrado em {project_dir}/00_input/project.yaml"], {}

    try:
        data = load_yaml(yaml_path)
    except Exception as exc:  # YAML malformado
        return [f"YAML inválido em {yaml_path}: {exc}"], {}

    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in data:
            errors.append(f"campo obrigatório ausente: '{key}'")

    status = data.get("status")
    if status not in ALLOWED_STATES:
        errors.append(f"status '{status}' não é permitido. Estados válidos: {ALLOWED_STATES}")

    mode = data.get("mode")
    if mode not in MODES:
        errors.append(f"mode '{mode}' inválido. Use um de: {list(MODES)}")

    if data.get("channel_mode") not in CHANNEL_MODES:
        errors.append(f"channel_mode '{data.get('channel_mode')}' inválido. Use um de: {list(CHANNEL_MODES)}")

    gates = data.get("approved_gates") or []
    if not isinstance(gates, list):
        errors.append("'approved_gates' deve ser uma lista")
        gates = []
    for g in gates:
        if g not in ALLOWED_GATES:
            errors.append(f"gate desconhecido em approved_gates: '{g}'. Válidos: {sorted(ALLOWED_GATES)}")

    if status in ALLOWED_STATES:
        idx = ALLOWED_STATES.index(status)
        required: list[str] = []
        for state, state_gates in STATE_REQUIRES_GATES.items():
            if idx >= ALLOWED_STATES.index(state):
                required.extend(state_gates)
        if mode == "adjacent_trend" and idx >= ALLOWED_STATES.index("direction_selected"):
            required.append("trend_alignment")
        for g in required:
            if g not in gates:
                errors.append(f"status '{status}' exige o gate '{g}' em approved_gates. Não avance sem aprovação.")

    length = data.get("length") or {}
    min_c, max_c = length.get("min_per_block"), length.get("max_per_block")
    if isinstance(min_c, int) and isinstance(max_c, int) and min_c > max_c:
        errors.append(f"length.min_per_block ({min_c}) maior que length.max_per_block ({max_c})")
    if length.get("unit") not in ("characters", "words"):
        errors.append(f"length.unit '{length.get('unit')}' inválido. Use 'characters' ou 'words'")

    ref = data.get("reference") or {}
    rf = data.get("reference_filter") or {}
    validate_metric(ref, "views", "views_source", errors)
    validate_metric(ref, "age_hours", "age_source", errors)

    if mode in ("adjacent_trend", "reference_adaptation") and status in ALLOWED_STATES:
        if ALLOWED_STATES.index(status) >= ALLOWED_STATES.index("reference_filtered") and not ref.get("url"):
            errors.append(f"mode '{mode}' exige reference.url a partir de reference_filtered")

    expected = expected_meets_filter(
        ref.get("views"), ref.get("age_hours"),
        rf.get("minimum_views", 100000), rf.get("recency_window_hours", 20),
    )
    stored = ref.get("meets_filter", "unknown")
    if ref.get("url") and stored != expected:
        errors.append(
            f"reference.meets_filter = {stored!r}, mas pelos dados informados deveria ser {expected!r} "
            f"(mínimo {rf.get('minimum_views')} views, até {rf.get('recency_window_hours')} h)"
        )

    blocks = data.get("blocks", 5)
    approved_blocks = data.get("approved_blocks") or []
    for b in approved_blocks:
        if not isinstance(b, int) or not 1 <= b <= blocks:
            errors.append(f"approved_blocks contém valor inválido: {b!r}")
        elif not (project_dir / "06_script" / f"block-{b:02d}.txt").exists():
            errors.append(f"bloco {b} está em approved_blocks, mas 06_script/block-{b:02d}.txt não existe")
    if "script" in gates and sorted(approved_blocks) != list(range(1, blocks + 1)):
        errors.append(f"gate 'script' aprovado, mas approved_blocks = {approved_blocks} (esperado 1..{blocks})")

    return errors, data


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2

    project_dir = Path(sys.argv[1])
    if not project_dir.exists():
        print(f"ERRO: diretório de projeto não encontrado: {project_dir}", file=sys.stderr)
        return 2

    errors, data = validate(project_dir)
    if errors:
        print(f"INVÁLIDO: {project_dir}")
        for e in errors:
            print(f"  - {e}")
        return 1

    status = data.get("status")
    print(f"OK: {project_dir} — project.yaml válido")
    print(f"  modo: {data.get('mode')} | estado: {status} | gates: {data.get('approved_gates') or []}")
    if status == "writing_in_progress":
        pending = [n for n in range(1, data.get("blocks", 5) + 1) if n not in (data.get("approved_blocks") or [])]
        print(f"  blocos pendentes: {pending}")
    print(f"  próximo comando: {NEXT_COMMAND.get(status, '?')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
