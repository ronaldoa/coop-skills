# Multi-workline mode

Single-dashboard mode breaks once a repo carries several long-running lines of work, each
resumed by a different (sometimes parallel) session: one dashboard becomes sections nobody
owns, or one line overwrites another's state. Multi-workline mode changes only the
operational layer:

| Single mode | Multi-workline mode |
|---|---|
| one dashboard holds the handoff | **each line's design doc holds its own handoff block** (`§0`) |
| dashboard = state | dashboard = **router of active lines** (one row per line → its `§0`) |
| `/save-status` rewrites the dashboard | `/save-status <line>` rewrites **that line's** `§0` + its router row |

Switch when a second line needs its own "next step" that the first line's reader
should not have to read past.

## A line = one design doc that owns its own handoff

```
docs/<LINE>_PLAN.md            ← or _DESIGN.md; one per line
  > STATUS: in-flight · 2026-10-15 · <one line>      ← doc-index stamp (doc-index.md)
  ## 0. Session handoff — START HERE                 ← the ONLY live entry marker
  ### 0.0 Handoff block (2026-10-15 close)           ← rewritten every session
  ### 0.1 … (rulings / design order that a resumer must not re-argue)
  ## 1. … the design proper (stable §-numbers; never renumber)
```

Template: `templates/WORKLINE.md.tmpl`.

### The handoff block has a fixed shape

Open with the fields that tell a cold reader **whether the environment is broken**
before anything else, then the work:

1. **HEAD** — a *query*, not a hash you typed: `git log --oneline -1 -- docs/<LINE>.md`
   (a pasted hash is stale the moment another session commits).
2. **Baseline** — the test command(s) and the count they printed *this session*
   (`271 passed`), the type-check result, and what this line spends (LLM calls, quota,
   DB writes — "zero LLM, zero code" is a valid and useful baseline).
3. **Files of this line** — which doc/section owns which concern (one line each).
4. **Progress** — against the plan's own slice list; name the status rung honestly
   (proposed / recommended / ruled / landed / verified — see decision-ledger).
5. **Next step** — one concrete action, with the files it touches and what to read first.
6. **Carried holes** — a table: *hole · affected cases · current exit (what happens today)
   · who/when it gets decided*. A hole without an exit is a silent default waiting to happen.
7. **🛑 Do-not list** — the mistakes this line already paid for, one line each, with the
   reason. This is the highest-value section for the next session.
8. **Out of this line** — work handed to another line, with its pointer.

**Size cap: the block fits on two screens.** Detail goes into the numbered sections or
into git history; the block points. A handoff that needs scrolling is a second design doc.

### Exactly one live entry point per doc

When a new handoff is written, the old one is **demoted** (rename its heading to
`[SUPERSEDED <date> → §0.0]`), not left beside it. *Measured rot: one plan once carried
five "start here" markers of four vintages; the oldest, 700 lines above the real one,
said "no need to read anything else".* `hooks/doc_gates.py` enforces "≤ 1 live entry
marker per doc".

### Line closure

A finished line gets `STATUS: DONE · <date> · <one line>`, a final handoff saying
**where the residue went** (debt-register ids, another line), and then stops receiving
appends. Residual work is not kept alive inside a DONE doc.

## The router row and the personal-memory pointer

The dashboard (`CURRENT_STATUS_AND_NEXT_STEPS.md`) becomes a table:

| Line | Doc → handoff | Status | Next step (one line) | Last close |
|---|---|---|---|---|

If the agent also has a personal / auto-memory index (e.g. Claude Code's
`MEMORY.md`), give each line **one pointer line** there — "X line entry → read
`docs/X.md` §0.0" — and nothing more. Rules that turn out to be durable are
**promoted** into the repo (`AGENTS.md`, a principles file, the doc) and the memory
entry is deleted or reduced to "promoted to <file>, don't rebuild it here". Memory that
copies the repo is a mirror and will drift.

## Commit log as the progress log

The handoff block points at git instead of retelling history, so commit subjects must
be greppable. A small, fixed prefix vocabulary works (example set, adapt freely):

| Prefix | Meaning |
|---|---|
| 📐 | design / spec change |
| 📝 | draft awaiting a ruling |
| ⚖️ | records a user ruling (quote it) |
| 🤝 | handoff-block update only |
| 📏 / 📊 / 🧪 | measurement / reading / experiment (state cost: calls spent) |
| 🔎 | diagnosis, no fix |
| ✨ / 🩹 / 🔧 | feature / fix / instrument |
| 🗑️ | deletion |
| ✅ | closes a debt id or slice |

End the subject with the **cost tag** — `(zero LLM, zero code)`, `(208 calls, 0 errors)` —
so "what did this cost / did this run anything" is answerable from `git log` alone.
Progress query: `git log --oneline --grep='<LINE-ID>'`.

## When multiple sessions share one worktree

The handoff discipline is useless if parallel sessions' commits swallow each other's files.
The field rules (explicit path-list commits, private worktrees for production edits, "a
clean snapshot is never a premise") live in the `engineering-discipline` plugin's
`agent-ops.md` §A.
