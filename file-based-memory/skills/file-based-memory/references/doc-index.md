# The doc index: status stamps, stable paths, pointers that fail loudly

Once `docs/` passes a few dozen files, a directory tree stops being navigation and the
router (`AGENTS.md` → "Design Specs") can no longer list everything. The pattern that
scaled to 200+ docs:

## 1. Status lives in the doc, the index is derived

Every doc opens with one stamp line in three parts:

```
> STATUS: <status> · <YYYY-MM-DD> · <one sentence: what this doc is / where it stands>
```

Status vocabulary (adapt, but keep it closed):
`in-flight` (has an unfinished next step) · `active` (maintained, never "done") ·
`not-started` · `rejected` (conclusion = don't build) · `DONE` · `ratified`
(conclusion doc) · `reference` · `stale` · `undetermined`.

`docs/INDEX.md` is **generated from the stamps**, not hand-edited. Change a status by
editing the doc's stamp, then regenerate. A doc with no stamp lands in
`undetermined` — **never guess a status**: a wrong status looks like a conclusion,
which is worse than no status. (A first version that guessed from keywords filed a
pure API reference as "in-flight".)

If you add a generator, make its default mode **reconcile, not rewrite**: list rows
that disagree with stamps, docs without a stamp, malformed stamps, docs missing from
the index; rewrite a row only when that doc is named (`--apply FOO.md`). A whole-table
regenerate destroys hand-added rows that are newer than their stamps.

`hooks/doc_gates.py` checks the stamp's shape on every changed doc.

## 2. Topic indexes, not folders

Group docs by **topic index pages** (`SEC_INDEX.md`, `EVALUATION_INDEX.md` …) linked
from `INDEX.md`'s "how to use" section, instead of moving files into folders.
**Never move or rename a doc that code comments point at** — those pointers break
silently (no compiler, no grep warning). Track the count of in-code references per doc
in the index so the cost of a move is visible.

## 3. Pointers into code: `path#symbol`, never `path:line`

```
good:  `server/agent/conversation.ts#applyTurnTransition`
bad:   server/agent/conversation.ts:412
```

The failure modes differ: a drifted line number **still resolves** — to the wrong code,
silently. A renamed or deleted symbol makes the pointer check go **red**.
`hooks/doc_gates.py` verifies that every `` `path#symbol` `` names an existing file
that contains that symbol, and rejects newly added `path.ext:NN` pointers. (It buys
"silent → loud", not correctness: a grep cannot prove the symbol is the thing the prose
means.)

## 4. Cross-document section references carry the file name

Inside a doc, `§3.2` means this doc. Anywhere else, write `` `FILE.md` §3.2 ``.
Never renumber a doc's sections once other docs cite them — append a section and point.

## 5. Debt is not in the index

Known defects live in one register with stable ids (see the `decision-ledger` plugin);
plans carry a one-line pointer (`→ DEBT_REGISTER D-42`), never a copy of the entry.

## 6. The gates need a trigger

Doc checks only run if something runs them. If the repo has no CI, a git hook is the
only automatic trigger, and `core.hooksPath` is local config that a fresh clone does
not have:

```
git config core.hooksPath .githooks   # install
git config core.hooksPath             # check — empty output = gates run only when someone remembers
```

This plugin's `PreToolUse` hook runs the gates before any agent-issued `git commit`,
which covers agent commits but not human ones.
