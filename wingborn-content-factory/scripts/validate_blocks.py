#!/usr/bin/env python3
"""Valida os cinco blocos de roteiro de um projeto Wingborn Content Factory.

Uso:
    python3 validate_blocks.py <caminho-do-projeto> [--block N]

Verifica projects/<id>/06_script/block-01.txt até block-05.txt:
  - existência de cada arquivo;
  - codificação UTF-8;
  - contagem de caracteres (incluindo espaços) entre min e max configurados
    (padrão 3200-3500, ou lidos de 00_input/project.yaml se presente);
  - ausência de marcadores técnicos como [CENA], [PAUSE], [SCENE], [MUSIC] etc;
  - ordem/numeração correta dos arquivos (block-01 .. block-05).

Use --block N para validar apenas um bloco (ex.: logo após ser escrito).

Código de saída 0 se tudo válido, 1 se qualquer bloco falhar.
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

DEFAULT_MIN = 3200
DEFAULT_MAX = 3500
DEFAULT_BLOCKS = 5

# Marcadores de produção que não podem aparecer no texto final de narração.
FORBIDDEN_MARKERS = [
    r"\[CENA\]",
    r"\[SCENE\]",
    r"\[PAUSE\]",
    r"\[PAUSA\]",
    r"\[MUSIC\]",
    r"\[MÚSICA\]",
    r"\[SFX\]",
    r"\[SOM\]",
    r"\[NOTE\]",
    r"\[NOTA\]",
    r"\bBLOCK\s*\d+\s*[:\-]",
    r"\bBLOCO\s*\d+\s*[:\-]",
]


def load_length_config(project_dir: Path) -> tuple[int, int, int]:
    """Retorna (min_per_block, max_per_block, blocks). Usa padrões se project.yaml
    não existir ou PyYAML não estiver disponível."""
    if yaml is None:
        return DEFAULT_MIN, DEFAULT_MAX, DEFAULT_BLOCKS

    candidates = [
        project_dir / "00_input" / "project.yaml",
        project_dir / "project.yaml",
    ]
    for c in candidates:
        if c.exists():
            try:
                data = yaml.safe_load(c.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError:
                return DEFAULT_MIN, DEFAULT_MAX, DEFAULT_BLOCKS
            length = data.get("length", {}) if isinstance(data, dict) else {}
            min_c = length.get("min_per_block", DEFAULT_MIN)
            max_c = length.get("max_per_block", DEFAULT_MAX)
            blocks = data.get("blocks", DEFAULT_BLOCKS)
            return min_c, max_c, blocks
    return DEFAULT_MIN, DEFAULT_MAX, DEFAULT_BLOCKS


def validate_block_file(path: Path, min_chars: int, max_chars: int) -> list[str]:
    errors: list[str] = []

    if not path.exists():
        errors.append(f"arquivo não encontrado: {path}")
        return errors

    raw_bytes = path.read_bytes()
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        errors.append(f"não é UTF-8 válido: {exc}")
        return errors

    char_count = len(text)
    if char_count < min_chars or char_count > max_chars:
        errors.append(
            f"contagem de caracteres fora da faixa: {char_count} (esperado entre {min_chars} e {max_chars}, incluindo espaços)"
        )

    for pattern in FORBIDDEN_MARKERS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            errors.append(f"marcador técnico proibido encontrado (padrão: {pattern})")

    if not text.strip():
        errors.append("arquivo está vazio")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--block", type=int, default=None, help="Validar apenas o bloco N")
    args = parser.parse_args()

    project_dir: Path = args.project_dir
    if not project_dir.exists():
        print(f"ERRO: diretório de projeto não encontrado: {project_dir}", file=sys.stderr)
        return 2

    min_chars, max_chars, blocks = load_length_config(project_dir)
    script_dir = project_dir / "06_script"

    block_numbers = [args.block] if args.block else list(range(1, blocks + 1))

    all_ok = True
    for n in block_numbers:
        block_path = script_dir / f"block-{n:02d}.txt"
        errors = validate_block_file(block_path, min_chars, max_chars)
        if errors:
            all_ok = False
            print(f"INVÁLIDO: {block_path}")
            for e in errors:
                print(f"  - {e}")
        else:
            char_count = len(block_path.read_text(encoding="utf-8"))
            print(f"OK: {block_path} — {char_count} caracteres")

    if args.block is None:
        expected = [f"block-{n:02d}.txt" for n in range(1, blocks + 1)]
        if script_dir.exists():
            existing = sorted(p.name for p in script_dir.glob("block-*.txt"))
            unexpected = [f for f in existing if f not in expected]
            if unexpected:
                all_ok = False
                print(f"INVÁLIDO: arquivos de bloco inesperados ou fora de ordem: {unexpected}")

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
