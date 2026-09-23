"""Testes dos validadores do Wingborn Content Factory.

Rodar a partir da raiz de wingborn-content-factory/:
    python3 -m unittest discover -s tests -v
"""

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
FIXTURE = ROOT / "tests" / "fixtures" / "adjacent-trend-mother-dragons"
NEGATIVE_CASES = ROOT / "tests" / "fixtures" / "trend-negative-cases.yaml"
EMPTY_EXAMPLE = ROOT / "projects" / "2026-09-23-exemplo-vazio"

sys.path.insert(0, str(SCRIPTS))
from wb_common import count_units  # noqa: E402

REFERENCE_TITLE = "Her mother left her to die at the hands of the dragons — but she was the heir of Tiamat"


def run(script: str, *args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *map(str, args)],
        capture_output=True, text=True, cwd=ROOT,
    )


def classifications(output: str) -> dict[str, str]:
    ids = re.findall(r"== Direção (\S+)", output)
    verdicts = re.findall(r"CLASSIFICAÇÃO: (\w+)", output)
    return dict(zip(ids, verdicts))


class FixtureCopy(unittest.TestCase):
    """Cada teste que altera arquivos trabalha numa cópia do fixture."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.project = Path(self._tmp.name) / "project"
        shutil.copytree(FIXTURE, self.project)

    def tearDown(self):
        self._tmp.cleanup()

    def edit_yaml(self, relpath: str, mutate) -> None:
        path = self.project / relpath
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        mutate(data)
        path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")

    def replace_in(self, relpath: str, old: str, new: str, count: int = 1) -> None:
        path = self.project / relpath
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text, f"trecho não encontrado em {relpath}: {old!r}")
        path.write_text(text.replace(old, new, count), encoding="utf-8")


# ---------------------------------------------------------------------------
class TestCounting(unittest.TestCase):
    def test_trailing_newline_and_edges_not_counted(self):
        self.assertEqual(count_units("abc\n"), 3)
        self.assertEqual(count_units("  abc  \n\n"), 3)

    def test_internal_line_breaks_and_spaces_count(self):
        self.assertEqual(count_units("a b\nc"), 5)

    def test_crlf_counts_as_one_break(self):
        self.assertEqual(count_units("a\r\nb"), count_units("a\nb"))

    def test_words_and_no_spaces_units(self):
        self.assertEqual(count_units("one two  three", unit="words"), 3)
        self.assertEqual(count_units("a b c", count_spaces=False), 3)


class TestBlocks(FixtureCopy):
    def test_fixture_five_blocks_within_range(self):
        result = run("validate_blocks.py", FIXTURE)
        self.assertEqual(result.returncode, 0, result.stdout)
        for n in range(1, 6):
            text = (FIXTURE / "06_script" / f"block-{n:02d}.txt").read_text(encoding="utf-8")
            self.assertTrue(3200 <= count_units(text) <= 3500, f"bloco {n}: {count_units(text)}")

    def test_short_block_detected(self):
        path = self.project / "06_script" / "block-03.txt"
        path.write_text(path.read_text(encoding="utf-8")[:2000], encoding="utf-8")
        result = run("validate_blocks.py", self.project)
        self.assertEqual(result.returncode, 1)
        self.assertIn("block-03.txt", result.stdout)
        self.assertIn("fora da faixa", result.stdout)

    def test_long_block_detected(self):
        path = self.project / "06_script" / "block-02.txt"
        path.write_text(path.read_text(encoding="utf-8") * 2, encoding="utf-8")
        self.assertEqual(run("validate_blocks.py", self.project, "--block", 2).returncode, 1)

    def test_production_markers_detected(self):
        for marker in ("[PAUSE]", "[CENA 3]", "BLOCO 2: ", "# Block title\n"):
            with self.subTest(marker=marker):
                path = self.project / "06_script" / "block-04.txt"
                original = path.read_text(encoding="utf-8")
                path.write_text(marker + original[: 3300 - len(marker)], encoding="utf-8")
                result = run("validate_blocks.py", self.project, "--block", 4)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn("marcador técnico", result.stdout)
                path.write_text(original, encoding="utf-8")

    def test_missing_and_out_of_sequence_blocks_detected(self):
        (self.project / "06_script" / "block-05.txt").unlink()
        (self.project / "06_script" / "block-06.txt").write_text("extra", encoding="utf-8")
        result = run("validate_blocks.py", self.project)
        self.assertEqual(result.returncode, 1)
        self.assertIn("não encontrado", result.stdout)
        self.assertIn("block-06.txt", result.stdout)

    def test_non_utf8_detected(self):
        (self.project / "06_script" / "block-01.txt").write_bytes("Ailis caf\xe9".encode("latin-1"))
        result = run("validate_blocks.py", self.project, "--block", 1)
        self.assertEqual(result.returncode, 1)
        self.assertIn("UTF-8", result.stdout)


class TestConsistency(FixtureCopy):
    def test_fixture_is_consistent(self):
        result = run("validate_consistency.py", FIXTURE)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn("ERRO", result.stdout)

    def test_altered_name_detected(self):
        self.replace_in("06_script/block-03.txt", "Out in the Reach, Ailis", "Out in the Reach, Ailish")
        result = run("validate_consistency.py", self.project)
        self.assertEqual(result.returncode, 1)
        self.assertIn("possivelmente alterado", result.stdout)
        self.assertIn("Ailish", result.stdout)

    def test_missing_name_detected(self):
        self.edit_yaml("05_character_bible/character-bible.yaml", lambda b: b["ally"].update(name="Brannoc"))
        result = run("validate_consistency.py", self.project)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Brannoc", result.stdout)

    def test_partial_script_does_not_flag_unwritten_blocks(self):
        for n in range(2, 6):
            (self.project / "06_script" / f"block-{n:02d}.txt").unlink()
        result = run("validate_consistency.py", self.project)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("INFO: ally ('Tamsin') ainda não apareceu", result.stdout)
        self.assertNotIn("desaparece", result.stdout)

    def test_age_in_words_contradiction_detected(self):
        self.replace_in("06_script/block-01.txt", "Ailis was nine years old.", "Ailis was twelve years old.")
        result = run("validate_consistency.py", self.project)
        self.assertEqual(result.returncode, 1)
        self.assertIn("idade", result.stdout)
        self.assertIn("12", result.stdout)

    def test_age_in_digits_contradiction_detected(self):
        self.replace_in("06_script/block-01.txt", "Ailis was nine years old.", "Ailis was a 19-year-old girl.")
        result = run("validate_consistency.py", self.project)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("19", result.stdout)

    def test_other_character_age_not_attributed_to_protagonist(self):
        self.replace_in("06_script/block-02.txt", "The woman's name was Tamsin.",
                        "The woman's name was Tamsin, and she was seventy years old.")
        self.assertEqual(run("validate_consistency.py", self.project).returncode, 0)

    def test_symbol_object_never_mentioned_detected(self):
        self.edit_yaml("05_character_bible/character-bible.yaml",
                       lambda b: b["story"].update(symbol_object="silver thimble"))
        result = run("validate_consistency.py", self.project)
        self.assertEqual(result.returncode, 1)
        self.assertIn("silver thimble", result.stdout)

    def test_dragon_scale_color_contradiction_warned(self):
        self.replace_in("06_script/block-04.txt", "Her ash-grey scales ran with river mist.",
                        "Her golden scales ran with river mist.")
        result = run("validate_consistency.py", self.project)
        self.assertIn("AVISO: dragão", result.stdout)

    def test_opening_without_antagonist_detected(self):
        # O magistrado só aparece no bloco 4: não identifica o responsável nos primeiros ~30 s.
        self.edit_yaml("05_character_bible/character-bible.yaml",
                       lambda b: b["antagonist"].update(name="Tamsin", relation="magistrate"))
        result = run("validate_consistency.py", self.project)
        self.assertEqual(result.returncode, 1)
        self.assertIn("bloco 1: antagonista", result.stdout)


class TestProject(FixtureCopy):
    def test_fixture_and_empty_example_valid(self):
        for path in (FIXTURE, EMPTY_EXAMPLE):
            with self.subTest(path=path.name):
                result = run("validate_project.py", path)
                self.assertEqual(result.returncode, 0, result.stdout)

    def test_resume_reports_next_command(self):
        self.assertIn("próximo comando: /revisar-retencao", run("validate_project.py", FIXTURE).stdout)
        self.assertIn("próximo comando: /triar-referencia", run("validate_project.py", EMPTY_EXAMPLE).stdout)

    def test_resume_reports_pending_blocks(self):
        def mutate(p):
            p.update(status="writing_in_progress", approved_blocks=[1, 2])
            p["approved_gates"].remove("script")
        self.edit_yaml("00_input/project.yaml", mutate)
        result = run("validate_project.py", self.project)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("blocos pendentes: [3, 4, 5]", result.stdout)

    def test_metric_without_source_rejected(self):
        self.edit_yaml("00_input/project.yaml", lambda p: p["reference"].update(views_source="unknown"))
        result = run("validate_project.py", self.project)
        self.assertEqual(result.returncode, 1)
        self.assertIn("nunca são inventadas", result.stdout)

    def test_unknown_metrics_are_accepted(self):
        self.edit_yaml("00_input/project.yaml", lambda p: p["reference"].update(
            views=None, age_hours=None, views_source="unknown", age_source="unknown", meets_filter="unknown"))
        self.assertEqual(run("validate_project.py", self.project).returncode, 0)

    def test_meets_filter_must_match_numbers(self):
        self.edit_yaml("00_input/project.yaml", lambda p: p["reference"].update(views=50000))
        result = run("validate_project.py", self.project)
        self.assertEqual(result.returncode, 1)
        self.assertIn("meets_filter", result.stdout)

    def test_state_without_gate_rejected(self):
        self.edit_yaml("00_input/project.yaml", lambda p: p["approved_gates"].remove("packaging"))
        result = run("validate_project.py", self.project)
        self.assertEqual(result.returncode, 1)
        self.assertIn("'packaging'", result.stdout)

    def test_adjacent_trend_requires_trend_gate(self):
        self.edit_yaml("00_input/project.yaml", lambda p: p["approved_gates"].remove("trend_alignment"))
        self.assertEqual(run("validate_project.py", self.project).returncode, 1)

    def test_invalid_mode_rejected(self):
        self.edit_yaml("00_input/project.yaml", lambda p: p.update(mode="copy_the_reference"))
        self.assertEqual(run("validate_project.py", self.project).returncode, 1)


class TestTrendAlignment(FixtureCopy):
    def test_fixture_directions(self):
        result = run("validate_trend_alignment.py", FIXTURE, "--all")
        found = classifications(result.stdout)
        self.assertEqual(found, {"A": "ALIGNED", "B": "ALIGNED", "C": "ALIGNED"}, result.stdout)
        self.assertEqual(result.returncode, 0)

    def test_high_and_medium_proximity_are_aligned(self):
        for direction, level in (("A", "high"), ("B", "medium")):
            with self.subTest(direction=direction):
                result = run("validate_trend_alignment.py", FIXTURE, "--direction", direction)
                self.assertIn(f"(proximidade: {level})", result.stdout)
                self.assertIn("CLASSIFICAÇÃO: ALIGNED", result.stdout)

    def test_negative_cases(self):
        result = run("validate_trend_alignment.py", FIXTURE, "--directions-file", NEGATIVE_CASES)
        self.assertEqual(classifications(result.stdout),
                         {"TOO_DISTANT": "TOO_DISTANT", "TOO_CLOSE": "TOO_CLOSE"}, result.stdout)
        self.assertEqual(result.returncode, 1)

    def test_name_swap_copy_detected_without_name_reuse(self):
        result = run("validate_trend_alignment.py", FIXTURE, "--directions-file", NEGATIVE_CASES,
                     "--direction", "TOO_CLOSE")
        self.assertIn("nomes: novos", result.stdout)
        self.assertIn("repetidos na mesma ordem", result.stdout)
        self.assertIn("eventos proibidos reaproveitados", result.stdout)

    def test_selected_direction_is_default(self):
        result = run("validate_trend_alignment.py", FIXTURE)
        self.assertEqual(list(classifications(result.stdout)), ["A"])
        self.assertEqual(result.returncode, 0)

    def test_reused_reference_name_is_too_close(self):
        self.edit_yaml("04_selected_direction/selected-direction.yaml",
                       lambda d: d["characters"].append({"name": "Tiamat", "role": "dragon"}))
        self.assertIn("CLASSIFICAÇÃO: TOO_CLOSE", run("validate_trend_alignment.py", self.project).stdout)

    def test_single_prohibited_event_requires_review(self):
        self.edit_yaml("04_selected_direction/selected-direction.yaml", lambda d: d["causal_chain"].__setitem__(
            9, "the mother kneels and begs forgiveness before the royal court"))
        result = run("validate_trend_alignment.py", self.project)
        self.assertIn("CLASSIFICAÇÃO: REVIEW_REQUIRED", result.stdout)

    def test_incomplete_direction_requires_review(self):
        def mutate(d):
            d["causal_chain"] = d["causal_chain"][:3]
            d["ending"] = ""
        self.edit_yaml("04_selected_direction/selected-direction.yaml", mutate)
        result = run("validate_trend_alignment.py", self.project)
        self.assertIn("CLASSIFICAÇÃO: REVIEW_REQUIRED", result.stdout)
        self.assertIn("3 passos", result.stdout)

    def test_market_slots_alone_are_not_copy(self):
        # Mãe + filha + dragões explícitos no texto não tornam a direção TOO_CLOSE.
        self.edit_yaml("04_selected_direction/selected-direction.yaml", lambda d: d.update(
            logline="A mother abandons her daughter to the dragons; the daughter's blood hides a royal heir. "
                    + d["logline"]))
        self.assertIn("CLASSIFICAÇÃO: ALIGNED", run("validate_trend_alignment.py", self.project).stdout)

    def test_other_modes_not_applicable(self):
        self.edit_yaml("00_input/project.yaml", lambda p: p.update(mode="original_channel_story"))
        result = run("validate_trend_alignment.py", self.project)
        self.assertEqual(result.returncode, 0)
        self.assertIn("NOT_APPLICABLE", result.stdout)


class TestPackagingAlignment(FixtureCopy):
    ADDENDUM_ALIGNED_TITLES = [
        "Her Mother Offered Her to the Dragon Shrine — Until the Ancient Queen Answered Her Cry.",
        "Sold by Her Family to Calm the Dragons — She Returned as the One They Were Sworn to Obey.",
        "They Called Her Blood a Curse and Cast Her into the Nest — Then the Black Dragon Chose Her.",
    ]
    PARAPHRASES = [
        "Her mother left her to die among the dragons — but she was Tiamat's true heir",
        "Left to Die at the Hands of the Dragons by Her Own Mother — Yet She Was Their Rightful Heir",
        REFERENCE_TITLE,
    ]

    def test_fixture_packaging_passes(self):
        result = run("validate_packaging_alignment.py", FIXTURE)
        self.assertEqual(result.returncode, 0, result.stdout)
        for flag in ("PROMISE_ALIGNED: sim", "EMOTION_ALIGNED: sim", "VISUAL_HOOK_ALIGNED: sim",
                     "FANTASY_HOOK_ALIGNED: sim", "CURIOSITY_GAP_ALIGNED: sim",
                     "TEXT_TOO_CLOSE: não", "COMPOSITION_TOO_CLOSE: não", "PROMISE_TOO_GENERIC: não"):
            self.assertIn(flag, result.stdout)
        self.assertIn("RESULTADO GERAL: PASS", result.stdout)

    def test_addendum_examples_are_not_text_too_close(self):
        for title in self.ADDENDUM_ALIGNED_TITLES:
            with self.subTest(title=title):
                result = run("validate_packaging_alignment.py", FIXTURE, "--title", title)
                self.assertIn("TEXT_TOO_CLOSE: não", result.stdout)
                self.assertIn("PROMISE_TOO_GENERIC: não", result.stdout)

    def test_paraphrases_are_text_too_close(self):
        for title in self.PARAPHRASES:
            with self.subTest(title=title):
                result = run("validate_packaging_alignment.py", FIXTURE, "--title", title)
                self.assertIn("TEXT_TOO_CLOSE: sim", result.stdout)
                self.assertEqual(result.returncode, 1)

    def test_generic_title_detected(self):
        result = run("validate_packaging_alignment.py", FIXTURE, "--title", "A Woman Finds a Dragon")
        self.assertIn("PROMISE_TOO_GENERIC: sim", result.stdout)
        self.assertEqual(result.returncode, 1)

    def test_title_option_without_wave_slots_is_generic(self):
        self.edit_yaml("09_seo/title-options.yaml",
                       lambda t: t["title_options"][0].update(viral_slots_preserved=["dragon_presence"]))
        result = run("validate_packaging_alignment.py", self.project)
        self.assertIn("PROMISE_TOO_GENERIC: sim", result.stdout)

    def test_copied_composition_detected(self):
        ref = yaml.safe_load((FIXTURE / "02_reference_analysis" / "viral-wave-package.yaml").read_text())
        self.edit_yaml("09_seo/packaging.yaml", lambda p: p["thumbnail"].update(
            composition=dict(ref["reference_surface"]["thumbnail"]["composition"])))
        result = run("validate_packaging_alignment.py", self.project)
        self.assertIn("COMPOSITION_TOO_CLOSE: sim", result.stdout)
        self.assertEqual(result.returncode, 1)

    def test_woman_and_dragon_alone_is_not_composition_copy(self):
        self.edit_yaml("09_seo/packaging.yaml", lambda p: p["thumbnail"]["composition"].update(
            pose="girl standing, arms folded",
            dragon_position="dragon perched on a rooftop behind the girl, right side",
            setting="snowy village square at night"))
        result = run("validate_packaging_alignment.py", self.project)
        self.assertIn("COMPOSITION_TOO_CLOSE: não", result.stdout)
        self.assertIn("dimensões iguais à referência: nenhuma", result.stdout)

    def test_prompt_without_ratio_or_negatives_requires_review(self):
        self.edit_yaml("09_seo/packaging.yaml", lambda p: p["thumbnail"].update(
            prompt_en=p["thumbnail"]["prompt_en"].replace("16:9 ", "").replace("no text, no logo, no watermark", "")))
        result = run("validate_packaging_alignment.py", self.project)
        self.assertIn("prompt sem '16:9'", result.stdout)
        self.assertIn("prompt sem 'no watermark'", result.stdout)
        self.assertIn("RESULTADO GERAL: REVIEW_REQUIRED", result.stdout)


class TestTitlePromise(unittest.TestCase):
    def test_fixture_titles(self):
        result = run("validate_title_promise.py", "--project", FIXTURE)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(result.stdout.count("PASS:"), 2)
        self.assertEqual(result.stdout.count("REVIEW_REQUIRED:"), 1)

    def test_they_without_antecedent_requires_review(self):
        result = run("validate_title_promise.py", "They Left")
        self.assertEqual(result.returncode, 0)
        self.assertIn("REVIEW_REQUIRED", result.stdout)

    def test_too_long_fails(self):
        self.assertEqual(run("validate_title_promise.py", "Her Mother " + "Very " * 30 + "Betrayed Her").returncode, 1)

    def test_role_not_in_selected_direction_fails(self):
        result = run("validate_title_promise.py", "Her Sister Left Her to the Dragons — But the Grey One Bowed",
                     "--project", FIXTURE)
        self.assertEqual(result.returncode, 1)
        self.assertIn("'sister'", result.stdout)


class TestExports(FixtureCopy):
    def test_exports_tts_is_clean_and_ordered(self):
        result = run("build_exports.py", self.project)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        out = self.project / "11_exports"
        tts = (out / "tts_plain_text.txt").read_text(encoding="utf-8")
        self.assertNotRegex(tts, r"\[|^#|BLOCO|BLOCK")
        blocks = [(self.project / "06_script" / f"block-{n:02d}.txt").read_text(encoding="utf-8").strip()
                  for n in range(1, 6)]
        positions = [tts.index(b[:60]) for b in blocks]
        self.assertEqual(positions, sorted(positions))
        manifest = json.loads((out / "production_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["characters_per_block"]), 5)
        self.assertTrue(all(3200 <= c <= 3500 for c in manifest["characters_per_block"]))
        self.assertEqual(manifest["mode"], "adjacent_trend")
        for name in ("script_full.txt", "block-05.txt", "thumbnail_prompt_en.txt", "production_manifest.json"):
            self.assertTrue((out / name).exists(), name)

    def test_markers_block_export(self):
        path = self.project / "06_script" / "block-02.txt"
        text = path.read_text(encoding="utf-8")
        path.write_text(text[:3200] + "\n[SFX] wind", encoding="utf-8")
        # O validador recusa antes de exportar: marcadores nunca chegam ao TTS.
        self.assertEqual(run("build_exports.py", self.project).returncode, 1)

    def test_refuses_invalid_blocks(self):
        (self.project / "06_script" / "block-01.txt").write_text("curto demais", encoding="utf-8")
        result = run("build_exports.py", self.project)
        self.assertEqual(result.returncode, 1)
        self.assertFalse((self.project / "11_exports" / "tts_plain_text.txt").exists())


if __name__ == "__main__":
    unittest.main()
