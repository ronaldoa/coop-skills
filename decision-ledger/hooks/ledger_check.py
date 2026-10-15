#!/usr/bin/env python3
"""Ledger gate: the mechanical half of the decision-ledger rules.

  L1 debt ids   in LEDGER_DEBT_FILE, every entry heading appears exactly once, every
                index row `[D-<id>](#d-<id>)` has an entry, every entry has a row.
                Entry heading = `### D-<id>` then end of line, ` — <title>`, ` · …` or
                `{#d-<id>}` (`### D-93 measurements` is a SUBSECTION of D-93, not an entry).
                Index = the first table after `<a id="debt-index">`, else the first table
                with D- rows, up to the next BLANK line as in GFM (a table inside an entry
                body is not the index; a row broken across lines does not end the table).
  L2 rulings    across LEDGER_DIRS, no text cites `Qn (open)` while that question's own
                entry is `### Qn [RULED …]`, and no citation names a question that does
                not exist. `Qn (open)` cites the same doc; `` `FILE.md` Qn (open) `` cites
                FILE.md (basename, resolved inside LEDGER_DIRS)

Both are whole-tree scans, not delta-scoped: ruling Qn in one doc makes OTHER, untouched
docs wrong, and that is exactly the moment this must go red. Both are pure functions of
text, so nothing outside the docs can turn them red.

It catches only these shapes. A ruled question still listed as a "candidate" in prose,
or a ruling never propagated to a table row, stays a human check.
Bypass (audited): LEDGER_BYPASS=1 on the gated command. Exit 2 on violation.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys

DEBT_HEADING_RE = re.compile(r"^### (D-\d+[a-z]?)(?:[ \t]*$|[ \t]+[—·]|[ \t]*\{#)", re.M)
DEBT_ROW_RE = re.compile(r"^\|\s*\[(D-\d+[a-z]?)\]\(#([\w-]+)\)")
INDEX_ANCHOR = 'id="debt-index"'
Q_HEADING_RE = re.compile(r"^#{2,6} Q(\d+) \[(OPEN|RULED[^\]]*|PARKED[^\]]*)\]", re.M)
Q_OPEN_CITE_RE = re.compile(r"(?:`([\w./-]+\.md)`\s*)?(?<![\w-])Q(\d+) \(open\)")


COMMENT_RE = re.compile(r"<!--.*?-->", re.S)


def read(path: str) -> str:
    """File text with HTML comments blanked (newlines kept, so line numbers hold): a
    template's commented-out example entry is not an entry."""
    with open(path, encoding="utf-8", errors="replace") as f:
        return COMMENT_RE.sub(lambda m: "\n" * m.group(0).count("\n"), f.read())


def index_rows(text: str) -> list[tuple[str, str]]:
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if INDEX_ANCHOR in l), None)
    if start is None:
        start = next((i for i, l in enumerate(lines) if DEBT_ROW_RE.match(l)), len(lines))
    i = start
    while i < len(lines) and not lines[i].startswith("|"):
        i += 1
    rows = []
    while i < len(lines) and lines[i].strip():  # GFM: a table ends at a blank line, not at a pipe-less line
        m = DEBT_ROW_RE.match(lines[i])
        if m:
            rows.append((m.group(1), m.group(2)))
        i += 1
    return rows


def check_debt(root: str, rel: str) -> list[str]:
    path = os.path.join(root, rel)
    if not os.path.exists(path):
        return []
    text = read(path)
    heads = DEBT_HEADING_RE.findall(text)
    rows = index_rows(text)
    errs = []
    for d in sorted({h for h in heads if heads.count(h) > 1}):
        errs.append(f"L1 {rel}: {d} has {heads.count(d)} headings — ids are never reused; renumber the later one")
    row_ids = [r[0] for r in rows]
    for d in sorted({r for r in row_ids if row_ids.count(r) > 1}):
        errs.append(f"L1 {rel}: {d} has {row_ids.count(d)} index rows")
    for d, anchor in rows:
        if anchor != d.lower():
            errs.append(f"L1 {rel}: index row {d} links #{anchor}, expected #{d.lower()}")
    for d in sorted(set(row_ids) - set(heads)):
        errs.append(f"L1 {rel}: index row {d} has no `### {d}` heading")
    for d in sorted(set(heads) - set(row_ids)):
        errs.append(f"L1 {rel}: `### {d}` has no index row")
    return errs


def md_files(root: str, dirs: list[str]) -> list[str]:
    out = []
    for d in dirs:
        for dp, sub, files in os.walk(os.path.join(root, d)):
            sub[:] = [s for s in sub if s not in {".git", "node_modules"}]
            out += [os.path.relpath(os.path.join(dp, f), root).replace(os.sep, "/") for f in files if f.endswith(".md")]
    return sorted(out)


def check_rulings(root: str, dirs: list[str]) -> list[str]:
    docs = md_files(root, dirs)
    texts = {rel: read(os.path.join(root, rel)) for rel in docs}
    questions = {rel: {int(n): state for n, state in Q_HEADING_RE.findall(t)} for rel, t in texts.items()}
    by_base: dict[str, list[str]] = {}
    for rel in docs:
        by_base.setdefault(rel.rsplit("/", 1)[-1], []).append(rel)
    errs = []
    for rel, text in texts.items():
        for i, line in enumerate(text.splitlines()):
            if Q_HEADING_RE.match(line):
                continue
            for m in Q_OPEN_CITE_RE.finditer(line):
                named, n = m.group(1), int(m.group(2))
                if named:
                    targets = [p for p in by_base.get(named.rsplit("/", 1)[-1], []) if p == named or p.endswith("/" + named)]
                    if len(targets) != 1:
                        errs.append(f"L2 {rel}:{i + 1}: `{named}` Q{n} — {'no' if not targets else 'ambiguous'} such doc in {dirs}")
                        continue
                    target = targets[0]
                else:
                    target = rel
                state = questions[target].get(n)
                if state is None:
                    errs.append(f"L2 {rel}:{i + 1}: Q{n} (open) — {target} has no `### Q{n} [...]` entry")
                elif state != "OPEN":
                    errs.append(f"L2 {rel}:{i + 1}: says Q{n} (open), but {target} marks it [{state}] — update the citation")
    return errs


def main() -> int:
    root = os.environ.get("CLAUDE_PROJECT_DIR") or subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
    ).stdout.strip() or os.getcwd()
    debt = os.environ.get("LEDGER_DEBT_FILE", "docs/DEBT_REGISTER.md")
    dirs = [d for d in os.environ.get("LEDGER_DIRS", "docs").split(",") if d and os.path.isdir(os.path.join(root, d))]
    errs = check_debt(root, debt) + check_rulings(root, dirs)
    if errs:
        print("ledger gate failed (see the decision-ledger skill):", file=sys.stderr)
        for e in errs:
            print("  " + e, file=sys.stderr)
        print("Bypass deliberately with LEDGER_BYPASS=1 on the command, and say why in the message.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
