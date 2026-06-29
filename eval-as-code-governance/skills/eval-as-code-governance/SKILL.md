---
name: eval-as-code-governance
description: Govern a retrieval / ML eval suite as first-class code — decouple gold from the corpus surface (assert behavior via a predicate over stable semantic keys, not doc-ID + rank), then walk the L1–L8 decision checklist, the deterministic failure→action loop, the four coverage detectors, the looseness-symmetry guardrails, and the two-lane rule. Use when designing or migrating an eval/test suite, when corpus refactors keep breaking fixtures, when deciding what cases to add, or when auditing an eval suite's governance.
when_to_use: design / migrate an eval or retrieval test suite; corpus refactor keeps forcing "edit the fixture to pass"; decide which eval cases to add and how many; gold churns on every data change; audit an eval suite as code; set up coverage / statistical-power gating for evals
---

# eval-as-code-governance

Treat an eval / test suite as a first-class engineering artifact — manage it **like
code**. The root move, from which everything else follows: **decouple the gold from the
corpus surface** so a data/corpus refactor stops forcing you to "edit the fixture to
make the test pass." Framework:
[references/eval-as-code-governance.md](references/eval-as-code-governance.md).

**First principle.** A case must assert **behavior** ("top-k contains a doc satisfying
predicate P"), not **implementation** ("`doc_066` is at rank 1"). Gold pinned to doc-ID
+ rank is a unit test pinned to an internal snapshot — it breaks on every corpus
refactor and breeds the "fit the current output" anti-pattern. Express gold as a
**predicate over stable semantic keys**; let the corpus carry `doc → key` as a
build-time–derived view, not a second mapping file.

This is the design/governance layer above the reviewer-pass disciplines. It sits on top
of **fixture-authoring** (`review-fixtures`): that makes one fixture file's intent match
its data; this governs the whole suite — how gold is expressed, how failures route, how
coverage and statistical power are gated, how the suite stays externally valid.

## Two modes

- **Design / migrate** (the suite is new or you're unbinding gold from the corpus): walk
  L1–L8, then phase the rollout. Default to **Step 1 = L1 + L2 + L3 + L5**; defer L4/L6/L7
  to Step 2 and L8 (traffic anchor) to a separate project.
- **Audit** (an eval suite exists; check its governance): walk L1–L8 as a checklist and
  emit findings — which layers are present, which are missing, and the single highest-
  leverage gap (almost always L2 if gold is still doc-ID-pinned).

## Hard rules

1. **Behavior over implementation (L2/L3).** Remove the doc-ID *pin*, not rank — keep
   MRR/nDCG as first-class gateable metrics (demotion is invisible to binary recall).
2. **Matcher keys are constrained, never free strings (L1).** A predicate referencing a
   non-existent key/entity is a silent failure (always-red or false-green). Fail loud at
   authoring time; normalize entity references to canonical form.
3. **Enum vs registry by birthplace (L1).** Born in code (taxonomy) → enum. Born in data
   (corpus templates, entities) → registry/codegen — making these an enum re-creates the
   coupling L2 exists to remove.
4. **Loosening is symmetric (guardrails).** Loosen one dimension ⇒ add a
   `must_not_satisfy` covering *that* dimension, plus a reverse-direction cohort. Never
   tune a symmetric fix on one-directional data.
5. **Migration verdicts are re-run, not read.** "churn = 0", "superset, no gold lost",
   "no hit→miss flips" are runtime claims — re-derive with the producing command
   (spec-authoring §1.0). The correct migration criterion is **NOT byte-identical**
   (predicate gold is 1-to-many = looser by design); it is *satisfaction-set ⊇ old gold
   ⇒ no hit→miss flip*, with miss→hit flips enumerated as intended looseness.
6. **Which lane's numbers count (two-lane rule).** All production-relevant verdicts run
   on the production-faithful lane; never optimize the component/isolation proxy, and
   label its numbers as such.

## The walk

### Step 1 — frame the binding
State, for the suite under design/audit, what the gold is bound to. If gold is doc-ID +
rank, name the corpus refactor that would break it — that's the disease. Identify the
**existing semantic-key layer** to reuse (a template/slot schema, an entity catalog);
L2 reuses it, never forks a parallel one.

### Step 2 — walk L1–L8 (the checklist)
For each layer, state the option chosen + why + migration cost. ★ L2 is the keystone —
nothing above it is stable until gold is decoupled. (Full per-layer text in
[references/eval-as-code-governance.md](references/eval-as-code-governance.md) §3.)

- **L1** case schema as type contract (constrained matcher keys; enum-vs-registry).
- **L2 ★** gold ↔ corpus-surface decoupling (predicate over semantic keys).
- **L3** behavioral assertion + keep rank metrics gateable.
- **L4** case provenance + ownership + `guards` (what bug/behavior it protects).
- **L5** change-control gate (`query-change` vs `gold-change`; gold-change cites spec).
- **L6** coverage matrix + min-bucket size gate (`min_n = ceil(1/MDE)`).
- **L7** golden vs generated lifecycle + retirement trail.
- **L8** real-traffic anchor (external validity — heavy, separate).

### Step 3 — the operating loop (failure → action)
Once L2 + L4 are in, failures carry a **type** and route deterministically:
`WRONG_ENTITY` / `RERANK_DEMOTED` → **fix code** (case is doing its job); `DENSE_MISS` →
**fix corpus**; `GOLD_SEMANTIC_MISMATCH` → **fix the case**; `NO_SUCH_KEY` → add template
/ `known_gap` / remove; empty cell → **add a case**. `provenance.guards` is what
separates "caught the bug it should (leave it)" from "stale (change it)".

### Step 4 — what to add (four detectors) + add-discipline
Discover gaps via: (1) coverage matrix (empty/thin cell), (2) failure-driven (guard the
exact failure cell), (3) discriminative-power gap (two answers, one predicate → split
the key), (4) reverse sampling (bidirectional data — budget it). Add **only to cover a
missing behavior cell**, cell-driven not family-driven, up to an observable n, each
positive paired with a negative, real failure > synthetic. Never "add case = pin current
output as correct".

### Step 5 — emit the result
- **Design/migrate** → a phased plan: Step 1 (L1+L2+L3+L5), Step 2 (L4+L6+L7), Step 3 (L8),
  with the L2 migration milestones (key-layer ready → predicate gold + dual-run
  superset check → discriminative negatives → churn=0 under a semantics-preserving
  refactor → metric switch → retire the doc-ID field).
- **Audit** → findings keyed to layers:

```
F<N> — <one-line title> (<severity>, Layer L<n>)

- What the suite does today: <observed — file:line / schema / gate>
- What the layer requires: <the L<n> contract>
- Risk: <what breaks / what stays silently green>
- Fix: <smallest change toward the layer>
```

Severity: **HIGH** gold still corpus-surface-pinned (L2), a loose predicate with no
symmetric negative (false-hit leak), or a matcher key that can dangle (L1) · **MEDIUM**
missing provenance/`guards` (L4), no coverage/min-n gate (L6), optimizing the Lane-1
proxy · **LOW** lifecycle/trail gaps (L7) · **INFORMATIONAL** L8 (sound but a separate
project).

## Anti-patterns

Byte-identical as the migration criterion (predicate gold is looser by design — use
superset/no-hit→miss) · matcher keys as free strings (dangling gold = silent
always-red/false-green) · enum-ing data-born keys (re-welds the coupling) · one-way
looseness (loosen a dimension without the symmetric negative) · tuning a symmetric fix
on one-directional canaries · optimizing the component lane and reading its numbers as
production · adding by family quota instead of by coverage cell · "add a case" that just
records current output as correct.

## When a distinction doesn't fit the suite

Before forging a key, ask: does this distinction change the **intent identity**
(mode/topic/frame/key)? If no — it only changes a parsed value — it belongs upstream
(a parser's regression suite) or is a deferred slot sweep; **don't forge an
under-defined key** the schema can't constrain. Route to the right stage first.
