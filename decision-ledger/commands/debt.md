---
description: File, update or close an entry in the single debt register, with an id-collision check
argument-hint: [new <one line> | close D-<n> | update D-<n>]
---

Maintain `docs/DEBT_REGISTER.md` (or `$LEDGER_DEBT_FILE`) by the rules in its own header
and the `decision-ledger` skill's `references/debt-register.md`. If the register does not
exist, ask before creating it from `templates/DEBT_REGISTER.md.tmpl`.

- **new**: search that it isn't already filed → run the collision protocol → write the
  entry and its row in the index table → give plans that mention it a one-line `→ D-<n>`.
- **close / update**: change the entry and its index row together; a reclassification
  carries its reason; a close carries the commit and the verifying reading.

Then run `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/ledger_check.py`, show the diff, and commit
only if asked, with an explicit path list.
