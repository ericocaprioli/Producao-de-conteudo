#!/usr/bin/env python3
"""Teste de equivalência de clique: compara a embalagem da referência e a nova proposta.

Uso:
    python3 scripts/validate_packaging_alignment.py PROJECT_DIR
    python3 scripts/validate_packaging_alignment.py PROJECT_DIR --title "Título avulso"

Lê:
  - 02_reference_analysis/viral-wave-package.yaml  (reference_surface + functional_tags da referência)
  - 09_seo/title-options.yaml                        (fichas title_option da proposta)
  - 09_seo/packaging.yaml                            (functional_tags + thumbnail da proposta)
  - 05_character_bible/character-bible.yaml          (opcional: aparência no prompt)

Com project.yaml → selected_title preenchido, avalia só o título escolhido; senão, todas as opções.

Sinais relatados:
  PROMISE_ALIGNED, EMOTION_ALIGNED, VISUAL_HOOK_ALIGNED, FANTASY_HOOK_ALIGNED,
  CURIOSITY_GAP_ALIGNED, TEXT_TOO_CLOSE, COMPOSITION_TOO_CLOSE, PROMISE_TOO_GENERIC,
  REVIEW_REQUIRED

A comparação é funcional. Compartilhar "mulher + dragão" é elemento de gênero e não torna duas
thumbnails iguais: só dimensões específicas da composição (pose, enquadramento, ângulo, posição
do dragão, cenário, objeto, paleta/luz, expressão, texto, layout) contam como cópia.

Resultado por item: PASS, REVIEW_REQUIRED ou FAIL. Código de saída 1 se algum item der FAIL.
"""

import argparse
import sys
from pathlib import Path

from wb_common import (
    contains_term, genre_stems, load_config, load_first, load_project, overlap, title_too_close, tokens,
)


def tagset(tags: dict, key: str) -> set[str]:
    value = (tags or {}).get(key) or []
    return set(value) if isinstance(value, list) else {value}


def signal_groups(title: str, title_rules: dict) -> list[str]:
    return [
        g for g, words in (title_rules.get("keyword_groups") or {}).items()
        if any(contains_term(title, w) for w in words)
    ]


def has_turn(title: str, markers: list[str]) -> bool:
    low = f" {title.lower()} "
    return any((m in low) if not m.strip().isalpha() else contains_term(title, m.strip()) for m in markers)


def dimension_value(comp: dict, dim) -> str:
    if isinstance(dim, list):
        return " / ".join(str(comp.get(d, "")) for d in dim)
    return str(comp.get(dim, ""))


def same_dimension(a: str, b: str, genre: set[str], min_jaccard: float) -> bool:
    a_norm, b_norm = " ".join(tokens(a)), " ".join(tokens(b))
    if not a_norm or not b_norm:
        return False
    if a_norm == b_norm:
        return True
    o = overlap(a, b, genre)
    return bool(o["shared"]) and o["jaccard"] >= min_jaccard


def evaluate_title(option: dict, ref: dict, ref_tags: dict, prop_tags: dict, thumb_text: str,
                   mode: str, rules: dict, title_rules: dict, genre: set[str]) -> tuple[str, list[str]]:
    pk = rules.get("packaging") or {}
    align = rules.get("alignment") or {}
    title = option.get("text", "")
    lines, fails, reviews = [], [], []
    has_ref = mode != "original_channel_story" and bool(ref.get("title"))

    groups = signal_groups(title, title_rules)
    generic = len(groups) < pk.get("min_title_signal_groups", 3)
    if "viral_slots_preserved" in option:
        slots = option.get("viral_slots_preserved") or []
        if mode == "adjacent_trend" and len(slots) < pk.get("min_title_slots_preserved", 3):
            generic = True
    else:
        slots = "sem ficha"
        reviews.append("título sem ficha title_option: slots preservados não declarados")
    lines.append(f"PROMISE_TOO_GENERIC: {'sim' if generic else 'não'} (sinais {groups}; slots declarados {slots})")
    if generic:
        fails.append("PROMISE_TOO_GENERIC")

    if not has_ref:
        lines.append("comparação com a referência: não aplicável (sem referência)")
        return ("FAIL" if fails else "PASS"), lines

    close, detail = title_too_close(title, ref.get("title", ""), genre, align)
    reused_names = [n for n in ref.get("names") or [] if contains_term(title, n)]
    text_close = close or bool(reused_names)
    lines.append(f"TEXT_TOO_CLOSE: {'sim' if text_close else 'não'} ({detail}{'; nomes ' + str(reused_names) if reused_names else ''})")
    if text_close:
        fails.append("TEXT_TOO_CLOSE")
    declared = option.get("reference_phrase_overlap")
    if declared == "low" and text_close:
        reviews.append("ficha declara reference_phrase_overlap: low, mas o texto está próximo da referência")
    if declared not in ("low", "review_required"):
        reviews.append("reference_phrase_overlap deve ser 'low' ou 'review_required'")

    def aligned(flag: str, ok: bool | None, why: str) -> None:
        if ok is None:
            lines.append(f"{flag}: REVIEW_REQUIRED ({why})")
            reviews.append(flag)
        else:
            lines.append(f"{flag}: {'sim' if ok else 'não'} ({why})")
            if not ok:
                reviews.append(flag)

    for flag, key in (("PROMISE_ALIGNED", "promise"), ("EMOTION_ALIGNED", "emotion")):
        r, p = tagset(ref_tags, key), tagset(prop_tags, key)
        if not r or not p:
            aligned(flag, None, f"functional_tags.{key} ausente")
        else:
            ok = bool(r & p) and (key != "promise" or "reversal" in groups)
            aligned(flag, ok, f"comum: {sorted(r & p)}")

    r, p = tagset(ref_tags, "fantasy_hook"), tagset(prop_tags, "fantasy_hook")
    fantasy_words = (title_rules.get("keyword_groups") or {}).get("fantastical") or []
    visible = any(contains_term(title, w) or contains_term(thumb_text, w) for w in fantasy_words)
    if not r or not p:
        aligned("FANTASY_HOOK_ALIGNED", None, "functional_tags.fantasy_hook ausente")
    else:
        aligned("FANTASY_HOOK_ALIGNED", bool(r & p) and visible, f"comum: {sorted(r & p)}; visível no título: {visible}")

    gap_ref = (ref_tags or {}).get("curiosity_gap")
    if not gap_ref or not option.get("curiosity_gap"):
        aligned("CURIOSITY_GAP_ALIGNED", None, "curiosity_gap ausente na referência ou na ficha")
    else:
        turn = has_turn(title, title_rules.get("turn_markers") or [])
        aligned("CURIOSITY_GAP_ALIGNED", turn, f"marcador de virada no título: {turn}")

    if not option.get("promise_delivered_by"):
        reviews.append("promise_delivered_by vazio — onde a história entrega a promessa?")

    if fails:
        return "FAIL", lines + [f"revisar: {r}" for r in reviews]
    return ("REVIEW_REQUIRED" if reviews else "PASS"), lines + [f"revisar: {r}" for r in reviews]


def evaluate_thumbnail(thumb: dict, ref: dict, ref_tags: dict, prop_tags: dict, bible: dict | None,
                       mode: str, rules: dict, genre: set[str]) -> tuple[str, list[str]]:
    pk = rules.get("packaging") or {}
    align = rules.get("alignment") or {}
    lines, fails, reviews = [], [], []
    prompt = thumb.get("prompt_en", "")
    comp = thumb.get("composition") or {}

    if not thumb.get("concept") or not prompt:
        reviews.append("conceito ou prompt_en da thumbnail vazio")
    for term in pk.get("required_prompt_terms", []):
        if term.lower() not in prompt.lower():
            reviews.append(f"prompt sem '{term}'")
    if not thumb.get("text_intended"):
        for term in pk.get("required_negative_terms", []):
            if term.lower() not in prompt.lower():
                reviews.append(f"prompt sem '{term}' (use text_intended: true se o texto for proposital)")
    if bible:
        for who, field in (("protagonista", ("protagonist", "appearance")), ("dragão", ("dragon", "appearance"))):
            appearance = (bible.get(field[0]) or {}).get(field[1], "")
            o = overlap(appearance, prompt, set())
            if appearance and len(o["shared"]) < 2:
                reviews.append(f"prompt não repete a aparência fixa do(a) {who} da ficha")

    thumb_ref = ref.get("thumbnail") or {}
    if mode == "original_channel_story" or not thumb_ref:
        lines.append("comparação com a referência: não aplicável (sem thumbnail de referência)")
    else:
        r, p = tagset(ref_tags, "visual_hook"), tagset(prop_tags, "visual_hook")
        if not r or not p:
            lines.append("VISUAL_HOOK_ALIGNED: REVIEW_REQUIRED (functional_tags.visual_hook ausente)")
            reviews.append("VISUAL_HOOK_ALIGNED")
        else:
            coverage = len(r & p) / len(r)
            ok = coverage >= pk.get("visual_hook_min_coverage", 0.75)
            lines.append(f"VISUAL_HOOK_ALIGNED: {'sim' if ok else 'não'} (cobertura {coverage:.0%}; faltam {sorted(r - p)})")
            if not ok:
                reviews.append("VISUAL_HOOK_ALIGNED")

        ref_comp = thumb_ref.get("composition") or {}
        dims = pk.get("composition_dimensions") or []
        min_j = pk.get("composition_dimension_min_jaccard", 0.6)
        same = [
            (" / ".join(d) if isinstance(d, list) else d) for d in dims
            if (all(same_dimension(str(comp.get(x, "")), str(ref_comp.get(x, "")), genre, min_j) for x in d)
                if isinstance(d, list)
                else same_dimension(dimension_value(comp, d), dimension_value(ref_comp, d), genre, min_j))
        ]
        missing = [(" / ".join(d) if isinstance(d, list) else d) for d in dims
                   if not (all(comp.get(x) for x in d) if isinstance(d, list) else comp.get(d))]
        too_close = len(same) >= pk.get("composition_too_close_min_matches", 4)
        lines.append(f"COMPOSITION_TOO_CLOSE: {'sim' if too_close else 'não'} (dimensões iguais à referência: {same or 'nenhuma'})")
        if too_close:
            fails.append("COMPOSITION_TOO_CLOSE")
        elif same:
            reviews.append(f"dimensões que a regra manda alterar continuam iguais: {same}")
        if missing:
            reviews.append(f"composição sem as dimensões {missing}")

        text_close, detail = title_too_close(thumb.get("text", ""), thumb_ref.get("text", ""), genre, align)
        o = overlap(prompt, thumb_ref.get("description", ""), genre)
        paraphrase = (len(o["shared"]) >= pk.get("thumbnail_prompt_paraphrase_min_shared", 3)
                      and o["jaccard"] >= pk.get("thumbnail_prompt_paraphrase_min_jaccard", 0.4))
        lines.append(f"TEXT_TOO_CLOSE (thumbnail): {'sim' if text_close or paraphrase else 'não'} "
                     f"(texto: {detail or 'sem texto'}; prompt×descrição Jaccard {o['jaccard']:.2f})")
        if text_close or paraphrase:
            fails.append("TEXT_TOO_CLOSE")

    lines += [f"revisar: {r}" for r in reviews]
    if fails:
        return "FAIL", lines
    return ("REVIEW_REQUIRED" if reviews else "PASS"), lines


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida a equivalência de clique da embalagem.")
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--title", help="avaliar um título avulso em vez das fichas")
    args = parser.parse_args()

    pdir = args.project_dir
    if not pdir.exists():
        print(f"ERRO: diretório de projeto não encontrado: {pdir}", file=sys.stderr)
        return 2

    project = load_project(pdir)
    mode = project.get("mode", "adjacent_trend")
    rules = load_config("trend-rules.yaml")
    title_rules = load_config("title-rules.yaml")
    genre = genre_stems(rules.get("genre_terms") or [])

    package = load_first(pdir / "02_reference_analysis" / "viral-wave-package.yaml") or {}
    ref = package.get("reference_surface") or {}
    ref_tags = package.get("functional_tags") or {}
    packaging = load_first(pdir / "09_seo" / "packaging.yaml") or {}
    prop_tags = packaging.get("functional_tags") or {}
    thumb = packaging.get("thumbnail") or {}
    bible = load_first(pdir / "05_character_bible" / "character-bible.yaml")

    if mode != "original_channel_story" and not package:
        print("REVIEW_REQUIRED: viral-wave-package.yaml ausente — não há referência para comparar")
        return 1

    if args.title:
        options = [{"text": args.title, "reference_phrase_overlap": "review_required"}]
    else:
        options = (load_first(pdir / "09_seo" / "title-options.yaml") or {}).get("title_options") or []
        selected = project.get("selected_title")
        if selected:
            options = [o for o in options if o.get("text") == selected] or [{"text": selected}]
    if not options:
        print("ERRO: nenhum título para avaliar (09_seo/title-options.yaml)", file=sys.stderr)
        return 2

    results = []
    for i, option in enumerate(options, 1):
        verdict, lines = evaluate_title(option, ref, ref_tags, prop_tags, thumb.get("text", ""),
                                        mode, rules, title_rules, genre)
        results.append(verdict)
        print(f"== Título {i}: {option.get('text')}")
        for ln in lines:
            print(f"  {ln}")
        print(f"  RESULTADO: {verdict}\n")

    if thumb:
        verdict, lines = evaluate_thumbnail(thumb, ref, ref_tags, prop_tags, bible, mode, rules, genre)
        results.append(verdict)
        print("== Thumbnail")
        for ln in lines:
            print(f"  {ln}")
        print(f"  RESULTADO: {verdict}\n")
    else:
        results.append("REVIEW_REQUIRED")
        print("== Thumbnail\n  REVIEW_REQUIRED: 09_seo/packaging.yaml sem bloco 'thumbnail'\n")

    overall = "FAIL" if "FAIL" in results else "REVIEW_REQUIRED" if "REVIEW_REQUIRED" in results else "PASS"
    print(f"RESULTADO GERAL: {overall}")
    return 1 if overall == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
