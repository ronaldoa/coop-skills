# Optional enforcement: the doc-budget gate

Advisory rules ("keep entries 5–10 lines") get skipped under context pressure —
the same reason type-checks belong in a hook, not a README. For deterministic size
discipline, this plugin ships an optional **precommit gate**.

## What it does

`hooks/doc_budget_check.py` blocks a `git commit`/`git push` (exit 2) when a tracked
memory/router file violates its size discipline. It is wired through
`hooks/doc-budget-precommit.sh`, a `PreToolUse(Bash)` hook that runs the check only
when the about-to-run command is a commit/push.

It encodes the written rules mechanically:

- **Per-entry caps** on `project-memory/*` — 5–10 lines / a char ceiling per `## `
  entry, so an entry can't grow into a re-statement of a spec. A `## [FOLDED]`
  entry indexes over a closed cluster, so it gets the larger folded cap — see
  [supersede-trail.md](supersede-trail.md#folding-a-closed-cluster-folded).
- **Router line cap** on `AGENTS.md` — one route = one line (trigger → destination +
  status), so the index can't absorb narrative.
- **Whole-file budgets** — catch slow creep that per-entry checks miss.

## Delta semantics (anti false-positive-fatigue)

The gate is **delta-scoped**, so it never blocks you for pre-existing debt:

- A file is examined only when its worktree content differs from `HEAD`.
- Within memory files, only **new or modified** `## ` entries are gated — legacy
  oversize entries don't block until someone touches them (fix-when-you-touch).
- For `AGENTS.md`, only added/rewritten lines are width-checked.

## Bypass (audited, deliberate)

When an oversize is genuinely intended and reviewed:

```bash
DOC_BUDGET_BYPASS=1 git commit -m "deliberate oversize: <why>"
```

Set it on the gated command itself and say why in the commit message, so the
exception is visible in history.

## Tuning

Edit the `FILE_BUDGETS`, `LINE_CAPS`, and `ENTRY_CAPS` dicts at the top of
`hooks/doc_budget_check.py` to fit your repo. The shipped defaults are a sane
starting point, not law.

## If you don't want it

The gate is optional. To drop it, remove the `PreToolUse` block from
`hooks/hooks.json` (or delete the two `doc*` files). The cadence `Stop` hook and the
rest of the kit work without it.
