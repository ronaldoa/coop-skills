# The open-question register

## Format (one numbered section per line doc)

```
### Q24 [OPEN] <the question in one line>
- Options: (a) … — cost … · (b) … — cost … · (c) the user's earlier wording: "…"
- Recommended (agent): (a), because …
- Blocks: <slice / case ids>. Current exit until ruled: <what happens today>.

### Q13 [RULED 2026-10-14] <question>
⚖️ user "确认封闭" — <what it decides>. Landed: <commit or "not yet">.

### Q8 [PARKED 2026-10-12] <question> — revisit when <trigger>.
```

Ids are per doc and never reused; ruled and parked entries stay. Elsewhere cite
`Q24 (open)` or `` `FILE.md` Q24 (open) `` — the ledger gate turns those red once Q24 is ruled.

## Carried holes

An open question implementation will hit before it is ruled. Carry it in the line's
handoff table — *hole · affected cases · current exit · decided by / when* — and:

- no default fills it; code that must run first gives the undecided state a closed value
  (`unregistered`, `pending`), never `""`, `null` or the most common option;
- a case that depends on it is not reported as supported;
- "current exit" names what the user sees today — "falls into the nearest bucket" is a
  silent wrong answer and is itself a finding.

## Before you ask

1. Search this register and the ruling history (`git log --grep=⚖️`, the line's `§0.1`).
   Re-asking a ruled question costs trust; building on a stale "open" costs work.
   *(One day: an hour of work from a fossil "open" row, a question asked whose answer was
   in a debt entry, and a "pending" ruling reported that had been ruled the same day.)*
2. Questions with a unique correct answer are computed or measured, not asked.
3. Costs are numbers: "6 of 120 cases change, 2 user-visible", not "risky".
4. One round at a time; record each answer before opening the next.
