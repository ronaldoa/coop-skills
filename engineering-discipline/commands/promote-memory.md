---
description: Sort a personal / auto-memory directory into what belongs in the repo (principles, standing rules, field rules), what stays as a one-line pointer, and what should be deleted
argument-hint: [optional path to the memory directory; defaults to this project's auto-memory]
---

Follow `references/growing-a-principles-ledger.md` ("What to promote from personal
memory") in the `engineering-discipline` skill.

1. **Read every memory file in full** (default: the memory directory named in the system
   context; else `$ARGUMENTS`). Do not classify from the index lines alone — the index is a
   summary and the load-bearing clause is often only in the body.
2. **Classify each entry** into exactly one destination, with a one-line reason:

   | Destination | When |
   |---|---|
   | principles file (which §, merge or new) | true in any project, has an incident |
   | field rules (`agent-ops`-style) | operational, portable, has an incident |
   | router standing rules | this project, every session |
   | stays: one pointer line | an entry point into a line of work |
   | stays: dated fact + re-probe | environment state that changes |
   | delete | already in the repo, or superseded |

   For "already in the repo", **cite the file and line where it lives** — verify, don't
   assume (a memory may claim it was promoted when it was not, or the reverse).
3. **For each promotion, map before adding** (duplicate / complement / conflict) against
   the target file, and check the target's line ceiling. Quote the memory's incident; don't
   paraphrase it into something it didn't say.
4. **Present the table and stop.** Edit nothing until the user rules on it — promotions
   change files every session loads. After the ruling: make the edits, reduce each promoted
   memory to "promoted to <file> <date>" (or delete it), update the memory index, and run
   the ceiling gate.
