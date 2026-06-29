---
description: Checkpoint engineering state across CURRENT_STATUS_AND_NEXT_STEPS.md + project-memory/ for a resumable, cold-start handoff
argument-hint: [optional one-line summary of what changed this session]
---

Create a **resume-ready checkpoint** for the next session, which has zero
conversational context. This is not a human session summary — every claim must be
actionable from a cold start.

Follow the checkpoint protocol in the `file-based-memory` skill
(`references/checkpoint-protocol.md`). Execute the full protocol, not just the
summary below.

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

## Step 4 — confirm before writing

Before editing, briefly summarize:

- Which files will be updated.
- One bullet per file: what entry will be added or changed.
- Any borderline item that might not be load-bearing enough for durable memory.

Wait for confirmation unless the user explicitly asked to proceed without it.

## Step 5 — verify the writes

After editing, run `git diff` on the updated files and confirm:

- No accidental deletions.
- No duplicated content between the dashboard and durable memory.
- New durable entries include the expected `Why:` / `How to apply:` structure.

## Step 6 — cold-resume sufficiency check

Audit `CURRENT_STATUS_AND_NEXT_STEPS.md` + `AGENTS.md` as if you had zero prior
context. For the documented next action, answer these six questions using only
those two files, allowing one-hop reads to explicitly named docs / memory entries /
code modules:

1. What is the next action?
2. Which code files / functions should be touched?
3. Which spec sections should be read?
4. What prior surface should be consumed?
5. What is deferred or out of scope?
6. Which sanity-check commands / numeric claims need current verification?

If any answer is missing or requires a multi-hop chase, fix the checkpoint before
declaring it done.

Any test count, commit hash, or numeric verdict in the next-session entry must be
re-checked against live state, or explicitly marked as not re-verified.

## Step 7 — report

List which files were updated, which were swept and left unchanged, and what's still
open for next session. Include the cold-resume sufficiency verdict and any numeric
claim checks.
