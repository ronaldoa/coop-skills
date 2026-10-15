---
description: Record the user's ruling from this conversation — verbatim quote, date, what it decides, what it overturns, which open question it closes — in its one home, and update every pointer to it
argument-hint: [optional Q-id or topic the ruling answers]
---

Follow the `decision-ledger` skill's `references/rulings.md` (format, placement,
overturning).

1. **Find the user's message** that decides it (`$ARGUMENTS` names the Q-id or topic;
   else the most recent decision). No user message ⇒ **stop**: an unobjected recommendation
   is not a ruling.
2. **Write it in its one home**, verbatim, with the options it answered if the quote is
   short. If it overturns earlier text, mark that text `[SUPERSEDED …]` and keep it.
3. **Sweep citations** of the question and of anything overturned (`grep -rn "Qn (open)"`
   and the rule's key terms); update the line's handoff block (progress rung, carried-holes
   row). Run `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/ledger_check.py`.
4. **Show the diff.** Commit only if asked: `⚖️` subject carrying the quote, explicit
   path list.
