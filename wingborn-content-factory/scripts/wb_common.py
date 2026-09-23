"""Funções compartilhadas pelos validadores do Wingborn Content Factory."""

import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERRO: PyYAML não está instalado. Instale com: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"

MODES = ("adjacent_trend", "reference_adaptation", "original_channel_story")

STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "at", "by", "for", "with", "from", "into", "onto",
    "as", "is", "was", "were", "be", "been", "are", "it", "its", "that", "this", "these", "those", "who",
    "whom", "which", "what", "when", "where", "while", "his", "him", "he", "they", "them", "their", "then",
    "than", "but", "not", "no", "so", "if", "all", "one", "only", "own", "same", "there", "here", "has",
    "have", "had", "will", "would", "can", "could", "did", "does", "do", "after", "before", "over", "under",
    "up", "down", "out", "about", "again", "back", "every", "each", "any", "some", "most", "more", "very",
    "o", "os", "as", "um", "uma", "de", "do", "da", "dos", "das", "em", "no", "na", "nos", "nas", "por",
    "para", "com", "que", "e", "ou", "se", "sua", "seu", "suas", "seus", "ela", "ele", "mas", "até",
}


def load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def load_config(name: str) -> dict:
    path = CONFIG_DIR / name
    return load_yaml(path) if path.exists() else {}


def find_project_yaml(project_dir: Path) -> Path | None:
    for candidate in (project_dir / "00_input" / "project.yaml", project_dir / "project.yaml"):
        if candidate.exists():
            return candidate
    return None


def load_project(project_dir: Path) -> dict:
    path = find_project_yaml(project_dir)
    return load_yaml(path) if path else {}


def load_first(*paths: Path) -> dict | None:
    for p in paths:
        if p.exists():
            return load_yaml(p)
    return None


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def count_units(text: str, unit: str = "characters", count_spaces: bool = True) -> int:
    """Conta o texto narrado. Quebras de linha internas contam; espaços nas bordas do arquivo não."""
    body = normalize_newlines(text).strip()
    if unit == "words":
        return len(body.split())
    if not count_spaces:
        return len(re.sub(r"\s", "", body))
    return len(body)


def read_blocks(project_dir: Path, blocks: int = 5) -> list[str | None]:
    out: list[str | None] = []
    for n in range(1, blocks + 1):
        p = project_dir / "06_script" / f"block-{n:02d}.txt"
        out.append(normalize_newlines(p.read_text(encoding="utf-8")) if p.exists() else None)
    return out


# ---------------------------------------------------------------------------
# Semelhança textual (superfície), usada para distinguir cópia de slot de mercado.
# ---------------------------------------------------------------------------

def tokens(text: str) -> list[str]:
    return re.findall(r"[a-zà-öø-ÿ0-9]+", (text or "").lower())


def stem(token: str) -> str:
    for suffix in ("ing", "ed", "es", "s"):
        if token.endswith(suffix) and len(token) - len(suffix) >= 3:
            return token[: -len(suffix)]
    return token


def genre_stems(genre_terms: list[str]) -> set[str]:
    return {stem(t.lower()) for t in genre_terms}


def content_tokens(text: str, genre: set[str]) -> set[str]:
    return {
        stem(t) for t in tokens(text)
        if t not in STOPWORDS and len(t) > 2 and stem(t) not in genre
    }


def overlap(a: str, b: str, genre: set[str]) -> dict:
    ta, tb = content_tokens(a, genre), content_tokens(b, genre)
    shared = ta & tb
    union = ta | tb
    smaller = min(len(ta), len(tb)) or 1
    return {
        "shared": sorted(shared),
        "jaccard": len(shared) / len(union) if union else 0.0,
        "containment": len(shared) / smaller,
    }


def event_match(a: str, b: str, genre: set[str], rules: dict) -> bool:
    o = overlap(a, b, genre)
    return (
        len(o["shared"]) >= rules.get("event_min_shared_tokens", 2)
        and o["containment"] >= rules.get("event_min_containment", 0.6)
        and o["jaccard"] >= rules.get("event_min_jaccard", 0.3)
    )


def word_seq_ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, tokens(a), tokens(b)).ratio()


def title_too_close(candidate: str, reference: str, genre: set[str], rules: dict) -> tuple[bool, str]:
    if not candidate or not reference:
        return False, ""
    if candidate.strip().lower() == reference.strip().lower():
        return True, "idêntico à referência"
    ratio = word_seq_ratio(candidate, reference)
    if ratio >= rules.get("title_seq_ratio_too_close", 0.6):
        return True, f"mesma estrutura de frase da referência (razão {ratio:.2f})"
    o = overlap(candidate, reference, genre)
    if len(o["shared"]) >= 2 and o["jaccard"] >= rules.get("title_content_jaccard_too_close", 0.6):
        return True, f"mesmas palavras de conteúdo da referência {o['shared']} (Jaccard {o['jaccard']:.2f})"
    return False, f"razão {ratio:.2f}, Jaccard de conteúdo {o['jaccard']:.2f}"


def contains_term(text: str, term: str) -> bool:
    return re.search(r"(?<![\w])" + re.escape(term) + r"(?![\w])", text or "", flags=re.IGNORECASE) is not None


def has_prefix_keyword(text: str, keywords: list[str]) -> bool:
    toks = tokens(text)
    return any(t.startswith(k.lower()) for k in keywords for t in toks)


def flatten_text(value) -> str:
    """Concatena todas as strings de uma estrutura YAML (para buscas por evidência)."""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return " ".join(flatten_text(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(flatten_text(v) for v in value)
    return ""


def longest_increasing_run(pairs: list[tuple[int, int]]) -> int:
    """Maior subsequência crescente em j para pares (i, j) já ordenados por i."""
    js = [j for _, j in sorted(pairs)]
    best: list[int] = []
    for j in js:
        lo, hi = 0, len(best)
        while lo < hi:
            mid = (lo + hi) // 2
            if best[mid] < j:
                lo = mid + 1
            else:
                hi = mid
        if lo == len(best):
            best.append(j)
        else:
            best[lo] = j
    return len(best)
