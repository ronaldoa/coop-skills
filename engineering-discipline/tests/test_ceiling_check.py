"""Criteria for hooks/ceiling_check.py.  Run: python3 -m unittest discover -s engineering-discipline/tests"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest

HOOK = os.path.join(os.path.dirname(__file__), "..", "hooks", "ceiling_check.py")


class CeilingCheck(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write(self, rel: str, text: str) -> None:
        os.makedirs(os.path.dirname(os.path.join(self.root, rel)) or self.root, exist_ok=True)
        with open(os.path.join(self.root, rel), "w", encoding="utf-8") as f:
            f.write(text)

    def run_check(self) -> subprocess.CompletedProcess:
        env = {**os.environ, "CLAUDE_PROJECT_DIR": self.root}
        return subprocess.run([sys.executable, HOOK], env=env, capture_output=True, text=True)

    @staticmethod
    def doc(ceiling: int, lines: int) -> str:
        head = f"# Rules\n\n> **Ceiling: {ceiling} lines** — merge or delete.\n"
        return head + "x\n" * (lines - 3)

    def test_at_ceiling_passes(self) -> None:
        self.write("AGENTS.md", self.doc(20, 20))
        r = self.run_check()
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_over_ceiling_fails(self) -> None:
        self.write("AGENTS.md", self.doc(20, 21))
        r = self.run_check()
        self.assertEqual(r.returncode, 2)
        self.assertIn("AGENTS.md: 21 lines > declared ceiling 20", r.stderr)

    def test_nested_untracked_file_is_scanned(self) -> None:
        self.write("docs/PRINCIPLES.md", self.doc(10, 12))
        r = self.run_check()
        self.assertIn("docs/PRINCIPLES.md: 12 lines", r.stderr)

    def test_declaration_must_be_in_the_head(self) -> None:
        # a ceiling QUOTED deep in a doc is not that doc's declaration
        self.write("NOTES.md", "# Notes\n" + "x\n" * 15 + "the router says Ceiling: 3 lines\n")
        r = self.run_check()
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_ignored_file_is_not_scanned(self) -> None:
        self.write(".gitignore", "scratch/\n")
        self.write("scratch/A.md", self.doc(5, 9))
        r = self.run_check()
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
