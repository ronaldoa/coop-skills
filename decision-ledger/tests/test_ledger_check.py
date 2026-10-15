"""Criteria for hooks/ledger_check.py.  Run: python3 -m unittest discover -s decision-ledger/tests

Each arm has a clean case and a broken case asserting that arm's own message, so one
arm's red cannot stand in for another arm's missing check.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest

HOOK = os.path.join(os.path.dirname(__file__), "..", "hooks", "ledger_check.py")

REGISTER = """# Debt register

| ID | One line | Status | Priority |
|---|---|---|---|
| [D-1](#d-1) | a | 🔴 OPEN | P1 |
| [D-2](#d-2) | b | ✅ CLOSED | P2 |

### D-1
x
### D-2
y
"""

PLAN = """# Plan
## 15. Open questions
### Q1 [OPEN] still open
### Q2 [RULED 2026-10-14] closed
⚖️ user "确认封闭"
"""


class LedgerCheck(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        os.makedirs(os.path.join(self.root, "docs", "sub"))
        self.write("docs/DEBT_REGISTER.md", REGISTER)
        self.write("docs/PLAN.md", PLAN)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write(self, rel: str, text: str) -> None:
        with open(os.path.join(self.root, rel), "w", encoding="utf-8") as f:
            f.write(text)

    def run_check(self) -> subprocess.CompletedProcess:
        env = {**os.environ, "CLAUDE_PROJECT_DIR": self.root}
        env.pop("LEDGER_DEBT_FILE", None)
        env.pop("LEDGER_DIRS", None)
        return subprocess.run([sys.executable, HOOK], env=env, capture_output=True, text=True)

    def assert_red(self, msg: str) -> None:
        r = self.run_check()
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn(msg, r.stderr)

    def assert_green(self) -> None:
        r = self.run_check()
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_clean_passes(self) -> None:
        self.write("docs/OTHER.md", "see `PLAN.md` Q1 (open) and the ruled `PLAN.md` Q2\n")
        self.write("docs/PLAN.md", PLAN + "\nnext: Q1 (open)\n")
        self.assert_green()

    # ── L1 ──
    def test_l1_duplicate_heading(self) -> None:
        self.write("docs/DEBT_REGISTER.md", REGISTER + "### D-2\ncollided\n")
        self.assert_red("D-2 has 2 headings")

    def test_l1_duplicate_row(self) -> None:
        self.write("docs/DEBT_REGISTER.md", REGISTER.replace("| [D-2](#d-2) | b |", "| [D-2](#d-2) | b |\n| [D-2](#d-2) | again |"))
        self.assert_red("D-2 has 2 index rows")

    def test_l1_row_without_heading(self) -> None:
        self.write("docs/DEBT_REGISTER.md", REGISTER.replace("### D-2\ny\n", ""))
        self.assert_red("index row D-2 has no `### D-2` heading")

    def test_l1_heading_without_row(self) -> None:
        self.write("docs/DEBT_REGISTER.md", REGISTER + "### D-3\nnew\n")
        self.assert_red("`### D-3` has no index row")

    def test_l1_wrong_anchor(self) -> None:
        self.write("docs/DEBT_REGISTER.md", REGISTER.replace("[D-2](#d-2)", "[D-2](#d-1)"))
        self.assert_red("index row D-2 links #d-1")

    def test_l1_subsection_heading_is_not_an_entry(self) -> None:
        self.write("docs/DEBT_REGISTER.md", REGISTER + "### D-2 measurements (2026-08-07)\n### D-2(original symptom)— kept\n")
        self.assert_green()

    def test_l1_titled_entry_heading_counts(self) -> None:
        self.write("docs/DEBT_REGISTER.md", REGISTER + "### D-2 — collided title {#d-2}\n")
        self.assert_red("D-2 has 2 headings")

    def test_l1_table_in_entry_body_is_not_the_index(self) -> None:
        self.write("docs/DEBT_REGISTER.md", REGISTER + "\n| id | why |\n|---|---|\n| [D-1](#d-1) | cited again |\n")
        self.assert_green()

    def test_l1_anchor_selects_the_index_table(self) -> None:
        # a pointer table ABOVE the anchor must not be taken for the index
        text = "| [D-9](#d-9) | stray |\n\n" + REGISTER.replace("| ID |", '<a id="debt-index"></a>\n\n| ID |')
        self.write("docs/DEBT_REGISTER.md", text)
        self.assert_green()

    def test_l1_wrapped_row_does_not_end_the_index(self) -> None:
        self.write("docs/DEBT_REGISTER.md", REGISTER.replace("| [D-1](#d-1) | a |", "| [D-1](#d-1) | a\n continued |"))
        self.assert_green()

    def test_commented_examples_are_not_content(self) -> None:
        self.write("docs/DEBT_REGISTER.md", REGISTER + "<!-- example\n### D-9 — template\n-->\n")
        self.write("docs/PLAN.md", PLAN + "<!-- e.g. Q2 (open) -->\n")
        self.assert_green()

    def test_shipped_template_passes(self) -> None:
        tmpl = os.path.join(os.path.dirname(__file__), "..", "skills", "decision-ledger", "templates", "DEBT_REGISTER.md.tmpl")
        with open(tmpl, encoding="utf-8") as f:
            self.write("docs/DEBT_REGISTER.md", f.read())
        self.assert_green()

    def test_l1_missing_register_is_not_an_error(self) -> None:
        os.remove(os.path.join(self.root, "docs/DEBT_REGISTER.md"))
        self.assert_green()

    # ── L2 ──
    def test_l2_same_doc_stale_open(self) -> None:
        self.write("docs/PLAN.md", PLAN + "\nblocked on Q2 (open)\n")
        self.assert_red("says Q2 (open), but docs/PLAN.md marks it [RULED 2026-10-14]")

    def test_l2_cross_doc_stale_open(self) -> None:
        self.write("docs/sub/OTHER.md", "depends on `PLAN.md` Q2 (open)\n")
        self.assert_red("docs/sub/OTHER.md:1: says Q2 (open), but docs/PLAN.md")

    def test_l2_cross_doc_resolves_to_named_file_not_self(self) -> None:
        # OTHER.md has its own RULED Q1; the citation names PLAN.md, whose Q1 is OPEN ⇒ green
        self.write("docs/OTHER.md", "### Q1 [RULED 2026-10-01] own\n\nsee `PLAN.md` Q1 (open)\n")
        self.assert_green()

    def test_l2_unknown_question(self) -> None:
        self.write("docs/PLAN.md", PLAN + "\nsee Q9 (open)\n")
        self.assert_red("Q9 (open) — docs/PLAN.md has no `### Q9 [...]` entry")

    def test_l2_unknown_doc(self) -> None:
        self.write("docs/OTHER.md", "see `GONE.md` Q1 (open)\n")
        self.assert_red("`GONE.md` Q1 — no such doc")

    def test_l2_parked_is_not_open(self) -> None:
        self.write("docs/PLAN.md", PLAN + "### Q3 [PARKED 2026-10-12] later\n\nwaiting on Q3 (open)\n")
        self.assert_red("marks it [PARKED 2026-10-12]")


if __name__ == "__main__":
    unittest.main()
