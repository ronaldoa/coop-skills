# Supersede, don't delete

When a durable entry (`architecture.md` / `decisions.md` / `experiments.md`)
becomes wrong or outdated, **mark it SUPERSEDED with a pointer to what replaced
it** — do not silently remove it.

## Why the trail is the value

The expensive knowledge in `decisions.md` is *why an approach was rejected*. If you
delete the old entry when you change your mind, the next person (or you, in six
months) re-proposes the rejected approach, re-discovers the failure, and re-pays the
cost. The supersede trail is what makes the memory monotonic: it only ever gains
information.

A silent deletion also destroys the audit chain — you can no longer answer "when did
we believe X, and what changed our mind?" That question is exactly what durable
memory exists to answer.

## How to supersede

Keep the original entry; prepend a status marker and a forward pointer:

```markdown
## [SUPERSEDED 2026-06-28 → see "New approach to gate scoring"] Old gate heuristic

Why superseded: the fixed threshold drifted under the new calibration; replaced by
the isotonic fit measured in experiments.md "calibration v2".
<original body left intact below>
```

Conventions:

- **Use absolute dates** (`2026-06-28`), never "last week" — the reader has no
  temporal context.
- **Point forward by title**, so the replacement is one search away.
- **State the trigger** for the supersede (a measurement, an incident, a decision),
  not just "outdated".
- For a long chain, the newest entry is authoritative; older ones link forward in
  sequence so the chain is walkable in one direction.

## Distinguish from the operational dashboard

`CURRENT_STATUS_AND_NEXT_STEPS.md` is **replaceable**, not append-only — it holds
*current* operational state, so freely overwrite it. The supersede discipline
applies to the **durable** `project-memory/` layers, where history is the point.
