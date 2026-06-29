# Fixture Authoring Discipline — Sentinel-as-Contract

A reviewer-pass discipline for test-fixture / eval-dataset changes. Fixtures can
load cleanly and pass CI while their **testing intent drifts from their data** — the
file claims (by name or convention) to test one thing, the rows below exercise
another. This discipline is the executable contract that catches that drift.

**Why it exists.** The canonical failure: a fixture's testing intent is encoded only
in a **naming convention** (case-id slugs like `*_memory_*` / `*_history_*`) plus the
implicit input shape (which fields happen to be populated). No schema-level statement
makes the convention visible; no loader catches intent-vs-data drift. Two independent
readers then misread the same cohort — one conflated "key absent" with "key present +
null" (`dict.get` returns `None` for both), the other miscounted cases and conflated
two distinct shapes. The id *looked* right; the load-bearing fact was buried in the
data and in which consumer read which field.

**The fix in one line.** Lift implicit-by-convention test intent into an
**explicit, schema-level sentinel** that a loader validates on **every read**, so
intent-vs-data drift fails loud instead of being silently misread. This is the same
move spec-authoring and code-review make: turn an implicit-by-convention claim into an
explicit-by-schema artifact that fails loud on drift.

---

## 1. The contract — the sentinel

Every authored fixture file carries a **sentinel** as its first row (or a sibling
manifest) that is the **single source of truth for that file's testing intent**. Case
rows below it MUST satisfy the sentinel's declarations. A minimal sentinel declares:

| Field | Holds |
|---|---|
| `schema_version` | versions the sentinel shape; the loader **dispatches** on it (unknown version → fail-loud, never silent-parse) |
| `cohort` | a unique slug naming this file's cohort (no two files share one) |
| `input_shape` (or `query_shape`) | a **file-level invariant** — every case exercises the same shape |
| `intent` | 1–2 sentences: what aspect of behavior this file tests |
| `fields_populated` | dotted paths that MUST resolve to a **non-null** value in every case |
| `fields_absent_intentionally` | dotted paths whose key MUST be **absent** (NOT present-with-null) |
| `expected_behavior` | 1 sentence: which component is load-bearing + what it should produce |
| `naming_convention` | a regex the case ids MUST match |
| `case_count_at_authoring` | integer snapshot of the row count (manual, deliberate) |
| `authored_at` / `references` | provenance + links to the design/contract doc |

The sentinel is **executable**: the loader runs its declarations against the case
rows on every read, not just a structural "field exists, is a string" check.
(Generalize the field names to the project's fixture format — `.jsonl` first-row
sentinel, a `.json` manifest, a YAML front-block; the *shape* is what transfers.)

---

## 2. Per-fixture verification walk-through

After any single-file fixture change, run this 5-step pass before commit. Each step
is a runnable check, not a prose read.

1. **case-id ↔ `naming_convention`.** Every case `id` matches the regex. A new
   non-matching id → either widen the regex (deliberate cohort expansion) OR move the
   case to the sibling file it actually belongs to. Verify the regex against the real
   id list with **zero false negatives and zero unintended matches** — regex
   plausibility is not evidence.
2. **data ↔ `fields_populated` / `fields_absent_intentionally`.** Every populated
   path resolves to a non-null leaf; every "absent" path is a **missing key**, not a
   key-present-with-null. (This strict distinction is the whole point — `dict.get`
   conflates the two.) Fail-loud → either the case data is wrong, the sentinel claim
   is wrong, or the case is misplaced. **Do NOT silently adjust the sentinel to fit a
   misplaced case** — that re-introduces the drift the sentinel exists to prevent.
3. **`expected.*` ↔ `expected_behavior`.** Each case's expected outcome is consistent
   with the sentinel's prose. Often free-form prose vs structured fields → **reviewer
   responsibility**, not mechanically enforced; surface inconsistency as a drift
   finding.
4. **`case_count_at_authoring` ↔ actual count.** After add/remove, re-stamp the count
   (it's a manual deliberate snapshot, not auto-updated). Bump `last_revised_at`.
5. **single-shape per file.** `input_shape` is a **file-level invariant** — every row
   exercises the same shape. A case with a different shape → move it to a sibling or
   carve a new file; **DO NOT widen the shape prose to accept a mixed cohort** (that's
   the original misread anti-pattern).

---

## 3. Cross-file consistency

- **Cohort uniqueness.** Two files with the same `cohort` slug → namespace collision,
  almost certainly authoring drift. Surface as a finding; do not merge silently.
- **Single source of truth per cohort.** If a new file's intent overlaps an existing
  file's semantically, prefer adding cases to the existing file over creating a
  parallel one.
- **No second prose SoT.** Directory READMEs / index tables MUST be *derived* from the
  sentinels (file, cohort, shape, count, intent) — never hand-maintained as a second
  source that drifts.

---

## 4. Reviewer checklist (fixture-changing PR)

- [ ] Every case-row change has a corresponding sentinel update (or fits the existing
      declarations).
- [ ] `case_count_at_authoring` matches the new count.
- [ ] `fields_populated` / `fields_absent_intentionally` were **re-verified** this
      change — not inherited unread from the prior sentinel state.
- [ ] If `input_shape` would change, the cohort migration is intentional and the file
      move / split is captured in the PR description (not a silent shape drift).
- [ ] `last_revised_at` bumped if any sentinel field changed.
- [ ] The loader's structural + contract validators ran on the new state (CI green).
- [ ] Any generated aggregate / index is back in sync (`--check` exits 0).
- [ ] Derived README / index tables updated if `cohort` / `shape` / `intent` changed.

### 4.1 Symmetric-eval check (conditional — when a PR loosens gold, adds predicate
gold, or adds a one-directional canary)

The fuller treatment (the false-hit trigger condition, the six guardrails, the four
coverage detectors) lives in the **eval-as-code-governance** skill — reach for it when a
suite is loosening gold systematically, not just for a single fixture PR.

- [ ] **Symmetric negative**: each loosened gold dimension has a `must_not_satisfy`
      negative covering THAT dimension (loosen one dim = open one leak; close it).
      Distinguish a *coverage* check from a *correctness* one — don't turn an
      interchangeable-by-design pair into a judge-red correctness assertion.
- [ ] **Two-directional sampling**: a one-directional canary ("X demotes the correct
      item") is paired with a reverse cohort ("X recovers"). Never tune a symmetric
      problem on a one-directional dataset.
- [ ] **Rank metrics stay a gate**: don't downgrade MRR/nDCG to diagnostic — binary
      recall can't see demotion / sibling-downgrade.
- [ ] **Oracle independence**: the eval predicate judge is implemented independently
      of the production classifier (share spec, not code) with a drift test — a
      shared-code oracle lets a SUT bug blind the eval.
- [ ] **Blame-neutral judge**: the directional bet (which stage is at fault) lives in
      a flag-gated, default-OFF fix, not in gold/metric. Neutral = blame-neutral, NOT
      correctness-neutral (gold still asserts the right answer).
- [ ] **KPI-redefinition disclosed**: a gold loosening (relevant-set 1→N, recall
      systematically higher) is named as such in the PR description.

---

## 5. Full-coverage backfill template (bulk authoring / new schema / new directory)

For instrumenting many files at once, an **audit + schema-ratification pre-pass scales
linearly**; hand-writing N sentinel rows scales quadratically with cross-file
consistency. Do NOT start by hand-writing N sentinels.

1. **Audit (Phase 0).** Profile every target file *before editing*: case count, id
   prefix/family, row shape, load-bearing fields. Flag mixed-shape files.
2. **Restructure first.** Split/carve mixed-shape files so every file is pure
   single-shape *before* authoring any sentinel. Never widen shape prose to fit.
3. **Ratify the schema BEFORE authoring** sentinels in any new shape's directory
   (retrieval vs pipeline vs control). New schema version forks the validator
   dispatch; reserved enum/cohort values are decided up front.
4. **Validator dispatch as a registry** (open/closed): `version → validator`, with
   unit tests pinning the active schema set. Unknown version fails loud.
5. **Ship the batch verifier BEFORE backfilling** so it is the *acceptance gate*, not
   post-hoc. Manual per-file walk-through doesn't scale past ~dozens of files.
6. **Backfill one directory per commit**; flip each directory's "require sentinel"
   gate only after its files pass the verifier.
7. **Closeout numbers come from re-runnable snippets** — file counts, per-directory
   counts, moved-case counts, aggregate row counts, hashes — never hand-counted prose.

The batch verifier checks (cross-checked against the design's enumerated criteria):
sentinel exists + validates structurally; `fields_populated`/`fields_absent` match
every row; `case_count_at_authoring` matches; `naming_convention` matches every own id
AND **rejects every sibling-file id** (reverse-direction cross-product); single-shape
consistency; reserved cohort slug appears only on its designated directory; generated
aggregate pre/post ids+counts unchanged.

---

## 6. Anti-pattern — "looks right because the id contains the keyword"

A case id `..._memoryview_..._decision_...` *looks* like it tests the memoryview→
decision path — and may. But the load-bearing fact is in the case's *data* (which
field carries it) and in *which consumer reads it*, neither legible from the id. The
sentinel makes it load-bearing: `input_shape` (file fact) + `fields_populated`
(exactly which leaf carries the data) + `expected_behavior` (which component is
load-bearing). **The naming convention is a quick hint, not a contract** — always
trace the sentinel + the data + the loader's contract validator before treating "the
id contains keyword X" as evidence.

---

## 7. Enforcement boundary & when to apply

- **Single-file change** → run the §2 5-step walk-through manually.
- **Multi-file / cross-cutting / bulk** → run the §5 batch verifier (`--all`, exit 0 =
  clean) as the acceptance gate.
- **New schema version / new aggregate key / new fixture directory** → §5 preflight
  (audit → ratify → staged author → per-key gate flip → verifier) is mandatory.
- A different fixture format (e.g. `.json` modules vs `.jsonl`) needs schema
  adaptation, not a new discipline — the sentinel-as-contract shape transfers.

---

## 8. Relationship to the sibling disciplines

Companion to **code-review** (the `review-code` skill) and **spec-authoring** (the
`review-spec` skill). All three instantiate one principle — *commands establish facts;
code / specs / fixtures state claims* — applied to a different artifact class:

- **review-code**: the code's shape matches the claimed architecture + contract.
- **review-spec**: the prose matches the code.
- **review-fixtures**: the fixture's data matches its declared testing intent.

`code-review-discipline.md` §9 lists **"Sentinel-as-contract"** among its industrial
patterns; this discipline is that pattern applied as a reviewer-pass. Findings from
each cite that discipline's named checks, so recurring failures signal which class
keeps biting.

One level up sits the **eval-as-code-governance** skill: this discipline keeps a single
fixture file's intent matching its data; eval-as-code governs the whole *suite* as code
— how gold is expressed (predicate over semantic keys, not doc-ID), how failures route,
how coverage and statistical power are gated. Its L1 upgrades this discipline's
file-level sentinel into a case-level schema.
