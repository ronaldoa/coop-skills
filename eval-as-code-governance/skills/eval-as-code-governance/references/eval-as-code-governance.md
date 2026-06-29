# Eval-as-Code Governance — the design-choice checklist

Manage an eval / test suite as a first-class engineering artifact ("like code"). The
root move: **decouple the gold from the corpus surface** so a corpus/data refactor no
longer forces you to "edit the fixture to make the test pass."

## §0 The root disease — what got bound to "the result"

A single eval case mixes four things of very different stability:

| Component | Belongs to | Stability | Example |
|---|---|---|---|
| `query` | user / traffic | stable | "how were Tesla's earnings" |
| **`gold` (doc IDs + ranks)** | **corpus surface** | **very unstable** | `doc_066 @ rank 1` |
| `meta` (family / language / shape) | description | fairly stable | `earnings_boundary` |
| corpus (the retrieved docs) | independent artifact | gets refactored | a slice renamed/merged docs |

**The binding** = gold expressed via *corpus-surface identifiers* (doc ID + rank). The
moment the corpus is refactored, gold breaks → pressure to "edit the fixture so the
test passes" (the exact anti-pattern diagnose-first memory guards against). This is
isomorphic to a unit test pinned to an internal snapshot — **the case is pinned to an
implementation detail.**

**First principle:** a case should assert **behavior** ("retrieved a doc satisfying
predicate P"), not **implementation** ("`doc_066` is at rank 1").

## The fix in one line

Express gold as a **predicate over stable semantic keys**, and have the corpus carry
`doc → key` as an intrinsic, build-time–derived view (NOT a second mapping file).
Refactor the corpus → doc IDs change, semantic keys don't → gold doesn't churn.
`recall@k of doc IDs` becomes **"does top-k contain a doc satisfying predicate P?"**
(property-based). Reuse an existing semantic-key layer if one exists (a template/slot
schema, an entity catalog) — don't build a parallel one.

---

## §3 The decision checklist (L1–L8) — ★ = keystone

Each item: options → recommendation → why → migration cost. Walk them when designing,
migrating, or auditing an eval suite.

### L1 — Case schema is a type contract
Upgrade the file-level sentinel (see the **fixture-authoring** discipline) to a real
**case-level schema** (pydantic / JSON Schema) validated in CI. **Matcher keys MUST be
constrained, never free strings** — a predicate referencing a non-existent value is a
silent failure (always-red or false-green). Constrain each matcher field to a live
source and **fail loud at authoring time** (`NO_SUCH_TEMPLATE` / `UNKNOWN_LABEL` /
`COLLISION`). Normalize entity references to canonical form (e.g. "Microsoft" → `MSFT`)
or the predicate silently never matches.

**Enum vs registry** — decided by *where a new value is born*:
- **Born in code** (a taxonomy design decision: response-mode / topic / frame) → **enum**: small, code-owned, rarely changes, wants exhaustiveness.
- **Born in data** (authoring corpus/catalog: template IDs, companies) → **registry** (open vocabulary, validated against the live set). Making these an enum **re-creates the coupling** — every new corpus template would force a code edit, destroying the decoupling. Want enum autocomplete without coupling → **codegen** the type from the live registry (SoT stays in data).

### L2 — gold ↔ corpus-surface decoupling ★ (keystone)
Predicate gold (`{semantic_key, slots}`) instead of doc-ID + rank. This is the only
root-cause fix for the binding; every other layer is stable only on top of it. Reuse
the existing key layer; the work is batch-migrating gold + a build-time derived view +
**corpus-internal consistency checks** (not a second mapping file). Open question to
settle per suite: **predicate granularity** — too coarse = "too loose" (see L3 / the
symmetry guardrails).

### L3 — Behavioral assertion, not implementation
Binary `recall@k over the predicate-satisfaction set` **+ keep MRR/nDCG as first-class
gateable rank metrics** — do NOT demote rank to pure diagnostic. What you remove is the
*doc-ID pin* (implementation brittleness), **not rank**: degradations like "rank-1 item
pushed out" or "reranker swaps best sibling for second-best" are visible *only* in rank
metrics, never in binary recall. Pair predicate looseness with **symmetric**
discriminative tests (see guardrails below).

### L4 — Case-level provenance + ownership + guard target
Each case records `source` (traffic | authored | regression_guard | synthetic), an
`owner`, and **`guards`** = which behavior / bug / slice it protects. This is blame +
docstring + commit-message for the case: it decides how much to trust a failure and
whether the case may be retired. Without `guards` you can locate "which bug class" but
not "what this case was meant to protect" — and the failure-routing loop below can't
tell "it caught the bug it should (don't touch it)" from "it's stale (fix it)".

### L5 — Change control (the fixture PR gate)
Every fixture change is classified `query-change` (new coverage) vs `gold-change`. A
**`gold-change` MUST cite a spec / behavior change; "to make the current output pass"
is a forbidden reason.** Machine-decidable violations hard-block immediately (schema /
unknown id / collision / missing negative / confirmed false-hit); governance/coverage
items (provenance backfill, min-n, soft false-hit risk) start advisory, ratchet to hard
as the suite matures. This promotes diagnose-first from a principle to a checkable gate.

### L6 — Coverage matrix + minimum-bucket size gate
Lay cases on a grid (axes = the behavior dimensions you care about: `family × language ×
query-shape`, refined post-L2 to `key × entity-slot`). **Empty cell = untested
behavior** (like an unwalked branch in code coverage). **For any slice that feeds
gating, set a minimum n** — `min_n = ceil(1/MDE)` (e.g. MDE 5pp → min_n 20). A cell
below min_n is `coarse_diagnostic_only`, not gating-eligible; attach a Wilson CI
half-width as a statistical-power signal. **The hard lesson it operationalizes:** adding
1–2 cases to an undersampled cell gives *false confidence* (per-case granularity coarser
than the target effect). Drive additions by the matrix (gap-driven / failure-driven),
never by family quota or inspiration. Ship the matrix as a static case-count cross-tab
(no retrieval run, deterministic) and wire it as a standing additive reporter.

### L7 — Lifecycle: golden vs generated split + retirement trail
Two tiers: **golden** (human, high-value, strong contract, heavy review) vs
**generated** (synthetic, regenerable, light review, has a generator — review the
generator + a pilot, not every row). Stress/adversarial sets are natural generated
candidates. Retiring a case = deleting dead code: when its guard target no longer
exists, remove it **with a SUPERSEDED trail**.

### L8 — Real-traffic anchor (external validity)
The first seven layers, done perfectly, are still only self-consistent on a **synthetic
distribution**. Build a channel that samples real traffic into the golden tier so
"representative" goes from an assertion to a measurement. Flag this as a **heavier,
independent investment** (sampling / redaction / labeling pipeline, privacy/governance)
— don't bundle it with Step 1. This is the "distribution" leg of faithfulness (see the
two-lane rule); without it the suite can never be falsified against reality.

---

## The operating loop — failure type → action (deterministic routing)

The payoff of L2 + L4: failures carry a **type**, so add/modify/fix-code routes
deterministically. (Doc-ID recall can't give a type — it only says hit/miss.)

| Failure signal | Root cause | Action |
|---|---|---|
| `WRONG_ENTITY` (right template, wrong entity) | retrieval / rerank bug | **fix code** — the case is doing its job, don't touch it |
| `RERANK_DEMOTED` (dense found it, rerank pushed it out) | rerank coverage | **fix code** (rerank/fusion); don't touch the case |
| `DENSE_MISS` (right template never retrieved) | retrieval quality / multilingual coverage | **fix corpus** (add template+entity docs, multilingual) |
| `GOLD_SEMANTIC_MISMATCH` (query meaning ≠ gold predicate) | gold is mislabeled | **fix the case** (diagnose-first relabel, cite the query's truth) |
| `NO_SUCH_KEY` (gold points at a non-existent key) | testing an unsupported capability | **add the corpus template** (if it should exist) / mark `known_gap` / remove (if out of scope) |
| whole cell empty | coverage gap (L6 exposed it) | **add a case** |

One-line rule: failure is a *retrieval behavior* → fix code (the case is right); failure
is *gold wrong/missing* → fix/add the case. `provenance.guards` is what lets you tell
"it caught the bug it was meant to (leave it)" from "it's stale (change it)".

**Add-a-case = write a unit test (TDD):** write `query` + `gold` predicate +
`must_not_satisfy` + `provenance.guards`; L1 lint rejects a dangling gold; run eval
**red first** → fix code → green. **Modify-a-case** is legal *only* when the behavior
spec changed, and the PR must cite the spec — never "to make current output pass".

---

## What to add — the four coverage detectors

Complements the addition *principle* (only add to cover a missing behavior **cell**;
cell-driven not family-driven; add up to an observable n; a positive needs a paired
negative; real failure > synthetic). The detectors answer *where to discover* the gap:

1. **Coverage matrix (systematic, proactive = L6).** Empty cell → add (red-to-implement if in-scope, else `known_gap`); thin cell (n < min) → add volume.
2. **Failure-driven (reactive).** A real failure → add a regression guard in its *exact* cell, record `provenance.guards`. The failure tells you which cell.
3. **Discriminative-power gap (advanced — from the predicate structure itself).** Two queries that should get *different* answers map to the *same* predicate = the key under-discriminates → add distinguishing cases and likely split the key. (Its corpus-side dual: audit each predicate's doc set; if same-predicate docs differ on a behavior-driving dimension not in the key, split the key / add a slot.)
4. **Reverse sampling (bidirectional data — anti-overfit).** If all canaries point one direction ("rerank pushed gold out"), tuning a *symmetric* fix on one-directional data **necessarily overfits**. Deliberately author the reverse cohort ("dense ranked wrong / rerank recovered", `failure_direction: rerank_recovers`) so any down-weighting/guard fix **exposes its cost** instead of silently passing. This is the one detector with real authoring cost — budget it.

---

## Looseness symmetry — the six guardrails

Loosening gold (relevant set 1→N) to fix a false **MISS** (gold stricter than behavior)
opens a symmetric false **HIT** (gold looser than behavior → a bad retrieval stays
green). Same axis: **gold granularity vs true behavior granularity**. The architecture
is neutral; overfit risk lives entirely in the combination *loose predicate + binary
recall + only wrong-entity negatives + one-directional canary*. Don't abandon looseness
— pin it within bounds and **symmetrize**:

1. **Blame-neutral judge.** The directional bet (which stage is at fault) lives in a flag-gated, default-OFF fix, not in gold/metric. Neutral = blame-neutral, NOT correctness-neutral (gold still asserts the right answer).
2. **Symmetric negative law.** Loosen one dimension ⇒ a `must_not_satisfy` must cover *that* dimension, else it's a one-way leak. Distinguish a *coverage* negative from a *correctness* one — don't turn an interchangeable-by-design pair (e.g. en/zh same-metadata docs) into a judge-red correctness assertion (that manufactures a false-miss).
3. **Keep MRR/nDCG gateable** — don't downgrade rank to diagnostic (binary recall can't see demotion / sibling-downgrade).
4. **Reverse sampling** (detector 4 above) — never tune a symmetric problem on one-directional data.
5. **Institutionalize counter-hypothesis cases.** Every "can simplify / can delete / can loosen / channel X is more trustworthy" action gets a case that goes red if the counter-hypothesis holds.
6. **Oracle independence.** The eval predicate judge is implemented independently of the production classifier (share spec, not code) with a drift test — a shared-code oracle lets a SUT bug blind the eval.

**Synonym widening** is the *only* permitted relaxation above the strict label floor,
and only via a **human-registered** cluster (lives eval-side, references corpus-owned
labels) with a written equivalence reason + ≥1 `must_not_satisfy` negative + an audit
gate. A `strip _zh/_en`-style heuristic is a read-only *discovery* aid, never a matcher
rule (variant usage is inconsistent — auto-merging is brittle). `expectedAxis =
(mode, topic, frame)` derived from the gold doc is for **reporting + false-hit probing
only, never a matcher**: same-axis-different-gold → soft WARN (prompts adding a hard
negative); hitting an explicit `must_not_satisfy` → hard FAIL.

---

## The two-lane rule — which lane's numbers count

Eval cases are *lane-independent*; the same cases run on two harnesses, and **which lane
is a choice, not a dataset property**:

- **Lane 1 — component / isolation** (e.g. pure dense search, no rerank/fusion): answers *bi-encoder component* questions only.
- **Lane 2 — production-faithful** (the *same* service object as live: rerank engaged, channel-sep, fusion): the headline / acceptance / calibration / reproduce-a-real-problem lane.

Hard rules: (1) **all production-relevant verdicts go through Lane 2**; reproducing a
rerank/fusion-caused production issue on Lane 1 is the *wrong instrument* (the failure
literally doesn't exist there). (2) **Don't optimize the Lane-1 proxy** — the more
production fuses dense+BM25+rerank, the less Lane 1 represents it; always label Lane-1
numbers "component / isolation, not production". (3) Separate **two faithfulness legs**:
*path* faithfulness (does eval run production code? — fixable with Lane 2) vs
*distribution* faithfulness (do eval queries resemble real traffic? — needs L8, a
synthetic set can't fix it). The closed loop: real failure → capture (with production
envelope) into the suite → run on Lane 2 (faithful reproduce) → typed failure locates
the layer → fix + the case guards the regression forever.

---

## Route to the right stage first

Before writing a case, decide *which stage / which eval suite* a distinction belongs to
— the test: **does this distinction change the intent identity (mode/topic/frame/key)?**
If yes → it's an intent-class distinction the retrieval suite has a key for → add a
retrieval case (two cells + a cross negative). If no — it only changes a *parsed value*
(a period binding, a slot value) → it belongs upstream (the parser's regression suite,
gold on the parsed result) or it's a deferred slot sweep → **don't forge a key for it in
the retrieval suite** (the gold would be under-defined and the schema can't constrain
it).

---

## Phased rollout — don't lay all 8 layers at once

- **Step 1 (now, low cost, ride the existing key layer):** L1 + **L2** + L3 + L5 — directly unbinds gold from the result.
- **Step 2 (later, needs investment):** L4 provenance + L6 coverage matrix / min-n + L7 golden/generated split.
- **Step 3 (heaviest, separate project):** L8 traffic anchor — make "representative" real.

## Relationship to the sibling disciplines

This sits above **fixture-authoring** (the `review-fixtures` skill): that discipline
makes a single fixture file's *intent match its data* via a sentinel-as-contract; this
one governs *the whole suite as code* — how gold is expressed, how failures route, how
coverage and statistical power are gated, how the suite stays externally valid. L1 here
upgrades that discipline's file-level sentinel into a case-level schema. Migration
correctness claims (churn = 0 under a semantics-preserving refactor; superset-not-loss;
no hit→miss flips) are re-derived under the **spec-authoring** discipline (`review-spec`)
§1.0 iron rule — re-run the producer, never read the committed artifact.
