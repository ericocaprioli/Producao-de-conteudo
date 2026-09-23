#!/usr/bin/env python3
"""Narra o roteiro do Wingborn Content Factory com a sua voz (Chatterbox TTS).

Pensado para o Kaggle, mas funciona em qualquer máquina com GPU:
    python -u narrar.py            (lê config.json, se existir)

Entradas (procuradas sozinhas em /kaggle/input, /content e na pasta atual):
    - tts_plain_text.txt   exportado por /exportar-projeto (ou qualquer .txt único)
    - um áudio da sua voz  (.wav .mp3 .m4a .flac .ogg .opus .aac) — pode ser em português
    - opcional: voz_base.* — áudio de uma voz fluente em inglês com licença de uso

Modos:
    nativo    (padrão) 1) narra em inglês fluente com a voz base (padrão do Chatterbox ou voz_base.*)
              2) converte cada trecho para o SEU timbre (ChatterboxVC). Pronúncia nativa, voz sua.
    clonagem  narra direto imitando a sua gravação: herda também o sotaque dela.

Ritmo:
    velocidade  0.9 (padrão) deixa a fala 10% mais lenta que o modelo, sem mudar o tom da voz.
                Aplicada só na montagem final: mudá-la não gera nenhum trecho de novo.

Saídas na pasta atual:
    narracao_final.wav   narração completa, volume normalizado para o YouTube (-16 LUFS)
    narracao.srt         legenda com o tempo de cada trecho (serve para alinhar as cenas na edição)
    relatorio.txt        trechos, duração, take usada e trechos suspeitos
    takes/               cache: cada trecho é guardado pelo próprio conteúdo; rodar de novo só gera o que falta

Roda em processo separado do notebook de propósito: assim a instalação do Chatterbox não
exige "Restart session".
"""

import hashlib
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import time
import warnings
from pathlib import Path

# Silencia avisos e barras de progresso das bibliotecas (não afetam o áudio).
warnings.filterwarnings("ignore")
for _var, _val in (("TQDM_DISABLE", "1"), ("TRANSFORMERS_VERBOSITY", "error"), ("HF_HUB_VERBOSITY", "error"),
                   ("HF_HUB_DISABLE_PROGRESS_BARS", "1"), ("PYTHONWARNINGS", "ignore")):
    os.environ.setdefault(_var, _val)

DEFAULTS = {
    "modo": "nativo",          # "nativo" (sem sotaque) ou "clonagem" (imita a gravação, com sotaque)
    "voz_base": None,          # caminho de uma voz fluente em inglês (opcional; padrão = voz do Chatterbox)
    "exaggeration": 0.7,       # emoção: 0.5 neutro, 0.7+ dramático
    "cfg_weight": 0.3,         # menor = ritmo mais solto e menos sotaque copiado da referência
    "temperature": 0.8,
    "max_chars": 250,          # tamanho máximo de cada trecho
    "velocidade": 0.9,         # ritmo da fala: 1.0 = como o modelo gera, 0.9 = 10% mais lenta (o tom não muda)
    "pausa_frase": 0.25,       # silêncio entre trechos do mesmo parágrafo (s)
    "pausa_paragrafo": 0.7,    # silêncio no fim de cada parágrafo (s)
    "so_primeiros": None,      # teste rápido: gera só os N primeiros trechos
    "refazer_suspeitos": 2,    # tentativas extras para trechos com duração anormal (0 desliga)
    "usar_take": {},           # {"12": 2}: força a take 2 no trecho 12
    "ref_index": 0,            # qual áudio usar se houver vários
    "ref_inicio_seg": 0,       # de onde recortar a referência
    "ref_duracao_seg": 20,     # o modelo só aproveita os primeiros ~10 s; 20 s dão margem
    "roteiro": None,           # caminho manual do .txt (opcional)
    "referencia": None,        # caminho manual do áudio (opcional)
    "zip_takes": False,        # empacotar takes/ num .zip para download
}
SEARCH_DIRS = ["/kaggle/input", "/content", "."]
AUDIO_EXTS = (".wav", ".mp3", ".m4a", ".flac", ".ogg", ".opus", ".aac")
IGNORED_OUTPUTS = {"narracao_final.wav", "narracao_bruta.wav", "referencia.wav", "voz_base_preparada.wav"}
BASE_VOICE_STEM = "voz_base"
MODES = ("nativo", "clonagem")
SPEED_RANGE = (0.5, 2.0)   # limites do atempo em qualquer versão do ffmpeg
LOUDNORM = "loudnorm=I=-16:TP=-1.5:LRA=11"


class Erro(Exception):
    """Erro com mensagem pensada para o usuário do notebook."""


# ---------------------------------------------------------------------------
# Configuração e entradas
# ---------------------------------------------------------------------------

def load_config(path: Path = Path("config.json")) -> dict:
    cfg = dict(DEFAULTS)
    if path.exists():
        cfg.update(json.loads(path.read_text(encoding="utf-8")))
    cfg["usar_take"] = {int(k): int(v) for k, v in (cfg.get("usar_take") or {}).items()}
    return cfg


def check_speed(value) -> float:
    try:
        speed = float(value)
    except (TypeError, ValueError):
        speed = float("nan")
    if not SPEED_RANGE[0] <= speed <= SPEED_RANGE[1]:
        raise Erro(f"velocidade {value!r} inválida. Use um número com ponto entre {SPEED_RANGE[0]} e "
                   f"{SPEED_RANGE[1]}: 0.9 = 10% mais lenta, 1.0 = normal, 1.1 = 10% mais rápida.")
    return speed


def _walk(dirs: list[str]) -> list[Path]:
    files = []
    for d in dirs:
        p = Path(d)
        if p.is_dir():
            files += sorted(f for f in p.rglob("*") if f.is_file() and "takes" not in f.parts)
    return files


def find_inputs(cfg: dict, dirs: list[str] | None = None) -> tuple[Path, Path]:
    files = _walk(SEARCH_DIRS if dirs is None else dirs)

    if cfg.get("roteiro"):
        script = Path(cfg["roteiro"])
    else:
        named = [f for f in files if f.name == "tts_plain_text.txt"]
        txts = [f for f in files if f.suffix.lower() == ".txt" and f.name not in ("relatorio.txt",)]
        if named:
            script = named[0]
        elif len(txts) == 1:
            script = txts[0]
        else:
            raise Erro(
                "Não achei o roteiro. Adicione o tts_plain_text.txt (de 11_exports/) ao seu dataset, "
                f"ou informe ROTEIRO na célula de configuração. Arquivos .txt vistos: {[str(t) for t in txts]}"
            )

    if cfg.get("referencia"):
        ref = Path(cfg["referencia"])
    else:
        audios = [f for f in files if f.suffix.lower() in AUDIO_EXTS and f.name not in IGNORED_OUTPUTS
                  and f.stem.lower() != BASE_VOICE_STEM]
        if not audios:
            raise Erro("Não achei o áudio da sua voz. Adicione-o ao dataset (Add Input) ou informe REFERENCIA.")
        idx = cfg.get("ref_index", 0)
        if idx >= len(audios):
            raise Erro(f"REF_INDEX = {idx}, mas só há {len(audios)} áudio(s): {[str(a) for a in audios]}")
        if len(audios) > 1:
            print("Áudios encontrados (use REF_INDEX para escolher):")
            for i, a in enumerate(audios):
                print(f"  [{i}] {a}")
        ref = audios[idx]

    for p, nome in ((script, "roteiro"), (ref, "referência")):
        if not p.exists():
            raise Erro(f"O arquivo de {nome} não existe: {p}")
    return script, ref


def find_base_voice(cfg: dict, dirs: list[str] | None = None) -> Path | None:
    """Voz fluente usada no modo nativo. None = voz padrão embutida no Chatterbox."""
    if cfg.get("voz_base"):
        p = Path(cfg["voz_base"])
        if not p.exists():
            raise Erro(f"voz_base não existe: {p}")
        return p
    found = [f for f in _walk(SEARCH_DIRS if dirs is None else dirs) if f.stem.lower() == BASE_VOICE_STEM and f.suffix.lower() in AUDIO_EXTS
             and f.name not in IGNORED_OUTPUTS]
    return found[0] if found else None


# ---------------------------------------------------------------------------
# Texto
# ---------------------------------------------------------------------------

def split_long(sentence: str, max_chars: int) -> list[str]:
    """Quebra uma frase longa em pontos naturais (vírgula, ponto e vírgula, travessão), depois em espaços."""
    if len(sentence) <= max_chars:
        return [sentence]
    pieces = re.split(r"(?<=[,;:—–])\s+", sentence)
    out, cur = [], ""
    for piece in pieces:
        if len(piece) > max_chars:
            if cur:
                out.append(cur)
                cur = ""
            words, line = piece.split(), ""
            for w in words:
                if line and len(line) + 1 + len(w) > max_chars:
                    out.append(line)
                    line = w
                else:
                    line = f"{line} {w}".strip()
            cur = line
        elif cur and len(cur) + 1 + len(piece) > max_chars:
            out.append(cur)
            cur = piece
        else:
            cur = f"{cur} {piece}".strip()
    if cur:
        out.append(cur)
    return out


def split_script(text: str, max_chars: int, pausa_frase: float, pausa_paragrafo: float) -> list[tuple[str, float]]:
    """Divide em (trecho, pausa_depois). Linha em branco separa parágrafos."""
    paragraphs = [" ".join(p.split()) for p in re.split(r"\n\s*\n", text.replace("\r\n", "\n")) if p.strip()]
    chunks: list[tuple[str, float]] = []
    for p in paragraphs:
        sentences = []
        for s in re.split(r"(?<=[.!?…])\s+", p):
            sentences += split_long(s, max_chars)
        cur, start = "", len(chunks)
        for s in sentences:
            if cur and len(cur) + 1 + len(s) > max_chars:
                chunks.append((cur, pausa_frase))
                cur = s
            else:
                cur = f"{cur} {s}".strip()
        if cur:
            chunks.append((cur, pausa_frase))
        if len(chunks) > start:
            chunks[-1] = (chunks[-1][0], pausa_paragrafo)
    return chunks


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def file_hash(path: Path) -> str:
    return hashlib.md5(Path(path).read_bytes()).hexdigest()


def chunk_key(text: str, cfg: dict, ref_hash: str, base_hash: str = "") -> str:
    """Identidade de um trecho: muda se o texto, as vozes, o modo ou os ajustes de geração mudarem.

    A velocidade fica de fora: é aplicada só na montagem final, então mudá-la reaproveita todas as takes.
    """
    params = (text, ref_hash, cfg["exaggeration"], cfg["cfg_weight"], cfg["temperature"],
              cfg.get("modo", "nativo"), base_hash)
    return hashlib.md5(repr(params).encode("utf-8")).hexdigest()[:16]


def srt_time(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build_srt(entries: list[tuple[float, float, str]]) -> str:
    return "\n".join(
        f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{text}\n" for i, (a, b, text) in enumerate(entries, 1)
    )


def trim_silence(audio, sr: int, threshold_db: float = -45.0, margin_s: float = 0.05):
    """Remove silêncio no começo e no fim do trecho, para as pausas ficarem uniformes."""
    import numpy as np

    if audio.size == 0:
        return audio
    peak = float(np.max(np.abs(audio))) or 1.0
    loud = np.where(np.abs(audio) > peak * 10 ** (threshold_db / 20))[0]
    if loud.size == 0:
        return audio
    margin = int(sr * margin_s)
    return audio[max(0, loud[0] - margin): min(len(audio), loud[-1] + 1 + margin)]


def suspicious(durations: dict[int, float], texts: dict[int, str], low: float = 0.6, high: float = 1.6) -> list[int]:
    """Trechos cuja duração foge muito da velocidade típica desta narração (corte ou alucinação)."""
    rates = [len(texts[i]) / d for i, d in durations.items() if d > 0]
    if len(rates) < 3:
        return []
    cps = statistics.median(rates)
    out = []
    for i, d in durations.items():
        expected = len(texts[i]) / cps
        if d <= 0 or d > expected * high or d < expected * low:
            out.append(i)
    return out


def prepare_reference(src: Path, inicio: float, duracao: float, out: Path = Path("referencia.wav")) -> Path:
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-ss", str(inicio), "-t", str(duracao),
           "-i", str(src), "-ac", "1", str(out)]
    subprocess.run(cmd, check=True)
    return out


def audio_filter(velocidade: float) -> str:
    """atempo muda o ritmo sem mudar o tom; loudnorm vem depois, sobre o áudio já no ritmo final."""
    return LOUDNORM if velocidade == 1.0 else f"atempo={velocidade:g},{LOUDNORM}"


def normalize(src: Path, dst: Path, sr: int, velocidade: float = 1.0) -> None:
    """Ritmo final e volume no padrão do YouTube (~ -16 LUFS), mantendo a taxa de amostragem."""
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
                    "-af", audio_filter(velocidade), "-ar", str(sr), str(dst)], check=True)


# ---------------------------------------------------------------------------
# Geração
# ---------------------------------------------------------------------------

def load_model(kind: str = "tts"):
    try:
        import torch
        if kind == "vc":
            from chatterbox.vc import ChatterboxVC as Model
        else:
            from chatterbox.tts import ChatterboxTTS as Model
    except Exception as e:  # noqa: BLE001 - mensagem amigável para qualquer falha de import
        raise Erro(
            "O Chatterbox não carregou. Rode de novo a célula 1 (instalação) e depois esta. "
            f"Erro original: {e!r}"
        ) from e
    if not torch.cuda.is_available():
        raise Erro("GPU desligada. No Kaggle: Settings → Accelerator → GPU T4 x2 (ou P100) e rode tudo de novo.")
    return Model.from_pretrained(device="cuda")


def main() -> int:
    import numpy as np
    import soundfile as sf

    cfg = load_config()
    if cfg["modo"] not in MODES:
        raise Erro(f"modo '{cfg['modo']}' inválido. Use {MODES}.")
    native = cfg["modo"] == "nativo"
    speed = check_speed(cfg["velocidade"])
    script_path, ref_src = find_inputs(cfg)
    base_src = find_base_voice(cfg) if native else None
    print(f"Roteiro:    {script_path}")
    print(f"Sua voz:    {ref_src}")
    if native:
        print(f"Modo nativo: inglês fluente com {base_src or 'a voz padrão do Chatterbox'}, convertido para a sua voz.")
    else:
        print("Modo clonagem: imita a sua gravação (inclusive o sotaque).")
    print(f"Velocidade: {speed:g} (1.0 = ritmo do modelo)")

    text = script_path.read_text(encoding="utf-8")
    chunks = split_script(text, cfg["max_chars"], cfg["pausa_frase"], cfg["pausa_paragrafo"])
    if cfg.get("so_primeiros"):
        chunks = chunks[: int(cfg["so_primeiros"])]
        print(f"MODO TESTE: só os {len(chunks)} primeiros trechos.")
    if not chunks:
        raise Erro("O roteiro está vazio.")

    ref = prepare_reference(ref_src, cfg["ref_inicio_seg"], cfg["ref_duracao_seg"])
    ref_hash = file_hash(ref)
    base = prepare_reference(base_src, 0, cfg["ref_duracao_seg"], Path("voz_base_preparada.wav")) if base_src else None
    base_hash = file_hash(base) if base else ("padrao" if native else "")
    texts = {i: t for i, (t, _) in enumerate(chunks, 1)}
    keys = {i: chunk_key(t, cfg, ref_hash, base_hash) for i, t in texts.items()}

    takes = Path("takes")
    takes.mkdir(exist_ok=True)

    def path(i: int, t: int) -> Path:
        return takes / f"{keys[i]}_take{t}.wav"

    missing = [i for i in texts if not path(i, 1).exists()]
    print(f"{len(chunks)} trechos; {len(chunks) - len(missing)} já prontos no cache, {len(missing)} para gerar.")

    models: dict = {}
    sr = 24000

    def model(kind: str):
        if kind not in models:
            print("Carregando o modelo de " + ("conversão de voz" if kind == "vc" else "narração") + " na GPU...")
            models[kind] = load_model(kind)
        return models[kind]

    def save(wav, f: Path, rate: int) -> None:
        audio = wav.squeeze(0).detach().cpu().numpy().astype("float32")
        sf.write(str(f), trim_silence(audio, rate), rate)

    def generate(i: int, t: int) -> None:
        f = path(i, t)
        if f.exists():
            return
        tts = model("tts")
        prompt = str(base if native else ref) if (base or not native) else None
        wav = tts.generate(texts[i], audio_prompt_path=prompt, exaggeration=cfg["exaggeration"],
                           cfg_weight=cfg["cfg_weight"], temperature=cfg["temperature"])
        if not native:
            save(wav, f, tts.sr)
            return
        base_take = f.with_name(f.stem + "_base.wav")
        save(wav, base_take, tts.sr)
        vc = model("vc")
        try:
            converted = vc.generate(str(base_take), target_voice_path=str(ref))
        except TypeError as e:
            raise Erro(f"A versão instalada do Chatterbox mudou a conversão de voz. Use modo 'clonagem'. ({e})") from e
        save(converted, f, vc.sr)

    t0, done_chars = None, 0
    remaining_chars = sum(len(texts[i]) for i in missing)
    for n, i in enumerate(missing, 1):
        generate(i, 1)
        if t0 is None:  # o 1º trecho inclui o carregamento dos modelos: não entra na estimativa
            t0 = time.time()
            remaining_chars -= len(texts[i])
            print(f"trecho {i}/{len(chunks)} pronto (modelos carregados)", flush=True)
            continue
        done_chars += len(texts[i])
        rest = (time.time() - t0) / done_chars * (remaining_chars - done_chars)
        print(f"trecho {i}/{len(chunks)} pronto — faltam ~{max(rest, 0) / 60:.0f} min", flush=True)

    def duration(i: int, t: int) -> float:
        info = sf.info(str(path(i, t)))
        return info.frames / info.samplerate

    chosen = {i: 1 for i in texts}
    bad = suspicious({i: duration(i, 1) for i in texts}, texts)
    retries = int(cfg.get("refazer_suspeitos") or 0)
    if bad and retries:
        print(f"{len(bad)} trecho(s) com duração anormal: {bad}. Gerando até {retries} tentativa(s) extra(s)...")
        rates = [len(texts[i]) / duration(i, 1) for i in texts if i not in bad]
        cps = statistics.median(rates) if rates else 15.0
        for i in bad:
            for t in range(2, 2 + retries):
                generate(i, t)
            candidates = [t for t in range(1, 2 + retries) if path(i, t).exists()]
            expected = len(texts[i]) / cps
            chosen[i] = min(candidates, key=lambda t: abs(duration(i, t) - expected))

    for i, t in cfg["usar_take"].items():
        if i in texts:
            generate(i, t)
            chosen[i] = t

    parts, entries, cursor = [], [], 0.0
    for i, (_, pause) in enumerate(chunks, 1):
        audio, file_sr = sf.read(str(path(i, chosen[i])), dtype="float32")
        sr = file_sr
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        start = cursor
        cursor += len(audio) / sr
        entries.append((start, cursor, texts[i]))
        parts += [audio, np.zeros(int(sr * pause), dtype="float32")]
        cursor += pause
    sf.write("narracao_bruta.wav", np.concatenate(parts), sr)
    normalize(Path("narracao_bruta.wav"), Path("narracao_final.wav"), sr, speed)
    # O atempo estica o áudio inteiro por igual, pausas incluídas: a legenda acompanha na mesma proporção.
    entries = [(a / speed, b / speed, t) for a, b, t in entries]
    total = cursor / speed
    Path("narracao.srt").write_text(build_srt(entries), encoding="utf-8")

    still_bad = suspicious({i: duration(i, chosen[i]) for i in texts}, texts)
    chars = sum(len(t) for t in texts.values())
    lines = [f"Roteiro: {script_path}", f"Referência: {ref_src}",
             f"Duração: {total / 60:.1f} min | velocidade {speed:g} | {chars / total:.1f} caracteres por segundo", ""]
    if still_bad:
        lines.append(f"OUÇA ESTES TRECHOS (duração ainda anormal): {still_bad}")
        lines.append("Se algum estiver ruim: coloque USAR_TAKE = {número: 2} e rode de novo (só ele é regerado).")
        lines.append("")
    for (a, b, t), i in zip(entries, texts):
        flag = "  <-- ouvir" if i in still_bad else ""
        lines.append(f"[{i:03d}] {srt_time(a)}  take {chosen[i]}  {b - a:5.1f}s  {t[:70]}{flag}")
    Path("relatorio.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    Path("relatorio.json").write_text(json.dumps(
        {"suspeitos": still_bad, "takes": {str(i): str(path(i, chosen[i])) for i in texts},
         "textos": {str(i): texts[i] for i in texts}}, ensure_ascii=False, indent=1), encoding="utf-8")
    Path("narracao_bruta.wav").unlink()

    if cfg.get("zip_takes"):
        shutil.make_archive("takes", "zip", "takes")

    print()
    print("=" * 64)
    print(f"PRONTO: narracao_final.wav ({total / 60:.1f} min, velocidade {speed:g}), narracao.srt e relatorio.txt")
    if still_bad:
        print(f"Trechos para ouvir antes de publicar: {still_bad} (veja relatorio.txt ou a célula 4)")
    else:
        print("Nenhum trecho com duração anormal.")
    print("=" * 64)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Erro as e:
        print(f"\nERRO: {e}")
        sys.exit(1)
