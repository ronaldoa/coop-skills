---
name: file-based-memory
description: Set up and operate a persistent, resumable file-based memory for a repository so an agent can cold-start with zero conversational context. Use when bootstrapping a new repo's agent memory, when asked to checkpoint/resume engineering state, or when work spans multiple sessions and goals risk drifting as context fills.
when_to_use: bootstrap agent memory; checkpoint state before /clear or end of session; resume cold with no chat history; stop goal-drift across long tasks; "save status", "where were we", "set up project memory"
---

# File-Based Memory

Externalize the things a context window loses: route via one entrypoint, keep a
replaceable operational dashboard, and protect a small durable memory of *why*.
The disk is the source of truth; context is a cache.

This is the file-based-planning discipline (a "Manus-style" / planning-with-files
lineage — see [references/prior-art.md](references/prior-art.md)) generalized into
a reusable, repo-agnostic kit. It is **not** a domain skill; it sets up and
operates the memory substrate any other work sits on.

## The model in one screen

Four artifacts, each with a different decay rate and audience:

| Artifact | Decay | Audience | Holds |
|---|---|---|---|
| `AGENTS.md` (router) | rare | any agent, first contact | where things are; routes to truth, **does not store it** |
| `CURRENT_STATUS_AND_NEXT_STEPS.md` (dashboard) | per-session | "me, next session" | what's active, blockers, exact next commands |
| `project-memory/{architecture,decisions,experiments}.md` | quarters→indefinite | anyone changing the system | invariants, rejected approaches, measurement trail |
| user-/personal memory (optional) | indefinite | you across repos | your preferences, not repo facts |

Two laws hold the whole thing together:

1. **Truth vs index are separate.** The router and dashboard *point at* truth
   (code, docs, the memory files). Don't let the index become a second, drifting
   copy of the truth. See [references/bootstrap.md](references/bootstrap.md).
2. **Supersede, don't delete.** A wrong/old entry is marked SUPERSEDED with a
   pointer to what replaced it, not silently removed — the trail is the value.
   See [references/supersede-trail.md](references/supersede-trail.md).

## When this skill applies

- **Bootstrap**: a repo has no agent-memory scaffold → install the templates.
- **Checkpoint**: end of a work session, or before `/clear` / a context reset →
  run the checkpoint protocol so the next cold start is actionable.
- **Resume**: new session, zero chat history → read in bootstrap order, then act.

## Bootstrap a repo (first time)

The `/file-based-memory:bootstrap` command runs this on demand. Copy the templates into
the target repo root, then fill the placeholders:

```
templates/AGENTS.md.tmpl                      -> AGENTS.md
templates/CURRENT_STATUS.md.tmpl              -> CURRENT_STATUS_AND_NEXT_STEPS.md
templates/project-memory/README.md.tmpl       -> project-memory/README.md
templates/project-memory/architecture.md.tmpl -> project-memory/architecture.md
templates/project-memory/decisions.md.tmpl    -> project-memory/decisions.md
templates/project-memory/experiments.md.tmpl  -> project-memory/experiments.md
```

Do **not** invent content to fill them — leave a placeholder and a TODO where you
don't yet know the answer. An honest empty section beats a confident wrong one.

`AGENTS.md` is the **handbook** layer: reconstructible from its sources (README, build
manifest, env template, source tree, `docs/`), so it's allowed to be lossy in a way the
durable memory is not. To rebuild it from zero, audit a section against its source of
truth, or build the `docs/` router with an Explore subagent, see
[references/agents-rebuild.md](references/agents-rebuild.md) — section-by-section
recipe + the route-don't-store rule for what belongs in the router vs the layer above.

## Session bootstrap (every resume)

Read in this order before acting (full rationale in
[references/bootstrap.md](references/bootstrap.md)):

1. `CURRENT_STATUS_AND_NEXT_STEPS.md` — what's active, blockers, next commands. **Always.**
2. `project-memory/decisions.md` — only if the task involves an architectural /
   threshold / scope choice (avoids re-litigating measured decisions).
3. `project-memory/architecture.md` — only if touching invariants.
4. `project-memory/experiments.md` — only if running or interpreting evals.

## Checkpoint protocol (the `/save-status` analogue)

You are writing a **resume-ready checkpoint for a reader with zero context**, not
a human session recap. Full protocol in
[references/checkpoint-protocol.md](references/checkpoint-protocol.md); the shape:

1. **Survey** what changed: `git status`, `git log --oneline -20`, and what was
   tried / decided / rejected this session.
2. **Update only what genuinely changed.** A no-op checkpoint produces zero diffs.
   - dashboard: active item, blockers, next concrete commands moved
   - `architecture.md`: a new invariant confirmed, or one relaxed (record why)
   - `decisions.md`: an approach tried and rejected, a non-obvious tradeoff
   - `experiments.md`: a baseline/eval run, a regression, a calibration change
3. **Obey size discipline** (see below) — link to docs, don't compress them in.
4. **Supersede, don't delete** stale entries.

The `/file-based-memory:save-status` command runs this protocol on demand.

## Size discipline — memory is an index + anti-pitfall summary, not compressed docs

The one rule that stops `project-memory/` from becoming a second copy of `docs/`:

- **Per-entry cap: 5–10 lines.** More than that means you're rewriting a spec —
  write the conclusion + a link to the canonical doc instead.
- **Admission filter:**
  - `architecture.md`: admit only if forgetting it would cause a *wrong code change*.
  - `decisions.md`: admit only if the question is *likely to be re-argued* AND a
    reason for rejection was recorded with measurement / incident.
  - `experiments.md`: admit only if the number affects a *threshold/baseline/closure*.
- **Lead with the rule, then `Why:` and `How to apply:`** so a reader months later
  can judge edge cases.

This is optionally enforced by a precommit hook — see
[references/enforcement.md](references/enforcement.md).

## Auto-checkpoint cadence (the always-on nudge)

A non-blocking `Stop` hook (`hooks/save-status-cadence.sh`, registered in
`hooks/hooks.json`) counts commits landed since the dashboard was last touched and,
past a threshold, reminds you to checkpoint — the "2-action rule" made automatic.
It never blocks the turn and never loops. Configure via env:

- `SAVE_STATUS_CADENCE` — commit threshold (default 5; `0` disables)
- `CHECKPOINT_FILE` — dashboard filename (default `CURRENT_STATUS_AND_NEXT_STEPS.md`)

## Additional resources

- [references/bootstrap.md](references/bootstrap.md) — reading order + router philosophy (truth vs index)
- [references/agents-rebuild.md](references/agents-rebuild.md) — rebuild `AGENTS.md` from its sources: per-section recipe, doc-router Explore survey, route-don't-store rule
- [references/checkpoint-protocol.md](references/checkpoint-protocol.md) — the full checkpoint protocol
- [references/memory-model.md](references/memory-model.md) — the four-layer model, decay rates, admission filters
- [references/supersede-trail.md](references/supersede-trail.md) — supersede-don't-delete rules
- [references/enforcement.md](references/enforcement.md) — optional precommit size-discipline gate
- [references/prior-art.md](references/prior-art.md) — lineage + attribution
