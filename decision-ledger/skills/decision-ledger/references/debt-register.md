# The debt register

One file (`docs/DEBT_REGISTER.md`, or `$LEDGER_DEBT_FILE`) holds every known defect and
debt. The rules themselves live in the file's own header (`templates/DEBT_REGISTER.md.tmpl`)
so every reader of the register sees them; this page adds what does not fit there.

## The collision protocol

Parallel sessions on one branch each read the same maximum and allocate the same id;
cross-references then point at someone else's entry and nothing goes red. *(Twice in one
day in the origin project; later once across two machines.)*

1. Immediately before writing, take the max id from the headings **and** the index — and
   the remote branch's register if there is a remote.
2. Commit the new entry promptly; the gap between reading the max and committing is the race.
3. On collision the first commit keeps the id; the later renumbers and opens with
   `originally D-xx, renumbered for collision` — older commit messages use the old id.
4. Run `ledger_check.py`: each id exactly one entry heading and one index row.

## Entry shape

```
### D-42 — <one-line statement of the defect>

🔴 OPEN · P1 · filed 2026-10-15
- Symptom (user-visible): …
- Reproduction / evidence: <command, case id, reading>
- Owner / where it gets fixed: <line doc § or "unassigned">
- History: <dated one-liners: reclassified, partly fixed, closed by <commit>>
```

The gate counts `### D-42`, `### D-42 — …` and `### D-42 … {#d-42}` as the entry; a
heading like `### D-42 measurements` is a subsection. The index is the first table after
`<a id="debt-index"></a>` — appending index rows to any other table splits the index
silently. *(Found on adoption: 129 rows had been appended to a table inside one entry's
body, so "read the index tail for the max id" returned a stale max.)*

## Closing

`✅ CLOSED <date>` + the commit + the verifying reading. "Closed by deleting the code path"
is a different claim from "fixed" — say which. Rank by user-visible harm: wrong numbers
returned silently outrank an empty result, which downstream notices.
