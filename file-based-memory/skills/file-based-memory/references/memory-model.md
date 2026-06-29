# The four-layer memory model

Persistent engineering memory for a repository. Each layer has a distinct decay
rate and audience — that separation is the point. Collapse them and the fast layer
(operational state) pollutes the slow layer (durable rationale), or the slow layer
bloats into a re-statement of the docs.

| Layer | Decay | Audience | Purpose |
|------|-------|----------|---------|
| `CURRENT_STATUS_AND_NEXT_STEPS.md` | session | "me, next session" | what's active, blockers, exact next commands |
| `project-memory/architecture.md` | quarters | "anyone touching the system" | invariants, what NOT to change, structural shape |
| `project-memory/decisions.md` | indefinite | "future me / anyone proposing change" | rejected approaches with reasons; non-obvious tradeoffs |
| `project-memory/experiments.md` | indefinite | "anyone reading eval / regression results" | baselines, calibration history, measurement runs |

The dashboard lives at the repo **root** (high-visibility, first thing read). The
three durable files live in `project-memory/`. A router (`AGENTS.md`) sits above
all of them and only *points* — see [bootstrap.md](bootstrap.md).

## Reading order on session start

1. `CURRENT_STATUS_AND_NEXT_STEPS.md` — what's active right now. Always.
2. `decisions.md` — only if proposing an architectural / threshold / scope change.
3. `architecture.md` — only if touching invariants.
4. `experiments.md` — only if running or interpreting evals.

## Writing rules

- **Resume-ready, not human summary.** Concrete file paths, exact commands, numeric
  results. Not "we made progress on retrieval".
- **Append, then restructure.** New entries append; restructure when entries become
  stale or duplicative (and supersede — don't silently delete).
- **Lead with the rule, then `Why:` and `How to apply:`.** A reader six months from
  now needs the *why* to judge edge cases.
- **Don't duplicate the dashboard.** The dashboard is operational ground truth; the
  three durable files are the things that file would lose if rewritten.

## Size discipline — index + anti-pitfall summary, not compressed docs

The hard rule that keeps `project-memory/` from drifting into a second copy of `docs/`.

**Per-entry length cap: 5–10 lines.** If you find yourself writing more, you're
rewriting a spec — write the conclusion + a link to the canonical doc instead.

**Per-file admission filter:**

| File | Admit only if... |
|------|------------------|
| `architecture.md` | forgetting this rule would lead to a *wrong code change*. Not a system overview; not a "good to know". |
| `decisions.md` | the question is *likely to be re-argued*, AND a reason for rejection has been recorded with measurement / incident. |
| `experiments.md` | the number affects a *threshold / baseline / closure* judgment. Eval log dumps stay in run artifacts. |

**Worked example (generic).** When a subsystem's rules grow, the temptation is to
expand every case inline. Don't. Two short entries usually suffice:

- `architecture.md` — one invariant: *the high-precision layer owns X; broad
  coverage of variants is the next layer's job.*
- `decisions.md` — one rejected approach: *chasing every failing case in the
  high-precision layer (rejected — the downstream layer is the right surface).*
- A one-line pointer in either entry: `see docs/<area>.md` for the full rule.

If the spec moves, the spec moves. Memory points at it.

## Updating

Run the checkpoint protocol ([checkpoint-protocol.md](checkpoint-protocol.md), or
the `/file-based-memory:save-status` command) at the end of a working session to
checkpoint changes across all four layers.
