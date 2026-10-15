#!/usr/bin/env python3
"""Ceiling gate: a markdown file that declares `Ceiling: N lines` in its first ten lines
may not exceed N lines (counted as `wc -l` does).

Why a check and not a sentence: both instruction files in the origin project stated a
ceiling in prose; one sat at exactly its ceiling and the next append would have crossed it
silently, the other let one section grow to 42% of the file. Nothing went red. The
ceiling is the mechanism that forces "is this worth more than what it replaces?".

Scans every tracked or untracked (not ignored) `*.md` in the repo — few files declare a
ceiling, and a ceiling can be crossed by any edit to them, so there is no delta scope.
Bypass (audited): CEILING_BYPASS=1 on the gated command. Exit 2 on violation.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys

CEILING_RE = re.compile(r"Ceiling:\s*(\d+)\s*lines", re.I)


def repo_markdown(root: str) -> list[str]:
    out = subprocess.run(
        ["git", "-C", root, "ls-files", "--cached", "--others", "--exclude-standard", "--", "*.md"],
        capture_output=True, text=True,
    ).stdout.split("\n")
    return sorted({p for p in out if p})


def check(root: str) -> list[str]:
    errs = []
    for rel in repo_markdown(root):
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
        head = "\n".join(text.split("\n")[:10]).replace("*", "")
        m = CEILING_RE.search(head)
        if not m:
            continue
        ceiling, lines = int(m.group(1)), text.count("\n")
        if lines > ceiling:
            errs.append(f"{rel}: {lines} lines > declared ceiling {ceiling} — merge or delete a rule; don't raise the ceiling to fit")
    return errs


def main() -> int:
    root = os.environ.get("CLAUDE_PROJECT_DIR") or subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
    ).stdout.strip() or os.getcwd()
    errs = check(root)
    if errs:
        print("ceiling gate failed (see the engineering-discipline skill):", file=sys.stderr)
        for e in errs:
            print("  " + e, file=sys.stderr)
        print("Bypass deliberately with CEILING_BYPASS=1 on the command, and say why in the message.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
