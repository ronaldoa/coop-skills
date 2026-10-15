# Supersede, don't delete

Applies to the durable layers (`architecture` / `decisions` / `experiments`). The
dashboard is replaceable and exempt.

The expensive knowledge is *why an approach was rejected*. Delete the entry when you change
your mind and the next person re-proposes it, re-discovers the failure and re-pays the
cost; you also lose the answer to "when did we believe X, and what changed our mind?".

## Supersede one entry

Keep the original; prepend a marker and a forward pointer:

```markdown
## [SUPERSEDED 2026-06-28 → see "New approach to gate scoring"] Old gate heuristic

Why superseded: the fixed threshold drifted under the new calibration; replaced by the
isotonic fit measured in experiments.md "calibration v2".
<original body left intact below>
```

Absolute date · forward pointer by title · the **trigger** (a measurement, an incident, a
ruling — never just "outdated"). In a chain the newest entry is authoritative and older
ones link forward.

## Fold a closed cluster

When a whole slice reaches a terminal state, collapse its entries into one:

```markdown
## [FOLDED 2026-06-28] Stage-2 contract redesign (§13.x) — CLOSED

Terminal state: shipped as RATIFIED; thread closed. Folded entries (full text at commit
abc1234, see docs/stage2.md):
- "Stage2 owns claim-scope, not Stage3"
- "rejected: per-claim re-ranking in Stage2 (measured regression, experiments.md v3)"
```

A folded entry is an index over closed entries, so the gate gives it a larger cap
([enforcement.md](enforcement.md)). Fold only a genuinely closed, clustered slice; a single
stale entry is superseded, not folded.

The same marker demotes an old handoff heading in a line doc (`[SUPERSEDED <date> → §0.0]`),
which is how the doc gates tell a live entry point from history ([worklines.md](worklines.md)).
