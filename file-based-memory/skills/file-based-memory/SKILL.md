---
name: file-based-memory
description: Set up and operate a persistent, resumable file-based memory for a repository so an agent can cold-start with zero conversational context. Use when bootstrapping a new repo's agent memory, when asked to checkpoint/resume engineering state, or when work spans multiple sessions and goals risk drifting as context fills.
when_to_use: bootstrap agent memory; checkpoint state before /clear or end of session; resume cold with no chat history; stop goal-drift across long tasks; several parallel work threads each needing its own handoff; "save status", "where were we", "set up project memory", "write the handoff block"
---

# File-Based Memory

The disk is the source of truth; context is a cache. Four artifacts, each with a
different decay rate:

| Artifact | Decay | Holds |
|---|---|---|
| `AGENTS.md` (router) | rare | where things are — routes to truth, **never stores it** |
| `CURRENT_STATUS_AND_NEXT_STEPS.md` (dashboard) | per session | what's active, blockers, exact next commands |
| `project-memory/{architecture,decisions,experiments}.md` | indefinite | invariants · approaches tried and rejected · numbers that set a baseline |
| personal memory (optional) | indefinite | the user's preferences, and one pointer per line of work |

Two laws:

1. **Truth vs index.** The router and dashboard point; they never become a second copy.
2. **Supersede, don't delete** durable entries — [references/supersede-trail.md](references/supersede-trail.md).

## Where each rule lives

| Task | Read |
|---|---|
| bootstrap a repo | `/file-based-memory:bootstrap` |
| resume: reading order, router philosophy | [references/bootstrap.md](references/bootstrap.md) |
| checkpoint at session end | [references/checkpoint-protocol.md](references/checkpoint-protocol.md) (`/file-based-memory:save-status` runs it) |
| what may enter each memory file, size caps | [references/memory-model.md](references/memory-model.md) |
| several parallel lines of work | [references/worklines.md](references/worklines.md) + `templates/WORKLINE.md.tmpl` |
| more than a few dozen docs | [references/doc-index.md](references/doc-index.md) |
| rebuild or audit `AGENTS.md` | [references/agents-rebuild.md](references/agents-rebuild.md) |
| the precommit gates and their config | [references/enforcement.md](references/enforcement.md) |

User rulings, open questions and the debt register belong to the companion
`decision-ledger` plugin; `decisions.md` here keeps *approaches tried and rejected with
evidence*.

## Hooks

- `Stop`: `hooks/save-status-cadence.sh` nudges a checkpoint after `SAVE_STATUS_CADENCE`
  commits (default 5; `0` disables) since `CHECKPOINT_FILE` (default
  `CURRENT_STATUS_AND_NEXT_STEPS.md`) was last touched. Never blocks.
- `PreToolUse(Bash)` on `git commit`/`push`: the doc-budget gate and the doc gates —
  [references/enforcement.md](references/enforcement.md).
