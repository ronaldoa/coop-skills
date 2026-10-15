#!/usr/bin/env python3
"""Doc gates: the mechanical half of the doc-index and workline rules.

Why a hook: every rule below was first written as prose and rotted anyway (five
"start here" markers in one plan; line pointers that silently pointed at the wrong
code). Prose is the weak form; only an executed check holds.

Checks, on every changed markdown file under DOC_GATES_DIRS (delta-scoped like
doc_budget_check.py: a file is examined only when it differs from HEAD or is new):

  G1 stamp      the first 20 lines carry `> STATUS: <status> · <YYYY-MM-DD> · <text>`
                and <status> is in DOC_GATES_STATUSES (empty = any non-empty word)
  G2 one entry  at most one heading containing DOC_GATES_ENTRY_MARKER that is not
                demoted with "[SUPERSEDED"
  G3 pointers   every `path#symbol` resolves: `path` may be a suffix (`agent/plan.ts`,
                or a bare `plan.ts`); among the repo files ending with it, EXACTLY ONE
                contains the symbol (none = dead pointer, several = ambiguous)
  G4 no lines   no ADDED line introduces a `path.ext:NN` pointer

`--all` checks every markdown file (use once when adopting the gates; expect debt).
Bypass (audited): DOC_GATES_BYPASS=1 on the gated command. Exit 2 on violation.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys

DEFAULT_STATUSES = (
    "in-flight,active,not-started,rejected,DONE,ratified,reference,stale,undetermined"
)
STAMP_RE = re.compile(r"^> STATUS: (\S[^·]*?) · (\d{4}-\d{2}-\d{2}) · (\S.*)$")
POINTER_RE = re.compile(r"`([A-Za-z0-9_./-]+\.[A-Za-z0-9]+)#([A-Za-z_$][\w$]*)`")
LINE_POINTER_RE = re.compile(
    r"\b[\w./-]+\.(?:ts|tsx|js|jsx|mjs|cjs|py|go|rs|java|kt|rb|php|c|h|cc|cpp|hpp|cs|swift|sql|sh):\d+\b"
)
HEADING_RE = re.compile(r"^#{1,6} ")


def read(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def git(root: str, *args: str) -> str:
    r = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def changed_docs(root: str, dirs: list[str]) -> list[str]:
    tracked = git(root, "diff", "--name-only", "HEAD", "--", *dirs).split()
    new = git(root, "ls-files", "--others", "--exclude-standard", "--", *dirs).split()
    return sorted({p for p in tracked + new if p.endswith(".md")})


def all_docs(root: str, dirs: list[str]) -> list[str]:
    tracked = git(root, "ls-files", "--", *dirs).split()
    new = git(root, "ls-files", "--others", "--exclude-standard", "--", *dirs).split()
    return sorted({p for p in tracked + new if p.endswith(".md")})


def added_lines(root: str, rel: str) -> list[str]:
    if not git(root, "ls-files", "--", rel).strip():  # untracked: every line is new
        with open(os.path.join(root, rel), encoding="utf-8") as f:
            return f.read().splitlines()
    diff = git(root, "diff", "--unified=0", "HEAD", "--", rel)
    return [l[1:] for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]


SKIP_DIRS = {".git", "node_modules", "dist", "build", ".venv", "__pycache__"}


def file_index(root: str) -> dict[str, list[str]]:
    """basename -> every repo path with that basename. Walked, so a moved file is a MISS, not a guess."""
    idx: dict[str, list[str]] = {}
    for d, subdirs, files in os.walk(root):
        subdirs[:] = [s for s in subdirs if s not in SKIP_DIRS]
        for name in files:
            idx.setdefault(name, []).append(os.path.relpath(os.path.join(d, name), root).replace(os.sep, "/"))
    return idx


def check_file(root: str, rel: str, statuses: set[str], marker: str, exempt: set[str], idx: dict[str, list[str]]) -> list[str]:
    path = os.path.join(root, rel)
    if not os.path.exists(path):  # deleted in the worktree
        return []
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    errs: list[str] = []

    if os.path.basename(rel) not in exempt:
        stamp = next((m for m in map(STAMP_RE.match, lines[:20]) if m), None)
        if stamp is None:
            errs.append(f"G1 {rel}: no `> STATUS: <status> · <YYYY-MM-DD> · <one line>` in the first 20 lines")
        elif statuses and stamp.group(1).strip() not in statuses:
            errs.append(f"G1 {rel}: status '{stamp.group(1).strip()}' not in {sorted(statuses)}")

    live = [
        i + 1 for i, l in enumerate(lines)
        if HEADING_RE.match(l) and marker in l and "[SUPERSEDED" not in l
    ]
    if len(live) > 1:
        errs.append(f"G2 {rel}: {len(live)} live '{marker}' headings (lines {live}); demote all but one with [SUPERSEDED <date> → …]")

    for i, l in enumerate(lines):
        for m in POINTER_RE.finditer(l):
            target, symbol = m.group(1), m.group(2)
            candidates = [
                p for p in idx.get(target.rsplit("/", 1)[-1], [])
                if p == target or p.endswith("/" + target)
            ]
            if not candidates:
                errs.append(f"G3 {rel}:{i + 1}: `{target}#{symbol}` — file does not exist")
                continue
            sym_re = re.compile(rf"(?<![\w$]){re.escape(symbol)}(?![\w$])")
            hits = [p for p in candidates if sym_re.search(read(os.path.join(root, p)))]
            if not hits:
                errs.append(f"G3 {rel}:{i + 1}: `{target}#{symbol}` — symbol not found in file")
            elif len(hits) > 1:
                errs.append(f"G3 {rel}:{i + 1}: `{target}#{symbol}` — ambiguous, {len(hits)} files contain it; qualify the path")

    for l in added_lines(root, rel):
        for m in LINE_POINTER_RE.finditer(l):
            errs.append(f"G4 {rel}: new line-number pointer '{m.group(0)}' — write `path#symbol` instead")
    return errs


def main(argv: list[str]) -> int:
    root = os.environ.get("CLAUDE_PROJECT_DIR") or git(os.getcwd(), "rev-parse", "--show-toplevel").strip() or os.getcwd()
    dirs = [d for d in os.environ.get("DOC_GATES_DIRS", "docs").split(",") if d]
    raw = os.environ.get("DOC_GATES_STATUSES", DEFAULT_STATUSES)
    statuses = {s.strip() for s in raw.split(",") if s.strip()}
    marker = os.environ.get("DOC_GATES_ENTRY_MARKER", "START HERE")
    exempt = {s for s in os.environ.get("DOC_GATES_EXEMPT", "INDEX.md,README.md").split(",") if s}

    files = all_docs(root, dirs) if "--all" in argv else changed_docs(root, dirs)
    idx = file_index(root) if files else {}
    errs = [e for rel in files for e in check_file(root, rel, statuses, marker, exempt, idx)]
    if errs:
        print("doc gates failed (see the file-based-memory skill: references/doc-index.md, worklines.md):", file=sys.stderr)
        for e in errs:
            print("  " + e, file=sys.stderr)
        print("Bypass deliberately with DOC_GATES_BYPASS=1 on the command, and say why in the message.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
