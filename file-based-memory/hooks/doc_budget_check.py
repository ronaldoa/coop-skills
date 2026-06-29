#!/usr/bin/env python3
"""Doc-budget gate: keep AGENTS.md + project-memory/ + the dashboard within their
size disciplines, mechanically.

Why a hook: advisory rules ("keep entries 5-10 lines") get skipped under context
pressure — same rationale as a tsc precommit hook. Only a harness-executed check is
deterministic.

Delta semantics (anti false-positive-fatigue): a file is examined only when its
worktree content differs from HEAD, and within memory files only NEW or MODIFIED
`## ` entries are gated — legacy oversize entries don't block until someone touches
them (fix-when-you-touch). For AGENTS.md only added/rewritten lines are width-checked.

Caps encode the written rules:
- project-memory size discipline: 5-10 lines per entry, link to the canonical doc
  instead of compressing it -> entry caps below.
- AGENTS.md router-row contract: one route = one line -> line cap.
- File budgets stop slow whole-file creep that per-entry checks can't see.

Tune FILE_BUDGETS / LINE_CAPS / ENTRY_CAPS for your repo; defaults are a starting
point, not law.

Bypass (audited, deliberate): DOC_BUDGET_BYPASS=1 on the commit command.
Exit 2 on violation (blocks the gated git commit/push), 0 otherwise.
"""

from __future__ import annotations

import os
import subprocess
import sys

# file -> max bytes (worktree)
FILE_BUDGETS = {
    "AGENTS.md": 64_000,
    "CURRENT_STATUS_AND_NEXT_STEPS.md": 64_000,
    "project-memory/decisions.md": 160_000,
    "project-memory/architecture.md": 96_000,
    "project-memory/experiments.md": 160_000,
}

# file -> max chars for an ADDED line (router rows must stay one-line routes)
LINE_CAPS = {"AGENTS.md": 700}

# file -> (entry_max_chars, entry_max_nonempty_lines, folded_entry_max_chars)
# applies to NEW or MODIFIED `## ` entries only; titles starting with
# "## [FOLDED]" get the larger cap (they index over many folded entries).
ENTRY_CAPS = {
    "project-memory/decisions.md": (3_500, 16, 9_000),
    "project-memory/architecture.md": (3_500, 16, 9_000),
    "project-memory/experiments.md": (6_000, 30, 12_000),
}

SIZE_RULE = "the four-layer size discipline (5-10 lines/entry; link to the doc, don't compress it)"


def head_text(root: str, rel: str) -> str | None:
    r = subprocess.run(
        ["git", "-C", root, "show", f"HEAD:{rel}"],
        capture_output=True,
        text=True,
    )
    return r.stdout if r.returncode == 0 else None


def entries(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    title = None
    buf: list[str] = []
    for ln in text.split("\n"):
        if ln.startswith("## "):
            if title is not None:
                out[title] = "\n".join(buf).strip()
            title, buf = ln, []
        elif title is not None:
            buf.append(ln)
    if title is not None:
        out[title] = "\n".join(buf).strip()
    return out


def main() -> int:
    if os.environ.get("DOC_BUDGET_BYPASS") == "1":
        return 0
    root = os.environ.get("CLAUDE_PROJECT_DIR") or subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
    ).stdout.strip()
    if not root:
        return 0

    violations: list[str] = []
    for rel in FILE_BUDGETS:
        path = os.path.join(root, rel)
        if not os.path.exists(path):
            continue
        work = open(path, encoding="utf-8").read()
        head = head_text(root, rel)
        if head is not None and head == work:
            continue  # untouched this change -> not gated

        budget = FILE_BUDGETS[rel]
        size = len(work.encode("utf-8"))
        if size > budget:
            violations.append(
                f"{rel}: file is {size:,} B > budget {budget:,} B. Trim or fold before "
                f"committing (don't raise the budget) — see {SIZE_RULE}."
            )

        cap = LINE_CAPS.get(rel)
        if cap:
            head_lines = set((head or "").split("\n"))
            for i, ln in enumerate(work.split("\n"), 1):
                if len(ln) > cap and ln not in head_lines:
                    violations.append(
                        f"{rel}:{i}: added/modified line is {len(ln)} chars > {cap}. "
                        f"A router row = trigger -> destination + status (+ at most one "
                        f"load-bearing clause); move narrative into the doc it points at."
                    )

        caps = ENTRY_CAPS.get(rel)
        if caps:
            max_chars, max_lines, folded_chars = caps
            old = entries(head or "")
            for title, body in entries(work).items():
                if old.get(title) == body:
                    continue  # untouched entry -> not gated
                limit = folded_chars if title.startswith("## [FOLDED]") else max_chars
                nonempty = sum(1 for l in body.split("\n") if l.strip())
                if len(body) > limit:
                    violations.append(
                        f"{rel} entry {title[:70]!r}: body is {len(body):,} chars > {limit:,}. "
                        f"Write the conclusion + a link to the canonical doc instead of "
                        f"compressing the doc into memory."
                    )
                elif nonempty > max_lines:
                    violations.append(
                        f"{rel} entry {title[:70]!r}: {nonempty} non-empty lines > {max_lines}. "
                        f"Cap is 5-10 lines per entry — conclusion + canonical-doc link."
                    )

    if violations:
        print("doc-budget gate FAILED — fix the docs, then re-run the commit:", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        print(
            "\nIf this specific oversize is deliberate and reviewed, re-run with "
            "DOC_BUDGET_BYPASS=1 on the same command and say so in the commit message.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
