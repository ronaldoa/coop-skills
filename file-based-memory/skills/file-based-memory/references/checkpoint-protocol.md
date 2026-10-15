# Checkpoint protocol

The reader is the next session, with zero context — not a human wanting a recap. Every
claim must be actionable from a cold start. `/file-based-memory:save-status` runs this.

## 1. Decide what changed — a no-op checkpoint produces zero diffs

| File | Update when |
|---|---|
| dashboard (single mode) | active item, blockers or next commands changed; a landed commit worth surfacing |
| line doc `§0.0` + its dashboard row (multi-workline) | that line moved — rewrite the block in place with its fixed fields ([worklines.md](worklines.md)); never edit another line's block |
| `architecture.md` | an invariant confirmed, or relaxed (record why; if likely re-argued, also `decisions.md`) |
| `decisions.md` | an approach tried and rejected; a non-obvious tradeoff |
| `experiments.md` | a baseline ran, a regression was caught, a calibration changed with a measurement |

Also sweep for docs and router rows this session made stale (pointers, status labels);
fix them or say the sweep found none. Don't touch a file to bump a timestamp, and don't
copy content between the dashboard and `project-memory/` — each fact has one home.

A rule that proved durable this session is **promoted** into the repo (router,
principles file, line doc) and its personal-memory copy deleted — never kept in both.

## 2. Confirm before writing

List the files and one bullet per entry you will add or change, flag anything borderline,
and wait — unless the user asked for a direct edit or a commit in the same request.

## 3. Cold-resume sufficiency check

Using only the dashboard (or the line's `§0.0`) and `AGENTS.md`, plus one-hop reads to
sections they name explicitly, answer:

1. What is the next action?
2. Which files / functions does it touch?
3. Which spec sections must be read first?
4. Which prior artifact or module does it consume?
5. What is deferred or out of scope?
6. Which commands, hashes, counts or verdicts need re-checking?

Any answer missing, or needing a multi-hop chase ⇒ fix the checkpoint before calling it done.

## 4. Re-verify every number you leave behind

A test count is re-run, a hash confirmed reachable from `HEAD`, a verdict re-read from its
artifact — or the claim is marked **not re-verified** with the risk stated. Stale numbers
must never look current. (Prefer a *query* over a value where possible: `git log -1 --
<file>` instead of a pasted hash.)

## 5. Report

Files updated · files swept and left unchanged · what is open · the six-question verdict
(direct / one-hop / gap fixed) · which numbers were re-checked.

## Not here

Retrospectives (→ git history or a closeout doc), eval dumps (→ run artifacts), anything
derivable from code or `git log`.
