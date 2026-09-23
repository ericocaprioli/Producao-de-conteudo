#!/usr/bin/env python3
"""Verifica se uma direção surfa a onda viral sem virar adaptação disfarçada.

Uso:
    python3 scripts/validate_trend_alignment.py PROJECT_DIR
    python3 scripts/validate_trend_alignment.py PROJECT_DIR --all
    python3 scripts/validate_trend_alignment.py PROJECT_DIR --direction B
    python3 scripts/validate_trend_alignment.py PROJECT_DIR --directions-file outro.yaml

Lê:
  - 00_input/project.yaml (mode)
  - 02_reference_analysis/viral-wave-package.yaml (pacote viral + superfície da referência)
  - 04_selected_direction/selected-direction.yaml, se existir (padrão após /escolher-direcao)
  - 03_original_directions/directions.yaml (padrão antes da escolha, ou com --all)

Só se aplica ao modo adjacent_trend. Classificações:
  ALIGNED         — surfa a tendência e possui realização narrativa nova
  TOO_DISTANT     — história original, mas distante demais para a onda escolhida
  TOO_CLOSE       — risco elevado de adaptação disfarçada
  REVIEW_REQUIRED — dados insuficientes para decidir automaticamente

Combina regras determinísticas, a lista de eventos proibidos e os campos preenchidos pelo
modelo. Termos de gênero (mãe, filha, dragão...) são ignorados na comparação de superfície:
manter os slots de mercado não é cópia; repetir a sequência concreta é.

Código de saída: 0 se todas as direções avaliadas forem ALIGNED (ou modo não aplicável),
1 caso contrário, 2 em erro de uso.
"""

import argparse
import sys
from pathlib import Path

from wb_common import (
    contains_term, event_match, genre_stems, has_prefix_keyword, load_config, load_first, load_project,
    load_yaml, longest_increasing_run, overlap, stem, title_too_close, tokens,
)

LABELS = {
    "ALIGNED": "surfa a tendência e possui realização narrativa nova",
    "TOO_DISTANT": "história original, mas distante demais para a onda escolhida",
    "TOO_CLOSE": "risco elevado de adaptação disfarçada",
    "REVIEW_REQUIRED": "dados insuficientes para decidir automaticamente",
}


def evaluate(direction: dict, package: dict, rules: dict) -> tuple[str, list[str]]:
    align = rules.get("alignment") or {}
    slot_defs = rules.get("slots") or {}
    wave = package.get("viral_wave") or {}
    ref = package.get("reference_surface") or {}
    overrides = package.get("slot_keywords") or {}

    # Nomes próprios (da referência e da direção) não contam na semelhança de superfície:
    # trocar só os nomes não pode fazer uma sequência copiada parecer nova.
    proper_names = list(ref.get("names") or []) + [
        c.get("name", "") for c in direction.get("characters") or [] if isinstance(c, dict)
    ]
    genre = genre_stems(rules.get("genre_terms") or []) | {stem(t) for n in proper_names for t in tokens(n)}

    report: list[str] = []
    hard: list[str] = []
    soft: list[str] = []
    review: list[str] = []

    chain = [s for s in (direction.get("causal_chain") or []) if isinstance(s, str) and s.strip()]
    evidence = " ".join([
        direction.get("logline", ""), direction.get("title_draft", ""), direction.get("thumbnail_concept", ""),
        direction.get("revelation_mechanism", ""), direction.get("climax", ""), direction.get("ending", ""),
        " ".join(chain),
    ])

    # 1. Slots preservados
    declared = list(dict.fromkeys(direction.get("preserved_slots") or []))
    unknown_slots = [s for s in declared if s not in slot_defs]
    valid = [s for s in declared if s in slot_defs]
    wave_slots = wave.get("preserved_slots") or list(slot_defs)
    outside_wave = [s for s in valid if s not in wave_slots]
    unverified = [
        s for s in valid
        if not has_prefix_keyword(evidence, overrides.get(s) or slot_defs[s].get("keywords", []))
    ]
    verified = len(valid) - len(unverified)
    report.append(f"slots preservados: {len(valid)} declarados {valid} — com evidência no texto: {verified}")
    if unknown_slots:
        review.append(f"slots desconhecidos {unknown_slots} (válidos: {list(slot_defs)})")
    if outside_wave:
        review.append(f"slots {outside_wave} não constam em viral_wave.preserved_slots")
    if unverified:
        review.append(f"slots declarados sem evidência no texto da direção: {unverified}")
    if len(valid) > align.get("max_slots", 5):
        review.append(f"{len(valid)} slots preservados, acima do intervalo 4–5 — conferir se não é cópia")

    # 2. Elementos concretos alterados
    ce_rules = rules.get("changed_elements") or {}
    vocab = set(ce_rules.get("vocabulary") or [])
    changed = [c for c in dict.fromkeys(direction.get("changed_elements") or []) if c in vocab]
    missing_mandatory = [m for m in ce_rules.get("mandatory") or [] if m not in changed]
    report.append(f"elementos concretos alterados: {len(changed)} (mínimo {ce_rules.get('minimum_count', 5)})")
    if len(changed) < ce_rules.get("minimum_count", 5):
        soft.append(f"apenas {len(changed)} elementos concretos alterados declarados")
    if missing_mandatory:
        review.append(f"alterações obrigatórias não declaradas: {missing_mandatory}")

    # 3. Nomes e personagens
    characters = direction.get("characters") or []
    char_names = [c.get("name", "") for c in characters if isinstance(c, dict) and c.get("name")]
    reused = [n for n in (ref.get("names") or []) if contains_term(evidence + " " + " ".join(char_names), n)]
    if not char_names:
        review.append("direção sem personagens nomeados")
    if reused:
        hard.append(f"nomes da referência reutilizados: {reused}")
    report.append(f"nomes: {'REUTILIZADOS ' + str(reused) if reused else 'novos'} {char_names}")

    # 4. Cadeia causal
    lo, hi = align.get("causal_chain_min_steps", 7), align.get("causal_chain_max_steps", 10)
    if not lo <= len(chain) <= hi:
        review.append(f"cadeia causal com {len(chain)} passos (esperado {lo}–{hi})")
    ref_chain = ref.get("causal_chain") or []
    pairs = []
    for i, ref_step in enumerate(ref_chain):
        for j, step in enumerate(chain):
            if event_match(step, ref_step, genre, align):
                pairs.append((i, j))
                break
    in_order = longest_increasing_run(pairs)
    report.append(f"cadeia causal: {len(chain)} passos — coincidências com a referência: {len(pairs)}, em ordem: {in_order}")
    if in_order >= align.get("chain_order_too_close", 3):
        hard.append(f"{in_order} passos da cadeia da referência repetidos na mesma ordem")

    # 5. Eventos proibidos
    prohibited = wave.get("prohibited_events") or []
    fields = chain + [direction.get(k, "") for k in ("logline", "revelation_mechanism", "climax", "ending")]
    reused_events = [ev for ev in prohibited if any(event_match(s, ev, genre, align) for s in fields if s)]
    report.append(f"eventos proibidos reutilizados: {len(reused_events)}")
    for ev in reused_events:
        report.append(f"    - {ev}")
    if len(reused_events) >= align.get("prohibited_events_too_close", 2):
        hard.append(f"{len(reused_events)} eventos proibidos reaproveitados")
    elif reused_events:
        soft.append("1 evento proibido reaproveitado")

    # 6. Revelação, clímax e final
    for key, label in (("revelation_mechanism", "mecanismo de revelação"), ("climax", "clímax"), ("ending", "final")):
        mine, theirs = direction.get(key, ""), ref.get(key, "")
        if not mine:
            review.append(f"{label} não preenchido")
            continue
        if theirs and event_match(mine, theirs, genre, align):
            o = overlap(mine, theirs, genre)
            soft.append(f"{label} semelhante ao da referência {o['shared']}")
            report.append(f"{label}: SEMELHANTE à referência {o['shared']}")
        else:
            report.append(f"{label}: novo")

    # 7. Título
    title = direction.get("title_draft", "")
    if not title:
        review.append("título provisório (title_draft) não preenchido")
    else:
        close, detail = title_too_close(title, ref.get("title", ""), genre, align)
        report.append(f"título: {'QUASE IDÊNTICO' if close else 'próprio'} ({detail})")
        if close:
            hard.append(f"título quase idêntico ao da referência ({detail})")

    # 8. Thumbnail
    concept = direction.get("thumbnail_concept", "")
    ref_thumb = (ref.get("thumbnail") or {}).get("description", "")
    if not concept:
        review.append("conceito de thumbnail não preenchido")
    elif ref_thumb:
        o = overlap(concept, ref_thumb, genre)
        if len(o["shared"]) >= 3 and o["jaccard"] >= 0.4:
            soft.append(f"conceito de thumbnail semelhante ao da referência {o['shared']}")
            report.append(f"thumbnail: SEMELHANTE {o['shared']}")
        else:
            report.append(f"thumbnail: composição própria (Jaccard {o['jaccard']:.2f})")

    if not direction.get("wave_justification"):
        review.append("justificativa de pertencimento à onda não preenchida")

    # Perfil de proximidade (informativo)
    level = direction.get("proximity_level")
    profile = (rules.get("proximity_profiles") or {}).get(level)
    if profile:
        notes = []
        expected = profile["slots_preserved"]
        if len(valid) < expected or (level == "high" and len(valid) != expected):
            notes.append(f"esperado {expected} slots")
        lacking = [m for m in profile.get("must_change", []) if m not in changed]
        if lacking:
            notes.append(f"perfil pede alterar {lacking}")
        report.append(f"perfil '{level}': {'ok' if not notes else 'AVISO — ' + '; '.join(notes)}")

    if hard or len(soft) >= 2:
        verdict = "TOO_CLOSE"
    elif len(valid) < align.get("min_slots", 4):
        verdict = "TOO_DISTANT"
        report.append(f"apenas {len(valid)} slots preservados (mínimo {align.get('min_slots', 4)})")
    elif soft or review:
        verdict = "REVIEW_REQUIRED"
    else:
        verdict = "ALIGNED"

    report += [f"TOO_CLOSE: {h}" for h in hard] + [f"sinal de proximidade: {s}" for s in soft]
    report += [f"revisar: {r}" for r in review]
    return verdict, report


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida alinhamento com a tendência (adjacent_trend).")
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--direction", help="avaliar apenas a direção com este id (A, B, C...)")
    parser.add_argument("--all", action="store_true", help="avaliar todas as direções de directions.yaml")
    parser.add_argument("--directions-file", type=Path, help="arquivo alternativo com 'directions: [...]'")
    args = parser.parse_args()

    pdir = args.project_dir
    if not pdir.exists():
        print(f"ERRO: diretório de projeto não encontrado: {pdir}", file=sys.stderr)
        return 2

    mode = load_project(pdir).get("mode")
    if mode != "adjacent_trend":
        print(f"NOT_APPLICABLE: mode '{mode}' — este validador só se aplica a adjacent_trend")
        return 0

    package = load_first(pdir / "02_reference_analysis" / "viral-wave-package.yaml")
    if package is None:
        print("REVIEW_REQUIRED: 02_reference_analysis/viral-wave-package.yaml não encontrado — crie o pacote viral primeiro")
        return 1

    selected = pdir / "04_selected_direction" / "selected-direction.yaml"
    if args.directions_file:
        directions = load_yaml(args.directions_file).get("directions") or []
    elif selected.exists() and not args.all and not args.direction:
        directions = [load_yaml(selected)]
    else:
        path = pdir / "03_original_directions" / "directions.yaml"
        if not path.exists():
            print(f"ERRO: {path} não encontrado", file=sys.stderr)
            return 2
        directions = load_yaml(path).get("directions") or []

    if args.direction:
        directions = [d for d in directions if str(d.get("id")) == args.direction]
    if not directions:
        print("ERRO: nenhuma direção encontrada para avaliar", file=sys.stderr)
        return 2

    rules = load_config("trend-rules.yaml")
    all_aligned = True
    for d in directions:
        verdict, report = evaluate(d, package, rules)
        all_aligned &= verdict == "ALIGNED"
        print(f"== Direção {d.get('id', '?')} (proximidade: {d.get('proximity_level', '?')}) ==")
        for line in report:
            print(f"  {line}")
        print(f"  CLASSIFICAÇÃO: {verdict} — {LABELS[verdict]}\n")
    return 0 if all_aligned else 1


if __name__ == "__main__":
    sys.exit(main())
