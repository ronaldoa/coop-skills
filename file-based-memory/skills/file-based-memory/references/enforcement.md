# The precommit gates

Advisory size and format rules get skipped under context pressure; these run before every
agent-issued `git commit` / `git push` (`PreToolUse(Bash)` → `hooks/doc-budget-precommit.sh`)
and block with exit 2. They do **not** run on human commits — for those, wire the same
scripts into a git hook (and remember `core.hooksPath` is not present on a fresh clone,
[doc-index.md](doc-index.md) §6).

## Doc-budget gate — `hooks/doc_budget_check.py`

- **Per-entry caps** on `project-memory/*` `## ` entries (`## [FOLDED]` entries get the
  larger folded cap).
- **Router line cap** on `AGENTS.md` — one route = one line.
- **Whole-file budgets** — catch creep per-entry checks miss.

Delta-scoped so legacy debt never blocks: only files that differ from `HEAD`; within memory
files only new or modified entries; in `AGENTS.md` only added lines. Tune `FILE_BUDGETS`,
`LINE_CAPS`, `ENTRY_CAPS` at the top of the script. Bypass: `DOC_BUDGET_BYPASS=1` on the
command, with the reason in the message.

## Doc gates — `hooks/doc_gates.py`

On changed docs under `DOC_GATES_DIRS` (default `docs`):

| Gate | Checks | Why |
|---|---|---|
| G1 | `> STATUS: <status> · <date> · <line>` in the first 20 lines, status in `DOC_GATES_STATUSES` (empty = any) | the index is derived from stamps |
| G2 | ≤ 1 live heading containing `DOC_GATES_ENTRY_MARKER` (default `START HERE`) not marked `[SUPERSEDED` | one plan once had five "start here" markers |
| G3 | every `` `path#symbol` `` resolves: among repo files ending with `path`, exactly one contains the symbol | dead / ambiguous pointers go red |
| G4 | no newly added `file.ext:NN` pointer | line numbers drift silently |

`DOC_GATES_EXEMPT` defaults to `INDEX.md,README.md`. `python3 hooks/doc_gates.py --all`
audits every doc once when adopting — expect unstamped docs; fix them when touched. Bypass:
`DOC_GATES_BYPASS=1`. Criteria: `tests/test_doc_gates.py` — each gate has a clean and a
broken case, each mutation-checked to go red on its own arm.

## Dropping a gate

Remove the matching line from `hooks/doc-budget-precommit.sh`, or the whole `PreToolUse`
block from `hooks/hooks.json`. The cadence hook works without them.
