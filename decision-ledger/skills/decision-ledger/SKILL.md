---
name: decision-ledger
description: Record and track who decided what in a repository — the user's rulings (quoted verbatim, dated, with what they overturn), the agent's recommendations kept distinct from rulings, an open-question register, the honest status ladder from proposed to verified, and a single debt register with stable ids. Use when the user makes a call that should outlive the session, when presenting a decision that is the user's to make, when filing or closing known debt, or when resuming work that depends on earlier rulings.
when_to_use: the user just decided something ("go with A", "don't do X", "同意"); you need the user to choose between options; filing / closing a known defect or debt; before re-raising a question that may already be ruled; writing a handoff that cites decisions; "record this ruling", "is this decided?", "file a debt"
---

# Decision Ledger

Two kinds of decision look alike in a transcript and must never be confused on disk:
the agent's **recommendations** and the user's **rulings**. The expensive failure is a
recommendation written up as settled — the next session builds on it, and the user's
actual position, often one clause the restatement dropped, surfaces weeks later.

`project-memory/decisions.md` (file-based-memory) keeps *approaches tried and rejected
with evidence*; this ledger keeps *who decided what*. Neither copies the other.

## The status ladder — never report a higher rung than you hold

| Rung | Evidence | The lie one rung up |
|---|---|---|
| proposed | written down | "we're doing X" |
| recommended | the agent's argument, with reasons and costs | "we decided X" |
| **ruled** | a dated, verbatim user quote | "X is done" |
| landed | a commit | "X works" |
| verified | a real end-to-end run's reading, recorded | — |

Exits: `parked` needs a **trigger** to revisit (else it is a silent rejection);
`rejected` needs the **reason with evidence** (else it comes back in six months).
The rung belongs to each item, not the slice: "direction ruled on 9 items; none reached
*static check passes*" — not "slice ruled". Reports keep "not measured" as its own section.

## The rules, one line each — detail in one place

| Rule | Detail |
|---|---|
| Quote rulings **verbatim, in the user's language**, dated, with what they decide / overturn / close; a one-word ruling ("同意") is recorded with the options it answered | [rulings.md](references/rulings.md) |
| One home per ruling (the line doc, the question entry, or the router's standing rules); elsewhere a pointer — when you must restate to act, quote | [rulings.md](references/rulings.md) |
| Silence is not a ruling; a ruling does not extend by analogy to the next similar action | [rulings.md](references/rulings.md) |
| Open questions live in a numbered register per line doc: `### Qn [OPEN]` / `[RULED <date>]` / `[PARKED <date>]`; cited elsewhere as `Qn (open)` | [open-questions.md](references/open-questions.md) |
| Until ruled, a carried hole is never filled with a default; code represents it with a closed `unregistered` / `pending` value | [open-questions.md](references/open-questions.md) |
| Before asking: search for an existing ruling; give options with costs **as numbers**, recommended first, the other party's own words as an option | [open-questions.md](references/open-questions.md) |
| All known debt in one register, stable `D-<n>` ids, never reused; closed entries stay; reclassifying needs the reason; priority = user-visible harm | [debt-register.md](references/debt-register.md) |
| Check the current max id (and the remote's) immediately before allocating — parallel sessions collide; first commit keeps the id | [debt-register.md](references/debt-register.md) |

Commands: `/decision-ledger:ruling`, `/decision-ledger:debt`.

## The mechanical half

`hooks/ledger_check.py`, before agent-issued commits: **L1** every debt id has exactly one
entry heading and one index row; **L2** no `Qn (open)` citation of a question marked
`[RULED …]` or `[PARKED …]`, and none of a question that does not exist. It catches only
those shapes — a ruled question still listed as a "candidate" in prose is a human check.
