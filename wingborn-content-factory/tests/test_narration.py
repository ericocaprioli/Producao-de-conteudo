"""Testes do narrador (narration/narrar.py) sem GPU: o modelo e o ffmpeg são substituídos por falsos."""

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "narration"))
import narrar  # noqa: E402

try:
    import numpy as np
    import soundfile as sf
except ImportError:  # pragma: no cover
    np = sf = None

SCRIPT = (ROOT / "tests" / "fixtures" / "adjacent-trend-mother-dragons" / "06_script")


class TestSplit(unittest.TestCase):
    def test_chunks_respect_max_and_keep_all_words(self):
        text = "\n\n".join((SCRIPT / f"block-{n:02d}.txt").read_text() for n in range(1, 6))
        chunks = narrar.split_script(text, 250, 0.25, 0.7)
        self.assertTrue(all(len(c) <= 250 for c, _ in chunks))
        self.assertEqual(" ".join(c for c, _ in chunks).split(), text.split())

    def test_paragraph_end_gets_long_pause(self):
        chunks = narrar.split_script("One. Two.\n\nThree.", 250, 0.25, 0.7)
        self.assertEqual(chunks, [("One. Two.", 0.7), ("Three.", 0.7)])

    def test_single_newline_does_not_split_paragraph(self):
        self.assertEqual(len(narrar.split_script("Line one\nline two.", 250, 0.25, 0.7)), 1)

    def test_long_sentence_split_at_commas_then_words(self):
        sentence = ", ".join(["a clause with several words in it"] * 12) + "."
        parts = narrar.split_long(sentence, 100)
        self.assertTrue(all(len(p) <= 100 for p in parts))
        self.assertEqual(" ".join(parts).split(), sentence.split())
        no_commas = " ".join(["word"] * 80)
        self.assertTrue(all(len(p) <= 50 for p in narrar.split_long(no_commas, 50)))


class TestHelpers(unittest.TestCase):
    def test_srt(self):
        self.assertEqual(narrar.srt_time(3723.456), "01:02:03,456")
        srt = narrar.build_srt([(0, 1.5, "Hello."), (2, 3, "World.")])
        self.assertIn("1\n00:00:00,000 --> 00:00:01,500\nHello.", srt)
        self.assertIn("2\n00:00:02,000 --> 00:00:03,000\nWorld.", srt)

    def test_chunk_key_changes_with_text_voice_and_params(self):
        cfg = dict(narrar.DEFAULTS)
        base = narrar.chunk_key("text", cfg, "voiceA")
        self.assertEqual(base, narrar.chunk_key("text", cfg, "voiceA"))
        self.assertNotEqual(base, narrar.chunk_key("text!", cfg, "voiceA"))
        self.assertNotEqual(base, narrar.chunk_key("text", cfg, "voiceB"))
        self.assertNotEqual(base, narrar.chunk_key("text", {**cfg, "exaggeration": 0.5}, "voiceA"))

    def test_suspicious_durations(self):
        texts = {i: "x" * 150 for i in range(1, 7)}
        durations = {i: 10.0 for i in texts}
        durations[3] = 40.0   # alucinação
        durations[5] = 2.0    # corte
        self.assertEqual(narrar.suspicious(durations, texts), [3, 5])

    def test_config_merges_and_casts_take_keys(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "config.json"
            p.write_text(json.dumps({"exaggeration": 0.5, "usar_take": {"12": 2}}))
            cfg = narrar.load_config(p)
        self.assertEqual(cfg["exaggeration"], 0.5)
        self.assertEqual(cfg["usar_take"], {12: 2})
        self.assertEqual(cfg["max_chars"], 250)

    def test_find_inputs(self):
        with tempfile.TemporaryDirectory() as d:
            ds = Path(d) / "dataset"
            ds.mkdir()
            (ds / "tts_plain_text.txt").write_text("Hi.")
            (ds / "notes.txt").write_text("x")
            (ds / "voz.M4A").write_bytes(b"0")
            script, ref = narrar.find_inputs(dict(narrar.DEFAULTS), [d])
            self.assertEqual((script.name, ref.name), ("tts_plain_text.txt", "voz.M4A"))
            (ds / "voz.M4A").unlink()
            with self.assertRaises(narrar.Erro):
                narrar.find_inputs(dict(narrar.DEFAULTS), [d])

    @unittest.skipIf(np is None, "numpy ausente")
    def test_trim_silence(self):
        sr = 1000
        audio = np.concatenate([np.zeros(500), np.ones(300) * 0.5, np.zeros(700)]).astype("float32")
        trimmed = narrar.trim_silence(audio, sr, margin_s=0.01)
        self.assertEqual(len(trimmed), 300 + 2 * 10)


class FakeTensor:
    def __init__(self, arr):
        self.arr = arr

    def squeeze(self, _):
        return self

    def detach(self):
        return self

    def cpu(self):
        return self

    def numpy(self):
        return self.arr


class FakeModel:
    sr = 1000

    def __init__(self):
        self.calls = []

    def generate(self, text, **kwargs):
        self.calls.append(text)
        seconds = len(text) / 15
        if "HALLUCINATE" in text and self.calls.count(text) == 1:
            seconds *= 4  # primeira take ruim, segunda boa
        return FakeTensor(np.ones(int(self.sr * seconds), dtype="float32") * 0.3)


@unittest.skipIf(np is None, "numpy/soundfile ausentes")
class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.cwd = os.getcwd()
        os.chdir(self.dir)
        self.model = FakeModel()
        self._orig = (narrar.load_model, narrar.prepare_reference, narrar.normalize, narrar.SEARCH_DIRS)
        narrar.load_model = lambda: self.model
        narrar.prepare_reference = lambda src, a, b, out=Path("referencia.wav"): shutil.copy(src, out) and out
        narrar.normalize = lambda src, dst, sr: shutil.copy(src, dst)
        ds = self.dir / "input"
        ds.mkdir()
        paragraphs = [f"Paragraph {n} is calm and slow, told for quiet nights." for n in range(1, 7)]
        paragraphs[3] = "This line will HALLUCINATE on the first try, then settle down."
        (ds / "tts_plain_text.txt").write_text("\n\n".join(paragraphs))
        sf.write(str(ds / "voz.wav"), np.zeros(1000, dtype="float32"), 1000)
        narrar.SEARCH_DIRS = [str(ds)]

    def tearDown(self):
        narrar.load_model, narrar.prepare_reference, narrar.normalize, narrar.SEARCH_DIRS = self._orig
        os.chdir(self.cwd)
        self._tmp.cleanup()

    def test_full_run_retries_bad_chunk_and_caches(self):
        self.assertEqual(narrar.main(), 0)
        for name in ("narracao_final.wav", "narracao.srt", "relatorio.txt", "relatorio.json"):
            self.assertTrue(Path(name).exists(), name)
        report = json.loads(Path("relatorio.json").read_text())
        self.assertEqual(report["suspeitos"], [])
        self.assertTrue(report["takes"]["4"].endswith("_take2.wav"), report["takes"]["4"])
        self.assertEqual(Path("narracao.srt").read_text().count("-->"), 6)

        calls = len(self.model.calls)
        self.assertEqual(narrar.main(), 0)
        self.assertEqual(len(self.model.calls), calls, "segunda execução deveria usar só o cache")

        text = Path("input/tts_plain_text.txt")
        text.write_text(text.read_text().replace("Paragraph 6", "Paragraph six"))
        narrar.main()
        self.assertEqual(len(self.model.calls), calls + 1, "só o trecho alterado deveria ser regerado")


class TestNotebook(unittest.TestCase):
    def test_notebook_is_in_sync_with_narrar(self):
        import build_notebook
        committed = json.loads((ROOT / "narration" / "kaggle_narracao.ipynb").read_text(encoding="utf-8"))
        self.assertEqual(committed, json.loads(json.dumps(build_notebook.build())),
                         "rode: python3 narration/build_notebook.py")

    def test_notebook_has_no_restart_step(self):
        source = (ROOT / "narration" / "kaggle_narracao.ipynb").read_text(encoding="utf-8")
        self.assertNotIn("Restart session e continue", source)
        self.assertIn("!python -u narrar.py", source)


if __name__ == "__main__":
    unittest.main()
