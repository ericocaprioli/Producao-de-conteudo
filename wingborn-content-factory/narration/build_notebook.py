#!/usr/bin/env python3
"""Gera narration/kaggle_narracao.ipynb a partir de narration/narrar.py.

Uso: python3 narration/build_notebook.py
Rode sempre que alterar narrar.py (o teste tests/test_narration.py confere se estão em sincronia).
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "kaggle_narracao.ipynb"

INTRO = """# Narração Wingborn — sua voz com Chatterbox

**Antes de começar (uma vez por vídeo):**
1. No Kaggle, crie um *dataset* com 2 arquivos: o `tts_plain_text.txt` (pasta `11_exports/` do projeto) e um áudio da sua voz (15–30 s, voz limpa, sem música).
2. Neste notebook: **Add Input** → escolha esse dataset.
3. **Settings → Accelerator → GPU** e **Settings → Internet → On** (a internet exige telefone verificado na conta Kaggle).

**Para gerar:** clique em **Run All**. Não é preciso reiniciar a sessão em nenhum momento.

- Teste rápido primeiro? Na célula 3, coloque `"so_primeiros": 3`.
- Não quer ficar com a aba aberta? Use **Save Version → Save & Run All (Commit)**. O Kaggle roda sozinho e os arquivos ficam guardados na aba **Output** da versão, sem prazo para baixar.

**Resultado (aba Output → Download):** `narracao_final.wav`, `narracao.srt` (legenda com o tempo de cada trecho, útil para posicionar as cenas) e `relatorio.txt` (lista os trechos que merecem ser ouvidos).
"""

INSTALL = '''# 1) Instalação (10–15 min na primeira vez). Avisos vermelhos de "dependency conflicts" são normais.
import subprocess, sys

def ok(code):
    return subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)

if ok("import chatterbox, numpy.random").returncode == 0:
    print("Chatterbox já instalado nesta sessão.")
else:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "chatterbox-tts"])
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "-q", "torchvision"])
    # O pip costuma deixar o numpy com arquivos misturados no Kaggle: reinstala e confere em outro processo.
    for tentativa in range(1, 4):
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "-q", "numpy"])
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--force-reinstall", "--no-deps", "numpy==1.26.4"])
        r = ok("import numpy, numpy.random, chatterbox; print(numpy.__version__)")
        if r.returncode == 0:
            break
        print(f"tentativa {tentativa}: ainda com problema:", r.stderr[-300:])
    else:
        raise RuntimeError("A instalação falhou 3 vezes. Clique no botão de power (encerrar sessão), ligue de novo e rode tudo.")
    print("Instalado. Pode seguir — NÃO precisa reiniciar a sessão.")
'''

CONFIG = '''# 3) Ajustes (opcional). Os valores abaixo já funcionam; mude só se precisar.
import json

config = {
    "exaggeration": 0.7,        # emoção: 0.5 neutro, 0.7+ dramático (alto demais distorce)
    "cfg_weight": 0.3,          # menor = ritmo mais solto e menos sotaque copiado da referência
    "temperature": 0.8,
    "so_primeiros": None,       # TESTE RÁPIDO: coloque 3 para gerar só os 3 primeiros trechos
    "usar_take": {},            # depois de ouvir, ex.: {12: 2} usa a take 2 no trecho 12
    "refazer_suspeitos": 2,     # tentativas extras automáticas para trechos com duração estranha
    "ref_index": 0,             # se o dataset tiver vários áudios, qual usar (0 = primeiro)
    "ref_inicio_seg": 0,        # pule um início com silêncio ou ruído na sua gravação
    "roteiro": None,            # caminho manual do .txt, se a detecção automática falhar
    "referencia": None,         # caminho manual do áudio, se a detecção automática falhar
    "zip_takes": False,         # True para baixar todas as takes num .zip
}
json.dump(config, open("config.json", "w"), indent=1)
print("Ajustes salvos.")
'''

RUN = '''# 4) Gerar a narração. Pode rodar de novo à vontade: só o que mudou é gerado outra vez.
!python -u narrar.py
'''

LISTEN = '''# 5) (Opcional) Ouvir os trechos marcados como suspeitos no relatório.
#    Se um estiver ruim: na célula 3 coloque "usar_take": {número: 2} e rode as células 3 e 4 de novo.
import json, glob
from IPython.display import Audio, Markdown, display

MOSTRAR_TODOS = False   # True para listar todos os trechos

r = json.load(open("relatorio.json"))
alvo = list(r["textos"]) if MOSTRAR_TODOS else [str(i) for i in r["suspeitos"]]
if not alvo:
    print("Nenhum trecho suspeito. Se quiser conferir tudo, use MOSTRAR_TODOS = True.")
for i in alvo:
    display(Markdown(f"**Trecho {i}:** {r['textos'][i]}"))
    base = r["takes"][i].rsplit("_take", 1)[0]
    for f in sorted(glob.glob(base + "_take*.wav")):
        print(f.rsplit("_", 1)[1][:-4], "(em uso)" if f == r["takes"][i] else "")
        display(Audio(f))
'''


def cell(kind: str, source: str) -> dict:
    lines = source.splitlines(keepends=True)
    c = {"cell_type": kind, "metadata": {}, "source": lines}
    if kind == "code":
        c.update(execution_count=None, outputs=[])
    return c


def build() -> dict:
    code = (HERE / "narrar.py").read_text(encoding="utf-8")
    cells = [
        cell("markdown", INTRO),
        cell("code", INSTALL),
        cell("code", "%%writefile narrar.py\n# 2) Código da narração. Não precisa mexer aqui.\n" + code),
        cell("code", CONFIG),
        cell("code", RUN),
        cell("code", LISTEN),
    ]
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
            "kaggle": {"accelerator": "gpu", "isInternetEnabled": True},
        },
        "nbformat": 4,
        "nbformat_minor": 4,
    }


if __name__ == "__main__":
    NOTEBOOK.write_text(json.dumps(build(), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"OK: {NOTEBOOK}")
