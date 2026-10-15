# Growing your own principles ledger

`ENGINEERING_PRINCIPLES.md` here is a **snapshot of one project's ledger**, not a
standard. Adopt it whole, or start your own from `templates/ENGINEERING_PRINCIPLES.md.tmpl`
and grow it by the same rules. The rules matter more than the content: they are why the
file stayed readable at 300+ lines while being loaded every session.

## The rules

1. **Every principle carries an instance it paid for.** An italic line naming the real
   defect. A principle with no instance is an opinion and gets argued away; the instance is
   what lets a reader judge the edge cases.
2. **Map before adding: duplicate / complement / conflict.** Most "new" principles are a
   clause missing from an existing one and land better inside it. The same check catches
   the inverse error — citing a clause nobody wrote.
3. **A line ceiling, enforced by a check, with zero headroom.** Set the ceiling to the
   file's current length, so the next addition must displace something. "Is this worth more
   than what it replaces?" is the question an unbounded file never asks. `hooks/ceiling_check.py`
   enforces any file that declares `Ceiling: N lines` in its first ten lines.
4. **Stable §-IDs.** Code comments and docs cite `§1.5`; never renumber. Merged sections
   keep their id with a note ("absorbed §3.4").
5. **Portable vs local, in two files.** The principles file holds rules that would hold in
   any project; the router (`AGENTS.md` / `CLAUDE.md`) holds this project's standing rules
   and points at the principles. A local rule that turns out general moves to the
   principles file with its instance.
6. **Promote from memory, then delete the memory.** A personal-memory entry that keeps
   proving true is promoted into the repo (router or principles) and the memory entry is
   reduced to "promoted to <file> on <date>". Two copies drift.
7. **Prose is the weak form.** When a principle can be checked, add the check and name it
   next to the principle; when it cannot, say so ("this one is a review question").
8. **Absolute dates, quoted rulings.** "User ruling 2026-08-03: '<quote>'", never "recently".

## What to promote from personal memory

Run through the memory index periodically and sort every entry:

| Entry kind | Destination |
|---|---|
| true in any project, with an incident | principles file (merge into an existing § if possible) or `agent-ops.md`-style field rules |
| true in this project, every session | the router's standing rules |
| an entry point into a line of work | stays in memory as **one pointer line** to that line's handoff |
| a fact about the environment that changes (ports, which source is live) | stays in memory, dated, with the probe that re-checks it |
| already in the repo | delete from memory |

## Syncing a snapshot

The copy shipped in this plugin records its origin in `SKILL.md`. To refresh it from the
origin repo: `diff <origin>/ENGINEERING_PRINCIPLES.md references/ENGINEERING_PRINCIPLES.md`,
copy, bump the plugin version. Don't edit the snapshot in place — edit the origin and copy.
