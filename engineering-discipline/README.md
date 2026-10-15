# engineering-discipline

The rules, not the memory substrate. Packaged as a Claude Code plugin; companion to
`file-based-memory` (where state lives) and `decision-ledger` (who decided what).

- `references/ENGINEERING_PRINCIPLES.md` — verbatim snapshot of the origin project's
  principles (§1 verification · §2 contracts and LLM vs code · §3 measurement · §4
  troubleshooting · §5 workflow · §6 scope), each rule with the defect that paid for it.
- `references/agent-ops.md` — field rules distilled from that project's personal memory:
  parallel sessions on one worktree, processes and env precedence, test instruments, paid
  calls, claims and reports, two machines, LLM-application design rulings.
- `references/growing-a-principles-ledger.md` — how to grow your own: instance per rule,
  map before add, enforced zero-headroom ceiling, stable §-IDs, promote from memory then
  delete the memory.
- `/engineering-discipline:promote-memory` — sort a memory directory into repo rules,
  pointers and deletions (presents a table, edits only after a ruling).
- `hooks/ceiling_check.py` — files declaring `Ceiling: N lines` may not exceed N.
  Criteria: `python3 -m unittest discover -s engineering-discipline/tests`.

## License

MIT.
