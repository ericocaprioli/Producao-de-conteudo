"""Confere se a skill, os comandos de barra e as etapas da fábrica estão em sincronia."""

import json
import re
import unittest
from pathlib import Path

FACTORY = Path(__file__).resolve().parent.parent
REPO = FACTORY.parent
SKILL = REPO / ".claude" / "skills" / "wingborn-video" / "SKILL.md"
SLASH = REPO / ".claude" / "commands"


class TestRepoSetup(unittest.TestCase):
    def test_every_step_has_a_slash_command_pointing_to_it(self):
        for step in sorted((FACTORY / "commands").glob("*.md")):
            with self.subTest(step=step.name):
                wrapper = SLASH / step.name
                self.assertTrue(wrapper.exists(), f"falta .claude/commands/{step.name}")
                self.assertIn(f"wingborn-content-factory/commands/{step.name}", wrapper.read_text(encoding="utf-8"))

    def test_entry_commands_exist(self):
        for name in ("novo-video.md", "status.md"):
            self.assertTrue((SLASH / name).exists(), name)

    def test_slash_commands_have_description(self):
        for f in SLASH.glob("*.md"):
            with self.subTest(f=f.name):
                text = f.read_text(encoding="utf-8")
                self.assertTrue(text.startswith("---\ndescription: "), f.name)

    def test_skill_frontmatter_and_paths(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertRegex(text, r"\A---\nname: wingborn-video\ndescription: .+\n---\n")
        for rel in re.findall(r"`(wingborn-content-factory/[\w./-]+)`", text):
            with self.subTest(path=rel):
                self.assertTrue((REPO / rel).exists(), rel)
        for step in re.findall(r"\| `([a-z-]+)(?: N)?` —", text):
            with self.subTest(step=step):
                self.assertTrue((FACTORY / "commands" / f"{step}.md").exists(), step)

    def test_settings_hook_is_valid_json(self):
        settings = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
        self.assertIn("SessionStart", settings["hooks"])

    def test_beginner_guide_mentions_entry_points(self):
        guide = (REPO / "GUIA-INICIANTE.md").read_text(encoding="utf-8")
        for needle in ("/novo-video", "/status", "kaggle_narracao.ipynb", "Phone Verification", "main"):
            self.assertIn(needle, guide)


if __name__ == "__main__":
    unittest.main()
