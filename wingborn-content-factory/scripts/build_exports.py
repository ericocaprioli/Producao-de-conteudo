#!/usr/bin/env python3
"""Monta os arquivos finais de exportação de um projeto Wingborn Content Factory.

Uso:
    python3 scripts/build_exports.py <caminho-do-projeto>

Lê 06_script/, 08_scene_prompts/scenes.json, 09_seo/ (description.txt, tags.txt,
thumbnail-prompt.txt ou packaging.yaml → thumbnail.prompt_en) e 00_input/project.yaml.

Escreve em 11_exports/: script_full.txt, block-01..05.txt, tts_plain_text.txt,
image-prompts.json, image-prompts-en.txt, thumbnail_prompt_en.txt, youtube_description.txt,
tags.txt e production_manifest.json.

Recusa exportar se os blocos não passarem em validate_blocks.py.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

from wb_common import count_units, load_config, load_first, load_project, normalize_newlines

SCRIPT_DIR = Path(__file__).resolve().parent

PRODUCTION_MARKERS = [
    re.compile(r"\[(CENA|SCENE|PAUSE|PAUSA|MUSIC|MÚSICA|SFX|SOM|NOTE|NOTA|CUT|CORTE)[^\]]*\]", re.IGNORECASE),
    re.compile(r"^\s*(BLOCK|BLOCO)\s*\d+\s*[:\-—].*$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^\s*#+\s.*$", re.MULTILINE),
]


def clean(text: str) -> str:
    text = normalize_newlines(text)
    for pattern in PRODUCTION_MARKERS:
        text = pattern.sub("", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def blocks_are_valid(project_dir: Path) -> bool:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "validate_blocks.py"), str(project_dir)],
        capture_output=True, text=True,
    )
    print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    return result.returncode == 0


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2

    pdir = Path(sys.argv[1])
    if not pdir.exists():
        print(f"ERRO: diretório de projeto não encontrado: {pdir}", file=sys.stderr)
        return 2

    print("Validando blocos antes de exportar...")
    if not blocks_are_valid(pdir):
        print("ERRO: blocos inválidos. Corrija os blocos antes de exportar.", file=sys.stderr)
        return 1

    meta = load_project(pdir)
    n_blocks = meta.get("blocks", 5)
    out = pdir / "11_exports"
    out.mkdir(parents=True, exist_ok=True)
    generated: list[str] = []

    def write(name: str, content: str) -> None:
        (out / name).write_text(content, encoding="utf-8")
        generated.append(name)

    texts = []
    for n in range(1, n_blocks + 1):
        text = clean((pdir / "06_script" / f"block-{n:02d}.txt").read_text(encoding="utf-8"))
        texts.append(text)
        write(f"block-{n:02d}.txt", text)

    # Linha em branco entre blocos: o narrador trata cada bloco como parágrafo próprio (pausa longa).
    write("script_full.txt", "\n".join(texts))
    write("tts_plain_text.txt", "\n\n".join(t.strip() for t in texts) + "\n")

    scenes_src = pdir / "08_scene_prompts" / "scenes.json"
    if scenes_src.exists():
        scenes = sorted(json.loads(scenes_src.read_text(encoding="utf-8")), key=lambda s: s.get("scene", 0))
        write("image-prompts.json", json.dumps(scenes, indent=2, ensure_ascii=False) + "\n")
        lines = []
        for s in scenes:
            lines.append(f"[Scene {s.get('scene')} | block {s.get('block')}] {s.get('prompt_en', '')}")
            if s.get("negative_prompt"):
                lines.append(f"  negative: {s['negative_prompt']}")
        write("image-prompts-en.txt", "\n".join(lines) + "\n")
    else:
        print("AVISO: 08_scene_prompts/scenes.json não encontrado — prompts de imagem não exportados", file=sys.stderr)

    seo = pdir / "09_seo"
    thumb_txt = seo / "thumbnail-prompt.txt"
    packaging = load_first(seo / "packaging.yaml") or {}
    thumb_prompt = (packaging.get("thumbnail") or {}).get("prompt_en", "")
    if thumb_txt.exists():
        write("thumbnail_prompt_en.txt", clean(thumb_txt.read_text(encoding="utf-8")))
    elif thumb_prompt:
        write("thumbnail_prompt_en.txt", thumb_prompt.strip() + "\n")
    else:
        print("AVISO: nenhum prompt de thumbnail encontrado", file=sys.stderr)

    for src, dst in (("description.txt", "youtube_description.txt"), ("tags.txt", "tags.txt")):
        if (seo / src).exists():
            write(dst, clean((seo / src).read_text(encoding="utf-8")))
        else:
            print(f"AVISO: 09_seo/{src} não encontrado", file=sys.stderr)

    length = meta.get("length") or {}
    counts = [count_units(t, length.get("unit", "characters"), length.get("count_spaces", True)) for t in texts]
    cps = load_config("retention-rules.yaml").get("narration_chars_per_second", 15)
    total_chars = sum(count_units(t) for t in texts)
    manifest = {
        "project_id": meta.get("id", pdir.name),
        "mode": meta.get("mode", ""),
        "language": meta.get("language", ""),
        "blocks": n_blocks,
        "characters_per_block": counts,
        "estimated_duration_minutes": round(total_chars / cps / 60, 1),
        "selected_title": meta.get("selected_title", ""),
        "reference_url": (meta.get("reference") or {}).get("url", ""),
        "approved_gates": meta.get("approved_gates", []),
        "generated_files": generated + ["production_manifest.json"],
    }
    write("production_manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    print(f"OK: exportado para {out}")
    for f in generated:
        print(f"  - {f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
