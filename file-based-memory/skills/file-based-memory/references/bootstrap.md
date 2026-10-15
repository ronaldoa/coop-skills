# Resume order and the router

## Reading order on every resume

1. **`CURRENT_STATUS_AND_NEXT_STEPS.md`** — always. In multi-workline mode it is a table;
   follow your line's row to that doc's `§0.0` handoff block.
2. **`project-memory/decisions.md`** — only if the task involves an architectural /
   threshold / scope choice (avoids re-litigating measured decisions).
3. **`project-memory/architecture.md`** — only if touching invariants.
4. **`project-memory/experiments.md`** — only if running or interpreting evals.

Reads 2–4 are conditional on purpose: loading all memory every session spends context on
rationale the task does not need.

## The router (`AGENTS.md`)

The first file any agent reads. It routes; it does not store. Routes are one line each
(trigger → destination + status); narrative goes into the destination. An index that
restates truth goes stale silently and then misleads.

Tool overlays (e.g. `CLAUDE.md`) layer on top of `AGENTS.md` and hold only what is
specific to that tool; they never replace or copy it.
