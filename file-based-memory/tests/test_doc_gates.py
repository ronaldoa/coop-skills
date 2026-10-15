"""Criteria for hooks/doc_gates.py.  Run: python3 -m unittest discover -s file-based-memory/tests

Each gate has a clean case that must pass AND a broken case that must fail with that
gate's code — a test that only checks "something failed" lets one gate's red hide
another gate's missing check.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest

HOOK = os.path.join(os.path.dirname(__file__), "..", "hooks", "doc_gates.py")
STAMP = "> STATUS: in-flight · 2026-10-15 · a line\n"


def sh(root: str, *args: str) -> None:
    subprocess.run(args, cwd=root, check=True, capture_output=True)


class DocGates(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        sh(self.root, "git", "init", "-q")
        sh(self.root, "git", "config", "user.email", "t@example.invalid")
        sh(self.root, "git", "config", "user.name", "t")
        os.makedirs(os.path.join(self.root, "docs"))
        os.makedirs(os.path.join(self.root, "src"))
        self.write("src/a.ts", "export function applyTurnTransition() {}\n")
        self.write("docs/OLD.md", "# Old\n\nsee src/a.ts:12 for history\n")  # pre-existing debt
        sh(self.root, "git", "add", "-A")
        sh(self.root, "git", "commit", "-qm", "init")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write(self, rel: str, text: str) -> None:
        with open(os.path.join(self.root, rel), "w", encoding="utf-8") as f:
            f.write(text)

    def run_gates(self, *argv: str) -> subprocess.CompletedProcess:
        env = {**os.environ, "CLAUDE_PROJECT_DIR": self.root}
        for k in ("DOC_GATES_DIRS", "DOC_GATES_STATUSES", "DOC_GATES_ENTRY_MARKER", "DOC_GATES_EXEMPT"):
            env.pop(k, None)
        return subprocess.run([sys.executable, HOOK, *argv], env=env, capture_output=True, text=True)

    def assert_red(self, code: str) -> None:
        r = self.run_gates()
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn(code, r.stderr)

    def assert_green(self) -> None:
        r = self.run_gates()
        self.assertEqual(r.returncode, 0, r.stderr)

    # vacuity guard: an untouched tree checks nothing and passes; --all sees the debt
    def test_delta_scope(self) -> None:
        self.assert_green()
        r = self.run_gates("--all")
        self.assertEqual(r.returncode, 2)
        self.assertIn("G1 docs/OLD.md", r.stderr)

    def test_clean_doc_passes(self) -> None:
        self.write("docs/LINE.md", f"# Line\n\n{STAMP}\n## 0. Handoff — START HERE\n\nsee `src/a.ts#applyTurnTransition`\n")
        self.assert_green()

    def test_g1_missing_stamp(self) -> None:
        self.write("docs/LINE.md", "# Line\n\nno stamp\n")
        self.assert_red("G1 docs/LINE.md: no `> STATUS")

    def test_g1_status_outside_vocabulary(self) -> None:
        self.write("docs/LINE.md", "> STATUS: wip · 2026-10-15 · x\n")
        self.assert_red("status 'wip' not in")

    def test_g1_exempt_index(self) -> None:
        self.write("docs/INDEX.md", "# Index\n")
        self.assert_green()

    def test_g2_two_live_entries(self) -> None:
        self.write("docs/LINE.md", f"{STAMP}## START HERE (new)\n\n## START HERE (old)\n")
        self.assert_red("G2 docs/LINE.md: 2 live")

    def test_g2_superseded_entry_is_not_live(self) -> None:
        self.write("docs/LINE.md", f"{STAMP}## START HERE (new)\n\n## [SUPERSEDED 2026-10-01 → §0] START HERE (old)\n")
        self.assert_green()

    def test_g3_missing_file(self) -> None:
        self.write("docs/LINE.md", f"{STAMP}`src/gone.ts#applyTurnTransition`\n")
        self.assert_red("file does not exist")

    def test_g3_missing_symbol(self) -> None:
        self.write("docs/LINE.md", f"{STAMP}`src/a.ts#applyTurn`\n")  # a PREFIX of the real name: substring search would accept it
        self.assert_red("symbol not found")

    def test_g3_basename_suffix_resolves(self) -> None:
        self.write("docs/LINE.md", f"{STAMP}`a.ts#applyTurnTransition`\n")
        self.assert_green()

    def test_g3_suffix_must_end_on_a_path_segment(self) -> None:
        self.write("docs/LINE.md", f"{STAMP}`c/a.ts#applyTurnTransition`\n")  # src/a.ts does not end with /c/a.ts
        self.assert_red("file does not exist")

    def test_g3_ambiguous_basename(self) -> None:
        os.makedirs(os.path.join(self.root, "lib"))
        self.write("lib/a.ts", "export const applyTurnTransition = 1\n")
        self.write("docs/LINE.md", f"{STAMP}`a.ts#applyTurnTransition`\n")
        self.assert_red("ambiguous, 2 files")

    def test_g3_symbol_disambiguates_basename(self) -> None:
        os.makedirs(os.path.join(self.root, "lib"))
        self.write("lib/a.ts", "export const other = 1\n")
        self.write("docs/LINE.md", f"{STAMP}`a.ts#applyTurnTransition`\n")
        self.assert_green()

    def test_g4_new_line_pointer(self) -> None:
        self.write("docs/LINE.md", f"{STAMP}see src/a.ts:3\n")
        self.assert_red("G4 docs/LINE.md: new line-number pointer 'src/a.ts:3'")

    def test_g4_only_added_lines(self) -> None:
        # touching OLD.md must not flag its pre-existing pointer (fix-when-you-touch is G1's job)
        self.write("docs/OLD.md", f"{STAMP}# Old\n\nsee src/a.ts:12 for history\n")
        self.assert_green()


if __name__ == "__main__":
    unittest.main()
