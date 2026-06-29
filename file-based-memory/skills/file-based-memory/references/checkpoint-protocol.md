# Checkpoint protocol

The on-demand checkpoint (the `/file-based-memory:save-status` command runs this).
You are creating a **resume-ready checkpoint for a reader with zero context** — the
next session — not a human session recap. Every claim must be actionable from a cold
start.

## Step 1 — survey what changed this session

Before writing anything, gather:

1. `git status` — what's uncommitted.
2. `git log --oneline -20` — what landed.
3. The conversation: what was tried, what was decided, what was rejected.
4. A related-docs sweep: any doc / router entry made stale by this session's work
   (stale pointers, wrong status markers, superseded references). Fix those in the
   same checkpoint, or explicitly state the sweep found nothing to update.

## Step 2 — decide which files to update

Update only what genuinely changed. **A no-op checkpoint produces zero diffs** —
don't touch a file just to bump a timestamp.

| File | Update when |
|------|-------------|
| `CURRENT_STATUS_AND_NEXT_STEPS.md` | active item changed; blockers shifted; the next concrete commands changed; a new commit worth surfacing landed |
| `project-memory/architecture.md` | a new invariant was confirmed, or a previous one relaxed (record why) |
| `project-memory/decisions.md` | an approach was tried and rejected; a non-obvious tradeoff was made; "don't do X because Y" |
| `project-memory/experiments.md` | a new eval/baseline ran; a regression was caught; a calibration value changed with measurement |

## Step 3 — write to discipline

- **Resume-ready, not summary.** Concrete paths, exact commands, numbers. Not
  "made progress on retrieval".
- **Obey the size cap** (5–10 lines/entry) — link to the canonical doc instead of
  compressing it into memory. See [memory-model.md](memory-model.md).
- **Supersede, don't delete** stale entries. See [supersede-trail.md](supersede-trail.md).
- **Lead with the rule, then `Why:` and `How to apply:`** for durable entries.

## Step 4 — report

State, explicitly: which files were updated, which were swept and intentionally left
unchanged, and whether anything is still open for the next session. That report is
itself part of the cold-start handoff.

## What does NOT go here

- Long-form retrospectives → git history / a closeout doc, not memory.
- Eval log dumps → run artifacts, not `experiments.md` (record only the number that
  affects a threshold/baseline/closure).
- Anything derivable from the code or `git log` — memory holds the *why*, the code
  holds the *what*.
