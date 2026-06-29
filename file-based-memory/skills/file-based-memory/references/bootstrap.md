# Bootstrap & the router: truth vs index

## The router (`AGENTS.md`)

`AGENTS.md` is the **shared agent entrypoint** — the first file any agent reads.
Its job is to *route*, not to *store*: it orients a newcomer to the layout, lists
the commands, and points at where each kind of truth lives (code, `docs/`,
`project-memory/`). It is an **index**, not a source of truth.

Why keep them separate: an index that starts restating the truth becomes a second,
drifting copy. When the code or a spec changes, the index silently goes stale and
now actively misleads. Keep routes one line each (trigger → destination + status);
push narrative into the destination it points at.

Tool-specific overlays (e.g. a `CLAUDE.md` for Claude Code) layer *on top of*
`AGENTS.md` — they never replace it. The overlay holds only what's specific to that
tool (its slash commands, its hooks, its auto-loaded memory); shared truth stays in
`AGENTS.md` and the files it routes to.

## Session bootstrap — reading order on every resume

A new session has zero conversational context. Read in this order **before acting**:

1. **`CURRENT_STATUS_AND_NEXT_STEPS.md`** — operational state: what's active,
   blockers, exact next commands. **Always.** This is where you are right now.
2. **`project-memory/decisions.md`** — only if the task involves an architectural /
   threshold / scope choice. Prevents re-litigating decisions already measured against.
3. **`project-memory/architecture.md`** — only if touching invariants (structural
   shape, contract boundaries, what must not change).
4. **`project-memory/experiments.md`** — only if running or interpreting evals /
   baselines / calibration.

The conditional reads (2–4) are deliberate: loading all memory every session burns
context on rationale you don't need for the task at hand. Read the dashboard always;
reach for the durable layers only when the task type calls for them.

## Why this beats keeping it all in context

The context window is a cache, not storage: it's lossy (summarized under pressure),
volatile (gone on `/clear` or a crash), and finite (fills as work grows). Anything
that must survive those three failure modes belongs on disk. The dashboard +
durable memory are that disk; bootstrap is how a cold start re-warms the cache from
it.
