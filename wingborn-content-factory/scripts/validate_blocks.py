#!/usr/bin/env python3
"""Valida os blocos de roteiro de um projeto Wingborn Content Factory.

Uso:
    python3 scripts/validate_blocks.py <caminho-do-projeto> [--block N]

Verifica 06_script/block-01.txt até block-05.txt:
  - existência de cada arquivo;
  - codificação UTF-8;
  - contagem entre o mínimo e o máximo configurados em project.yaml (padrão 3200–3500
    caracteres, incluindo espaços, pontuação e quebras de linha internas; espaços nas
    bordas do arquivo e a quebra de linha final não contam);
  - ausência de marcadores técnicos ([CENA], [PAUSE], BLOCO 1: etc.);
  - nomes e ordem dos arquivos (nenhum block-*.txt fora da sequência).

Código de saída 0 se tudo válido, 1 se algum bloco falhar, 2 em erro de uso.
"""

import argparse
import re
import sys
from pathlib import Path

from wb_common import count_units, load_project

FORBIDDEN_MARKERS = [
    r"\[(CENA|SCENE|PAUSE|PAUSA|MUSIC|MÚSICA|SFX|SOM|NOTE|NOTA|CUT|CORTE)[^\]]*\]",
    r"^\s*(BLOCK|BLOCO)\s*\d+\s*[:\-—]",
    r"^\s*#+\s",
    r"^\s*\((pause|pausa|music|música|sfx)[^)]*\)",
]


def validate_block_file(path: Path, min_units: int, max_units: int, unit: str, count_spaces: bool) -> tuple[list[str], int | None]:
    if not path.exists():
        return [f"arquivo não encontrado: {path}"], None

    try:
        text = path.read_bytes().decode("utf-8")
    except UnicodeDecodeError as exc:
        return [f"não é UTF-8 válido: {exc}"], None

    errors: list[str] = []
    if not text.strip():
        return ["arquivo está vazio"], 0

    n = count_units(text, unit, count_spaces)
    if not min_units <= n <= max_units:
        errors.append(f"{n} {unit} — fora da faixa {min_units}–{max_units}")

    for pattern in FORBIDDEN_MARKERS:
        m = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        if m:
            errors.append(f"marcador técnico proibido: {m.group(0).strip()!r}")

    return errors, n


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida os blocos de roteiro.")
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--block", type=int, default=None, help="validar apenas o bloco N")
    args = parser.parse_args()

    if not args.project_dir.exists():
        print(f"ERRO: diretório de projeto não encontrado: {args.project_dir}", file=sys.stderr)
        return 2

    project = load_project(args.project_dir)
    length = project.get("length") or {}
    min_u = length.get("min_per_block", 3200)
    max_u = length.get("max_per_block", 3500)
    unit = length.get("unit", "characters")
    count_spaces = length.get("count_spaces", True)
    blocks = project.get("blocks", 5)

    if args.block is not None and not 1 <= args.block <= blocks:
        print(f"ERRO: --block deve estar entre 1 e {blocks}", file=sys.stderr)
        return 2

    script_dir = args.project_dir / "06_script"
    numbers = [args.block] if args.block is not None else list(range(1, blocks + 1))

    ok = True
    for n in numbers:
        path = script_dir / f"block-{n:02d}.txt"
        errors, count = validate_block_file(path, min_u, max_u, unit, count_spaces)
        if errors:
            ok = False
            print(f"INVÁLIDO: {path}")
            for e in errors:
                print(f"  - {e}")
        else:
            print(f"OK: {path} — {count} {unit} (faixa {min_u}–{max_u})")

    if args.block is None and script_dir.exists():
        expected = {f"block-{n:02d}.txt" for n in range(1, blocks + 1)}
        unexpected = sorted(p.name for p in script_dir.glob("block-*.txt") if p.name not in expected)
        if unexpected:
            ok = False
            print(f"INVÁLIDO: arquivos de bloco fora da sequência block-01..block-{blocks:02d}: {unexpected}")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
