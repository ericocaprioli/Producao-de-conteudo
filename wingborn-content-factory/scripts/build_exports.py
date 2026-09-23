#!/usr/bin/env python3
"""Monta os arquivos finais de exportação de um projeto Wingborn Content Factory.

Uso:
    python3 build_exports.py <caminho-do-projeto>

Lê:
  - 06_script/block-01.txt .. block-05.txt
  - 08_scene_prompts/scenes.json (lista de objetos no formato de templates/scene-prompt.json)
  - 09_seo/description.txt, 09_seo/tags.txt, 09_seo/thumbnail-prompt.txt (se existirem)
  - 00_input/project.yaml (para metadados do manifesto)

Escreve em 11_exports/:
  - script_full.txt
  - block-01.txt .. block-05.txt (normalizados)
  - tts_plain_text.txt (somente narração, sem marcadores)
  - image-prompts.json
  - image-prompts-en.txt
  - thumbnail_prompt_en.txt
  - youtube_description.txt
  - tags.txt
  - production_manifest.json

Este script recusa exportar se os blocos não passarem em validate_blocks.py, porque a
exportação não deve mascarar um roteiro inválido.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

SCRIPT_DIR = Path(__file__).resolve().parent

PRODUCTION_MARKER_PATTERN = re.compile(
    r"\[(CENA|SCENE|PAUSE|PAUSA|MUSIC|MÚSICA|SFX|SOM|NOTE|NOTA)\][^\n]*\n?",
    flags=re.IGNORECASE,
)


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = PRODUCTION_MARKER_PATTERN.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def run_block_validation(project_dir: Path) -> bool:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "validate_blocks.py"), str(project_dir)],
        capture_output=True,
        text=True,
    )
    print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    return result.returncode == 0


def load_project_meta(project_dir: Path) -> dict:
    if yaml is None:
        return {}
    for candidate in (project_dir / "00_input" / "project.yaml", project_dir / "project.yaml"):
        if candidate.exists():
            return yaml.safe_load(candidate.read_text(encoding="utf-8")) or {}
    return {}


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2

    project_dir = Path(sys.argv[1])
    if not project_dir.exists():
        print(f"ERRO: diretório de projeto não encontrado: {project_dir}", file=sys.stderr)
        return 2

    print("Validando blocos antes de exportar...")
    if not run_block_validation(project_dir):
        print("ERRO: blocos inválidos. Corrija os blocos antes de exportar.", file=sys.stderr)
        return 1

    script_dir = project_dir / "06_script"
    exports_dir = project_dir / "11_exports"
    exports_dir.mkdir(parents=True, exist_ok=True)

    generated_files: list[str] = []
    char_counts: list[int] = []
    block_texts: list[str] = []

    for n in range(1, 6):
        src = script_dir / f"block-{n:02d}.txt"
        raw = src.read_text(encoding="utf-8")
        normalized = normalize_text(raw)
        block_texts.append(normalized)
        char_counts.append(len(normalized.rstrip("\n")))

        out_path = exports_dir / f"block-{n:02d}.txt"
        out_path.write_text(normalized, encoding="utf-8")
        generated_files.append(out_path.name)

    script_full_path = exports_dir / "script_full.txt"
    script_full_path.write_text("\n".join(block_texts), encoding="utf-8")
    generated_files.append(script_full_path.name)

    tts_path = exports_dir / "tts_plain_text.txt"
    tts_path.write_text("\n".join(t.strip() for t in block_texts) + "\n", encoding="utf-8")
    generated_files.append(tts_path.name)

    scenes_src = project_dir / "08_scene_prompts" / "scenes.json"
    scenes = []
    if scenes_src.exists():
        scenes = json.loads(scenes_src.read_text(encoding="utf-8"))
        scenes_out = exports_dir / "image-prompts.json"
        scenes_out.write_text(json.dumps(scenes, indent=2, ensure_ascii=False), encoding="utf-8")
        generated_files.append(scenes_out.name)

        lines = []
        for s in scenes:
            lines.append(f"[Scene {s.get('scene')}] (block {s.get('block')}) {s.get('prompt_en', '')}")
            neg = s.get("negative_prompt")
            if neg:
                lines.append(f"  negative: {neg}")
        scenes_txt_out = exports_dir / "image-prompts-en.txt"
        scenes_txt_out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        generated_files.append(scenes_txt_out.name)
    else:
        print("AVISO: 08_scene_prompts/scenes.json não encontrado — pulando prompts de imagem", file=sys.stderr)

    seo_dir = project_dir / "09_seo"
    thumb_src = seo_dir / "thumbnail-prompt.txt"
    if thumb_src.exists():
        out = exports_dir / "thumbnail_prompt_en.txt"
        out.write_text(normalize_text(thumb_src.read_text(encoding="utf-8")), encoding="utf-8")
        generated_files.append(out.name)

    desc_src = seo_dir / "description.txt"
    if desc_src.exists():
        out = exports_dir / "youtube_description.txt"
        out.write_text(normalize_text(desc_src.read_text(encoding="utf-8")), encoding="utf-8")
        generated_files.append(out.name)

    tags_src = seo_dir / "tags.txt"
    if tags_src.exists():
        out = exports_dir / "tags.txt"
        out.write_text(normalize_text(tags_src.read_text(encoding="utf-8")), encoding="utf-8")
        generated_files.append(out.name)

    meta = load_project_meta(project_dir)
    manifest = {
        "project_id": meta.get("id", project_dir.name),
        "language": meta.get("language", ""),
        "blocks": 5,
        "characters_per_block": char_counts,
        "selected_title": meta.get("selected_title", ""),
        "reference_url": (meta.get("reference") or {}).get("url", ""),
        "approved_gates": meta.get("approved_gates", []),
        "generated_files": generated_files,
    }
    manifest_path = exports_dir / "production_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    generated_files.append(manifest_path.name)

    print(f"OK: exportado para {exports_dir}")
    for f in generated_files:
        print(f"  - {f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
