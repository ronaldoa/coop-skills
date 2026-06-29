---
description: Checkpoint engineering state across CURRENT_STATUS_AND_NEXT_STEPS.md + project-memory/ for a resumable, cold-start handoff
argument-hint: [optional one-line summary of what changed this session]
---

Create a **resume-ready checkpoint** for the next session, which has zero
conversational context. This is not a human session summary — every claim must be
actionable from a cold start.

Follow the checkpoint protocol in the `file-based-memory` skill
(`references/checkpoint-protocol.md`). In brief:

## Step 1 — survey

Gather before writing:
1. `git status` (uncommitted)
2. `git log --oneline -20` (what landed)
3. The conversation: what was tried, decided, rejected
4. A related-docs sweep: fix any pointer/status/reference made stale this session,
   or state the sweep found nothing.

If `$ARGUMENTS` is present, treat it as the focus hint; otherwise infer from context.

## Step 2 — update only what changed

A no-op checkpoint produces zero diffs.

| File | Update when |
|------|-------------|
| `CURRENT_STATUS_AND_NEXT_STEPS.md` | active item / blockers / next commands changed; a landed commit worth surfacing |
| `project-memory/architecture.md` | a new invariant confirmed, or one relaxed (record why) |
| `project-memory/decisions.md` | an approach tried and rejected; a non-obvious tradeoff |
| `project-memory/experiments.md` | a baseline/eval ran; a regression; a calibration change with measurement |

## Step 3 — discipline

- Resume-ready: concrete paths, exact commands, numbers.
- Size cap 5–10 lines/entry — link to the canonical doc, don't compress it in.
- Supersede stale entries (date + forward pointer + trigger), don't delete.

## Step 4 — report

List which files were updated, which were swept and left unchanged, and what's still
open for next session.
