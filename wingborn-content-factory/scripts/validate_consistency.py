#!/usr/bin/env python3
"""Compara character-bible.yaml com o roteiro e detecta inconsistências básicas.

Uso:
    python3 validate_consistency.py <caminho-do-projeto>

Lê projects/<id>/05_character_bible/character-bible.yaml e
projects/<id>/06_script/block-*.txt.

Checagens (heurísticas, não semânticas — sinalizam candidatos para revisão humana):
  - nomes do protagonista/antagonista/aliado/dragão ausentes do roteiro;
  - outros números de idade mencionados perto do nome do protagonista, diferentes
    da idade da ficha;
  - objeto-símbolo (story.symbol_object) nunca mencionado, ou mencionado só no início;
  - palavras-chave da aparência da ficha nunca aparecendo no roteiro (aviso leve).

Código de saída 0 se nenhuma inconsistência encontrada, 1 caso contrário.
Isto NÃO é uma verificação semântica completa: é um apoio determinístico, não substitui
revisão humana do roteiro.
"""

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERRO: PyYAML não está instalado. Instale com: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


def load_bible(project_dir: Path) -> dict | None:
    path = project_dir / "05_character_bible" / "character-bible.yaml"
    if not path.exists():
        path = project_dir / "character-bible.yaml"
    if not path.exists():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_script(project_dir: Path) -> str:
    script_dir = project_dir / "06_script"
    parts = []
    for n in range(1, 6):
        block_path = script_dir / f"block-{n:02d}.txt"
        if block_path.exists():
            parts.append(block_path.read_text(encoding="utf-8"))
    return "\n\n".join(parts)


def find_ages_near(name: str, text: str, window: int = 60) -> set[int]:
    ages = set()
    if not name:
        return ages
    for m in re.finditer(re.escape(name), text, flags=re.IGNORECASE):
        start = max(0, m.start() - window)
        end = min(len(text), m.end() + window)
        snippet = text[start:end]
        for age_match in re.finditer(r"\b(\d{1,3})[- ]?(year|ano)s?[- ]?old\b|\b(\d{1,3})[- ]?anos\b", snippet, flags=re.IGNORECASE):
            for g in age_match.groups():
                if g:
                    ages.add(int(g))
    return ages


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2

    project_dir = Path(sys.argv[1])
    if not project_dir.exists():
        print(f"ERRO: diretório de projeto não encontrado: {project_dir}", file=sys.stderr)
        return 2

    bible = load_bible(project_dir)
    if bible is None:
        print("ERRO: character-bible.yaml não encontrado (05_character_bible/character-bible.yaml)", file=sys.stderr)
        return 2

    script = load_script(project_dir)
    if not script.strip():
        print("ERRO: nenhum bloco de roteiro encontrado em 06_script/", file=sys.stderr)
        return 2

    warnings: list[str] = []
    errors: list[str] = []

    protagonist = bible.get("protagonist", {}) or {}
    antagonist = bible.get("antagonist", {}) or {}
    ally = bible.get("ally", {}) or {}
    dragon = bible.get("dragon", {}) or {}
    story = bible.get("story", {}) or {}

    named_roles = {
        "protagonist.name": protagonist.get("name"),
        "antagonist.name": antagonist.get("name"),
        "ally.name": ally.get("name"),
    }
    for field, name in named_roles.items():
        if name and name.strip():
            if not re.search(re.escape(name), script, flags=re.IGNORECASE):
                errors.append(f"nome de '{field}' ('{name}') não aparece no roteiro")

    bible_age = protagonist.get("age")
    if isinstance(bible_age, int) and protagonist.get("name"):
        ages_found = find_ages_near(protagonist["name"], script)
        contradictory = ages_found - {bible_age}
        if contradictory:
            errors.append(
                f"idade do protagonista na ficha é {bible_age}, mas o roteiro menciona idade(s) diferente(s) perto do nome: {sorted(contradictory)}"
            )

    symbol_object = story.get("symbol_object")
    if symbol_object and symbol_object.strip():
        occurrences = len(re.findall(re.escape(symbol_object), script, flags=re.IGNORECASE))
        if occurrences == 0:
            errors.append(f"objeto-símbolo da ficha ('{symbol_object}') nunca é mencionado no roteiro")
        elif occurrences == 1:
            warnings.append(
                f"objeto-símbolo ('{symbol_object}') aparece apenas uma vez — considere reforçar continuidade"
            )

    dragon_appearance = dragon.get("appearance")
    if dragon_appearance and dragon_appearance.strip():
        key_terms = [w for w in re.findall(r"[A-Za-zÀ-ÿ]{4,}", dragon_appearance)][:3]
        missing_terms = [t for t in key_terms if not re.search(re.escape(t), script, flags=re.IGNORECASE)]
        if key_terms and len(missing_terms) == len(key_terms):
            warnings.append(
                f"nenhum termo-chave da aparência do dragão na ficha ({key_terms}) aparece no roteiro — verificar consistência visual"
            )

    climax_location = story.get("climax_location")
    if climax_location and climax_location.strip():
        if not re.search(re.escape(climax_location), script, flags=re.IGNORECASE):
            warnings.append(f"local do clímax da ficha ('{climax_location}') não foi encontrado no roteiro")

    if errors:
        print(f"INCONSISTÊNCIAS DETECTADAS: {project_dir}")
        for e in errors:
            print(f"  ERRO: {e}")
    if warnings:
        for w in warnings:
            print(f"  AVISO: {w}")

    if not errors and not warnings:
        print(f"OK: {project_dir} — nenhuma inconsistência básica detectada")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
