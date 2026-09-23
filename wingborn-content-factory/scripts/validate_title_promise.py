#!/usr/bin/env python3
"""Verifica heuristicamente se um título cumpre a promessa esperada.

Uso:
    python3 validate_title_promise.py "<título>" [--direction <caminho selected-direction.md>]
    python3 validate_title_promise.py --file <caminho com um título por linha>

Usa config/title-rules.yaml (procurado relativo a este script) para palavras-chave e
padrões proibidos. Isto é um apoio por regras simples, não uma avaliação de qualidade:
quando a evidência é insuficiente, o script sinaliza REVIEW_REQUIRED em vez de aprovar
ou reprovar sem base.

Código de saída: 0 se todos os títulos passarem sem reprovação (REVIEW_REQUIRED conta como
passagem condicional), 1 se algum título for reprovado (FAIL).
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERRO: PyYAML não está instalado. Instale com: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_RULES_PATH = SCRIPT_DIR.parent / "config" / "title-rules.yaml"


def load_rules(path: Path) -> dict:
    if not path.exists():
        print(f"AVISO: {path} não encontrado, usando regras mínimas embutidas", file=sys.stderr)
        return {
            "max_length_chars": 100,
            "forbidden_patterns": [],
            "keyword_groups": {},
        }
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def contains_any(text: str, keywords: list[str]) -> bool:
    return any(re.search(r"\b" + re.escape(kw) + r"\b", text, flags=re.IGNORECASE) for kw in keywords)


def evaluate_title(title: str, rules: dict) -> tuple[str, list[str]]:
    """Retorna (veredito, motivos). Veredito em {PASS, REVIEW_REQUIRED, FAIL}."""
    notes: list[str] = []
    fail_reasons: list[str] = []

    max_len = rules.get("max_length_chars", 100)
    if len(title) > max_len:
        fail_reasons.append(f"título tem {len(title)} caracteres, acima do limite de {max_len}")

    for forbidden in rules.get("forbidden_patterns", []):
        pattern = forbidden.get("pattern") if isinstance(forbidden, dict) else forbidden
        reason = forbidden.get("reason", "") if isinstance(forbidden, dict) else ""
        if pattern and re.search(pattern, title, flags=re.IGNORECASE):
            fail_reasons.append(f"contém padrão proibido '{pattern}'" + (f" ({reason})" if reason else ""))

    keyword_groups = rules.get("keyword_groups", {})
    signals_found = {}
    for group_name, keywords in keyword_groups.items():
        signals_found[group_name] = contains_any(title, keywords)

    missing_signals = [g for g, found in signals_found.items() if not found]

    if fail_reasons:
        return "FAIL", fail_reasons

    if missing_signals:
        notes.append(
            "sinais não detectados por palavra-chave (pode estar presente de forma implícita — revisar manualmente): "
            + ", ".join(missing_signals)
        )
        return "REVIEW_REQUIRED", notes

    return "PASS", notes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("title", nargs="?", help="Título a validar (entre aspas)")
    parser.add_argument("--file", type=Path, help="Arquivo com um título por linha")
    parser.add_argument("--rules", type=Path, default=DEFAULT_RULES_PATH)
    args = parser.parse_args()

    if not args.title and not args.file:
        print(__doc__)
        return 2

    rules = load_rules(args.rules)

    titles: list[str] = []
    if args.title:
        titles.append(args.title)
    if args.file:
        if not args.file.exists():
            print(f"ERRO: arquivo não encontrado: {args.file}", file=sys.stderr)
            return 2
        titles.extend(line.strip() for line in args.file.read_text(encoding="utf-8").splitlines() if line.strip())

    any_fail = False
    for title in titles:
        verdict, notes = evaluate_title(title, rules)
        print(f"{verdict}: {title}")
        for n in notes:
            print(f"  - {n}")
        if verdict == "FAIL":
            any_fail = True

    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main())
