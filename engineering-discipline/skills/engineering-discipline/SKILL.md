---
name: engineering-discipline
description: Portable engineering discipline for agent-driven development — how to know a gate, measurement or claim is true (mutation-tested criteria, real end-to-end runs, honest "not measured"), how LLMs and deterministic code divide work, and the field rules for running many agent sessions on one codebase without breaking each other's work. Use when writing a test or gate, reporting a measurement, putting an LLM in a loop, deleting or adding a field or code path, designing a slice, running parallel sessions or worktrees, spending paid API calls, or promoting personal-memory lessons into a repo's rules.
when_to_use: writing a new test / gate / criterion; claiming a step is done; reporting numbers; designing an LLM-in-the-loop feature; deleting or adding a protocol field; parallel sessions sharing a worktree; killing processes / reading ports / env precedence; before spending LLM calls; "turn our memory into rules", "set up engineering principles for this repo"
---

# Engineering Discipline

| Reference | Answers |
|---|---|
| [ENGINEERING_PRINCIPLES.md](references/ENGINEERING_PRINCIPLES.md) | *how do I know this is true?* Start at its own router line (✍️ gate → §1 · 🚢 done → §1.6 · 🤖 LLM → §2.2 · 📊 measurement → §3 …) and read the § in full |
| [agent-ops.md](references/agent-ops.md) | *how do I find out without breaking anything?* — parallel sessions, processes, instruments, paid calls |
| [growing-a-principles-ledger.md](references/growing-a-principles-ledger.md) | how a repo grows and caps its **own** ledger, and what to promote from personal memory |

The principles file is a **verbatim** copy of EquityResearch's `ENGINEERING_PRINCIPLES.md`
at commit `60804e2c` (2026-10-08). Its italic instances name that project's defects; the
rules are stack- and domain-independent. Keep its §-IDs (the rules cross-reference them);
edit the origin and re-copy rather than editing the copy.

`hooks/ceiling_check.py` (before agent commits): a markdown file declaring
`Ceiling: N lines` in its first ten lines may not exceed N. `/engineering-discipline:promote-memory`
sorts a memory directory into repo rules, pointers and deletions.
