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

## Step 4 — preserve the trail

`CURRENT_STATUS_AND_NEXT_STEPS.md` is replaceable operational state. Rewrite its
current-state and next-action sections so a cold session can resume quickly; link
to closeout docs, `project-memory/*`, diagnostic artifacts, or git history for
older detail.

For `project-memory/*`, when superseding a prior entry, do not silently delete it.
Mark it `SUPERSEDED` with an absolute date, the trigger, and a forward pointer to
the replacement. Future sessions need to reconstruct why the decision changed.

When relaxing an architectural invariant, leave the new rule in `architecture.md`
and record the reopening / rejection rationale in `decisions.md` if it is likely
to be re-argued.

## Step 5 — confirm before writing

Before editing, briefly summarize to the user:

- Which files you will update.
- One bullet per file: what entry you will add or change.
- Anything borderline, such as a decision that might not be load-bearing enough
  for durable memory.

Wait for confirmation unless the user explicitly asks to proceed without it, asks
for a direct edit, or asks to commit / push as part of the same request.

## Step 6 — verify the writes

After writing, run `git diff` on the updated files and confirm:

- No accidental deletions.
- No duplicated content between `CURRENT_STATUS_AND_NEXT_STEPS.md` and
  `project-memory/*`.
- Each new durable entry has the fields its file requires (`Why:` /
  `How to apply:` / evidence pointer, as applicable).
- Stale related docs or router rows found in the sweep were updated, or explicitly
  left unchanged for a stated reason.

## Step 7 — cold-resume sufficiency check

The protocol's promise is that a fresh session can continue from the resume
entrypoints. Audit `CURRENT_STATUS_AND_NEXT_STEPS.md` and `AGENTS.md` as if you had
zero prior context. For the documented next code action, answer these six
questions using only those two files, allowing one-hop reads to explicitly named
spec sections, memory entries, artifacts, or code modules:

1. **What is the next action?**
2. **Which code files / functions should be touched?**
3. **Which spec sections should be read?**
4. **What prior phase / module / artifact should be consumed?**
5. **What is deferred or out of scope?**
6. **Which sanity-check commands, commit hashes, test counts, or numeric verdicts
   need current verification?**

For each answer, note where it lives. If any answer is missing or requires a
multi-hop chase, fix the checkpoint before declaring it complete.

Any numeric claim in the next-session entry must be checked against live state:

- If it cites a test count, run the command and confirm the count.
- If it cites a commit hash, confirm it is reachable from `HEAD`.
- If it cites a verdict or artifact value, reopen the artifact and confirm it
  still says the same thing.

If re-running an expensive command is not reasonable, mark the numeric claim as
not re-verified and explain the risk in the final report. Do not leave stale
numbers looking current.

## Step 8 — report

State, explicitly: which files were updated, which were swept and intentionally left
unchanged, and whether anything is still open for the next session. That report is
itself part of the cold-start handoff.

Include the cold-resume sufficiency verdict: which of the six questions are
answered directly, which require a named one-hop read, which numeric claims were
checked, and any resume gap fixed during the checkpoint.

## What does NOT go here

- Long-form retrospectives → git history / a closeout doc, not memory.
- Eval log dumps → run artifacts, not `experiments.md` (record only the number that
  affects a threshold/baseline/closure).
- Anything derivable from the code or `git log` — memory holds the *why*, the code
  holds the *what*.
