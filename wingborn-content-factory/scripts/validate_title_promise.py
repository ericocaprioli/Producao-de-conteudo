#!/usr/bin/env python3
"""Verifica por regras simples se um título cumpre a promessa esperada.

Uso:
    python3 scripts/validate_title_promise.py "<título>" [--project PROJECT_DIR]
    python3 scripts/validate_title_promise.py --file titulos.txt [--project PROJECT_DIR]
    python3 scripts/validate_title_promise.py --project PROJECT_DIR   (lê 09_seo/title-options.yaml)

Checa: comprimento, padrões proibidos, sinais de injustiça / vítima identificável /
elemento fantástico / inversão e, com --project, a correspondência com a direção
selecionada (papéis familiares citados, dragão plantado).

Vereditos: PASS, REVIEW_REQUIRED (evidência insuficiente — revisar manualmente) e FAIL.
O script não afirma qualidade: ausência de palavra-chave vira REVIEW_REQUIRED, não FAIL.
Código de saída 1 se algum título receber FAIL.
"""

import argparse
import re
import sys
from pathlib import Path

from wb_common import contains_term, flatten_text, load_config, load_first

DRAGON_WORDS = ["dragon", "dragons", "wyrm", "drake"]


def direction_text(project_dir: Path) -> str | None:
    data = load_first(project_dir / "04_selected_direction" / "selected-direction.yaml")
    return flatten_text(data) if data else None


def evaluate_title(title: str, rules: dict, direction: str | None) -> tuple[str, list[str]]:
    fails: list[str] = []
    reviews: list[str] = []

    max_len = rules.get("max_length_chars", 100)
    if len(title) > max_len:
        fails.append(f"{len(title)} caracteres, acima do limite de {max_len}")

    for rule in rules.get("forbidden_patterns", []):
        if re.search(rule["pattern"], title, flags=re.IGNORECASE):
            msg = f"padrão '{rule['pattern']}': {rule.get('reason', '')}"
            (fails if rule.get("severity", "fail") == "fail" else reviews).append(msg)

    missing = [
        group for group, words in rules.get("keyword_groups", {}).items()
        if not any(contains_term(title, w) for w in words)
    ]
    if missing:
        reviews.append("sinais não detectados por palavra-chave (podem estar implícitos): " + ", ".join(missing))

    if direction is None:
        reviews.append("correspondência com a direção não verificada (use --project após /escolher-direcao)")
    else:
        for role in rules.get("family_roles", []):
            if contains_term(title, role) and not contains_term(direction, role):
                fails.append(f"título cita '{role}', mas a direção selecionada não tem esse papel")
        generic = [t for t in rules.get("generic_family_terms", []) if contains_term(title, t)]
        if generic and not any(contains_term(direction, r) for r in rules.get("family_roles", [])):
            fails.append(f"título cita {generic}, mas a direção não define um traidor familiar")
        if any(contains_term(title, w) for w in DRAGON_WORDS) and not any(contains_term(direction, w) for w in DRAGON_WORDS):
            fails.append("título promete dragão, mas a direção selecionada não o planta")

    if fails:
        return "FAIL", fails + reviews
    if reviews:
        return "REVIEW_REQUIRED", reviews
    return "PASS", []


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida a promessa de títulos.")
    parser.add_argument("title", nargs="?")
    parser.add_argument("--file", type=Path)
    parser.add_argument("--project", type=Path)
    args = parser.parse_args()

    titles: list[str] = []
    if args.title:
        titles.append(args.title)
    if args.file:
        if not args.file.exists():
            print(f"ERRO: arquivo não encontrado: {args.file}", file=sys.stderr)
            return 2
        titles += [ln.strip() for ln in args.file.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not titles and args.project:
        options = load_first(args.project / "09_seo" / "title-options.yaml") or {}
        titles = [o.get("text", "") for o in options.get("title_options", []) if o.get("text")]
    if not titles:
        print(__doc__)
        return 2

    rules = load_config("title-rules.yaml")
    direction = direction_text(args.project) if args.project else None

    any_fail = False
    for title in titles:
        verdict, notes = evaluate_title(title, rules, direction)
        print(f"{verdict}: {title}")
        for n in notes:
            print(f"  - {n}")
        any_fail |= verdict == "FAIL"
    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main())
