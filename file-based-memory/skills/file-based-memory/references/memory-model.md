# What may enter each memory file

The dashboard is **replaceable** — overwrite it freely. The three durable files are the
things the dashboard would lose if rewritten; they are memory of *why*, and they are an
index plus anti-pitfall summary, **not compressed docs**.

## Admission filter

| File | Admit only if… |
|---|---|
| `architecture.md` | forgetting it would cause a *wrong code change* — not an overview, not "good to know" |
| `decisions.md` | the question is *likely to be re-argued* AND the rejection reason is recorded with a measurement or incident |
| `experiments.md` | the number affects a *threshold / baseline / closure* judgment; log dumps stay in run artifacts |

## Entry shape

- **5–10 lines per entry.** More means you are rewriting a spec: write the conclusion and
  link the canonical doc. If the spec moves, the spec moves; memory points at it.
- **Lead with the rule, then `Why:` and `How to apply:`** — a reader months later needs
  the why to judge edge cases.
- **Absolute dates.** Concrete paths, commands, numbers.
- Nothing derivable from the code or `git log` — memory holds the why, the code the what.

Example of the cap working: when a subsystem's rules grow, write one invariant in
`architecture.md` ("the high-precision layer owns X; variant coverage is the next
layer's job"), one rejected approach in `decisions.md` ("chasing every failing case in
the high-precision layer — rejected, the downstream layer is the right surface"), and a
pointer to `docs/<area>.md` for the full rule.

The cap is enforced on new and modified entries by the doc-budget gate
([enforcement.md](enforcement.md)).
