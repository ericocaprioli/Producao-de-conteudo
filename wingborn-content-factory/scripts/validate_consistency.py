#!/usr/bin/env python3
"""Compara character-bible.yaml com o roteiro e detecta inconsistências básicas.

Uso:
    python3 scripts/validate_consistency.py <caminho-do-projeto>

Lê 05_character_bible/character-bible.yaml e 06_script/block-*.txt.

ERRO (código de saída 1):
  - nome do protagonista, antagonista ou aliado ausente do roteiro;
  - nome possivelmente alterado (variação de 1–2 letras de um nome da ficha);
  - idade do protagonista diferente da ficha (dígitos ou por extenso: "nine years old");
  - objeto-símbolo nunca mencionado;
  - bloco 1 sem o antagonista (nome ou parentesco) nos primeiros ~30 s de narração,
    ou sem o objeto-símbolo nos primeiros ~60 s.

AVISO (não bloqueia):
  - cor de cabelo/olhos do protagonista ou de escamas do dragão diferente da ficha;
  - objeto-símbolo ausente dos blocos 1–2 (não plantado) ou dos blocos 4–5 (sumiu);
  - local do clímax ausente dos blocos 4–5;
  - nenhum sinal do dragão nos primeiros ~60 s do bloco 1.

É uma checagem determinística por regras, não semântica: aponta candidatos à revisão,
não substitui a leitura humana do roteiro.
"""

import re
import sys
from pathlib import Path

from wb_common import contains_term, load_config, load_first, read_blocks, tokens

UNITS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
    "seventeen": 17, "eighteen": 18, "nineteen": 19,
}
TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
_UNIT_ALT = "|".join(sorted(UNITS, key=len, reverse=True))
_TENS_ALT = "|".join(TENS)
NUM = rf"\d{{1,3}}|(?:{_TENS_ALT})(?:[- ](?:{_UNIT_ALT}))?|{_UNIT_ALT}"
AGE_PATTERNS = [
    rf"\b({NUM})[- ](?:years?|yrs?)[- ]old\b",
    rf"\baged\s+({NUM})\b",
    rf"\b({NUM})\s+anos\b",
]

COLORS = {
    "red", "copper", "auburn", "ginger", "black", "dark", "brown", "chestnut", "blonde", "blond", "golden",
    "gold", "fair", "silver", "white", "grey", "gray", "green", "blue", "amber", "hazel", "violet", "ash",
    "bronze", "crimson", "scarlet",
}
FEATURES = {"hair": "hair", "haired": "hair", "braid": "hair", "braids": "hair", "eyes": "eyes", "eyed": "eyes",
            "scales": "scales", "scaled": "scales"}
DRAGON_WORDS = ["dragon", "dragons", "wyrm", "drake", "dragão", "dragões"]


def parse_num(s: str) -> int:
    s = s.lower()
    if s.isdigit():
        return int(s)
    total = 0
    for part in re.split(r"[- ]", s):
        total += TENS.get(part, 0) + UNITS.get(part, 0)
    return total


def sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]


def levenshtein(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def name_variants(name: str, script: str, known: set[str]) -> set[str]:
    base = name.lower()
    found = set()
    for tok in set(re.findall(r"\b[A-ZÀ-Ý][a-zà-ÿ]+\b", script)):
        t = tok.lower()
        if t == base or t in known or t[0] != base[0] or abs(len(t) - len(base)) > 1:
            continue
        limit = 1 if len(base) <= 6 else 2
        if levenshtein(t, base) <= limit:
            found.add(tok)
    return found


def protagonist_ages(script: str, protagonist: str, other_names: list[str]) -> set[int]:
    ages = set()
    for sent in sentences(script):
        if not contains_term(sent, protagonist):
            continue
        name_positions = []
        for nm in [protagonist] + other_names:
            for m in re.finditer(r"\b" + re.escape(nm) + r"\b", sent, flags=re.IGNORECASE):
                name_positions.append((m.start(), nm))
        for pattern in AGE_PATTERNS:
            for m in re.finditer(pattern, sent, flags=re.IGNORECASE):
                nearest = min(name_positions, key=lambda p: abs(p[0] - m.start()))
                if nearest[1] == protagonist:
                    ages.add(parse_num(m.group(1)))
    return ages


def feature_colors(text: str) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    toks = tokens(text)
    for i, t in enumerate(toks):
        feat = FEATURES.get(t)
        if not feat:
            continue
        for prev in toks[max(0, i - 3):i]:
            if prev in COLORS:
                out.setdefault(feat, set()).add(prev)
    return out


def phrase_present(text: str, phrase: str) -> bool:
    if not phrase:
        return False
    if contains_term(text, phrase):
        return True
    head = tokens(phrase)[-1] if tokens(phrase) else ""
    return bool(head) and len(head) > 3 and contains_term(text, head)


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2

    project_dir = Path(sys.argv[1])
    if not project_dir.exists():
        print(f"ERRO: diretório de projeto não encontrado: {project_dir}", file=sys.stderr)
        return 2

    bible = load_first(project_dir / "05_character_bible" / "character-bible.yaml")
    if bible is None:
        print("ERRO: 05_character_bible/character-bible.yaml não encontrado", file=sys.stderr)
        return 2

    blocks = read_blocks(project_dir)
    present = [b or "" for b in blocks]
    script = "\n\n".join(present)
    if not script.strip():
        print("ERRO: nenhum bloco encontrado em 06_script/", file=sys.stderr)
        return 2

    errors: list[str] = []
    warnings: list[str] = []

    prot = bible.get("protagonist") or {}
    anta = bible.get("antagonist") or {}
    ally = bible.get("ally") or {}
    dragon = bible.get("dragon") or {}
    story = bible.get("story") or {}

    names = {"protagonist": prot.get("name"), "antagonist": anta.get("name"), "ally": ally.get("name")}
    names = {role: n.strip() for role, n in names.items() if isinstance(n, str) and n.strip()}
    known_lower = {n.lower() for n in names.values()}

    # Roteiro parcial (escrita bloco a bloco): ausências só são erro/aviso quando os blocos existem.
    complete = all(blocks)
    late_blocks_written = len(blocks) >= 5 and all(blocks[3:5])

    for role, name in names.items():
        if not contains_term(script, name):
            if complete:
                errors.append(f"nome de {role} ('{name}') não aparece no roteiro")
            else:
                print(f"  INFO: {role} ('{name}') ainda não apareceu nos blocos escritos")
        variants = name_variants(name, script, known_lower)
        if variants:
            errors.append(f"nome de {role} possivelmente alterado: {sorted(variants)} (ficha: '{name}')")

    age = prot.get("age")
    if isinstance(age, int) and names.get("protagonist"):
        others = [n for r, n in names.items() if r != "protagonist"]
        found = protagonist_ages(script, names["protagonist"], others)
        if found - {age}:
            errors.append(f"idade do protagonista na ficha é {age}, mas o roteiro indica {sorted(found - {age})}")

    bible_prot_colors = feature_colors(prot.get("appearance") or "")
    if names.get("protagonist"):
        prot_sentences = " . ".join(s for s in sentences(script) if contains_term(s, names["protagonist"]))
        for feat, cols in feature_colors(prot_sentences).items():
            if feat in bible_prot_colors and feat != "scales" and not cols & bible_prot_colors[feat]:
                warnings.append(
                    f"aparência: {feat} descrito como {sorted(cols)} perto de '{names['protagonist']}', "
                    f"ficha diz {sorted(bible_prot_colors[feat])}"
                )

    bible_dragon_colors = feature_colors(dragon.get("appearance") or "").get("scales", set())
    script_scales = feature_colors(script).get("scales", set())
    if bible_dragon_colors and script_scales and not script_scales <= bible_dragon_colors:
        warnings.append(
            f"dragão: escamas descritas como {sorted(script_scales - bible_dragon_colors)}, "
            f"ficha diz {sorted(bible_dragon_colors)}"
        )

    symbol = (story.get("symbol_object") or "").strip()
    if symbol:
        if not phrase_present(script, symbol):
            errors.append(f"objeto-símbolo da ficha ('{symbol}') nunca é mencionado no roteiro")
        else:
            if all(blocks[:2]) and not any(phrase_present(b, symbol) for b in present[:2]):
                warnings.append(f"objeto-símbolo ('{symbol}') não é plantado nos blocos 1–2")
            if late_blocks_written and not any(phrase_present(b, symbol) for b in present[3:5]):
                warnings.append(f"objeto-símbolo ('{symbol}') desaparece antes dos blocos 4–5 — verificar se é explicado")

    climax_location = (story.get("climax_location") or "").strip()
    if climax_location and late_blocks_written:
        if not any(contains_term(b, climax_location) for b in present[3:5]):
            warnings.append(f"local do clímax da ficha ('{climax_location}') não aparece nos blocos 4–5")

    if blocks and blocks[0]:
        retention = load_config("retention-rules.yaml")
        cps = retention.get("narration_chars_per_second", 15)
        opening = retention.get("opening") or {}
        first = blocks[0].strip()
        limit_antagonist = int(cps * opening.get("antagonist_identified_by_seconds", 30))
        limit_symbol = int(cps * opening.get("symbol_planted_by_seconds", 60))
        limit_fantasy = int(cps * opening.get("fantasy_signal_by_seconds", 60))

        markers = [m for m in (anta.get("name"), anta.get("relation")) if m]
        if markers and not any(contains_term(first[:limit_antagonist], m) for m in markers):
            errors.append(
                f"bloco 1: antagonista ({' / '.join(markers)}) não identificado nos primeiros "
                f"{limit_antagonist} caracteres (~{opening.get('antagonist_identified_by_seconds', 30)} s)"
            )
        if symbol and not phrase_present(first[:limit_symbol], symbol):
            errors.append(
                f"bloco 1: objeto-símbolo ('{symbol}') não plantado nos primeiros "
                f"{limit_symbol} caracteres (~{opening.get('symbol_planted_by_seconds', 60)} s)"
            )
        if not any(contains_term(first[:limit_fantasy], w) for w in DRAGON_WORDS):
            warnings.append(f"bloco 1: nenhum sinal do dragão nos primeiros {limit_fantasy} caracteres")

    for e in errors:
        print(f"  ERRO: {e}")
    for w in warnings:
        print(f"  AVISO: {w}")

    if errors:
        print(f"INCONSISTENTE: {project_dir} — {len(errors)} erro(s), {len(warnings)} aviso(s)")
        return 1
    print(f"OK: {project_dir} — nenhuma inconsistência bloqueante ({len(warnings)} aviso(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
