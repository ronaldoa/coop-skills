# decision-ledger

Who decided what, on disk. Packaged as a Claude Code plugin; companion to
`file-based-memory`.

- **Rulings vs recommendations** — the user's decisions recorded verbatim, dated, with
  what they decide / overturn / close; the agent's recommendations never written as settled.
- **Status ladder** — proposed → recommended → ruled → landed → verified; reports never
  round up.
- **Open-question register** — `### Qn [OPEN|RULED <date>|PARKED <date>]` per line doc;
  carried holes are never filled with defaults.
- **Debt register** — one file, stable `D-<n>` ids, never reused, closed entries kept,
  collision protocol for parallel sessions.
- **Ledger gate** (`hooks/ledger_check.py`, run before agent commits): L1 each debt id has
  exactly one entry and one index row; L2 no `Qn (open)` citation of a ruled question.

## Use

- `/decision-ledger:ruling [Q-id]` — record the ruling just made
- `/decision-ledger:debt new … | close D-n | update D-n`
- Config: `LEDGER_DEBT_FILE` (default `docs/DEBT_REGISTER.md`) · `LEDGER_DIRS` (default `docs`) · bypass `LEDGER_BYPASS=1`
- Criteria: `python3 -m unittest discover -s decision-ledger/tests` (each arm mutation-checked)

## License

MIT.
