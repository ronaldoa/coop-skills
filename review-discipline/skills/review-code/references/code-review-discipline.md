# Code Review Discipline — Boundary Hygiene + Industrial Patterns

A reviewer-pass discipline for production code changes. Code can pass tests and
compile cleanly while still drifting on **architecture** (source-of-truth
fragmentation, boundary leaks, premature abstraction, defensive cruft) and on
**contract adherence** (tests assert mechanics, not the contract). This discipline
is the executable contract that catches that drift.

**First requirement — read the code, not the prose.** Before treating any
architectural claim (boundary, dispatch, SoT, contract surface) as true, re-derive
it from source with the smallest mechanical check (`rg`, `grep`, `git log -p`,
type-check, narrow unit test). A doc / commit message / PR description tells you
where to look; it cannot prove the code has the claimed shape.

**Iron rule for runtime claims.** For every runtime claim (eval/probe metric,
recall/accuracy number, count, "N tests pass", "byte-unchanged", gate PASS/FAIL),
re-derive it by running the producing command **end-to-end** — never by reading an
author-committed artifact (it is a claim under review, not evidence). When a flag
toggles behavior, run **both** states.

---

## 1. The discipline

After any production-code change, run a verification walk-through on the modified
modules:

> Read the change as if you've never seen the surrounding code. For every
> architectural claim (boundary placement, dispatch shape, SoT location, contract
> surface), verify against the source. Walk the call sites, don't just look at the
> function.

Two lenses, both must pass:

- **A. Boundary / SoT hygiene** — does the architecture stay clear over time? (Rows 1–3)
- **B. Pattern / overdesign / contract enforcement** — established patterns, no
  unnecessary abstraction, the contract actually enforced? (Rows 4–11)

This is the author's own pre-commit check. It is **not** line-by-line reading (that
catches typos, not architectural drift), **not** a reviewer's job alone, and **not**
optional for "small" PRs (a 3-line widening of a SoT-critical gate is the canonical
small-but-dangerous change).

---

## 2. What to verify — the 11 rows

Each row names a bug class; the right column is the concrete check. Every finding
must cite one row by name.

### Boundary / SoT (architectural hygiene)

| Row | How to verify |
|---|---|
| **1. Single source of truth (SoT)** | Every load-bearing fact has exactly **one** canonical location; other code references it. Before adding a constant/enum/lookup, ask "where does this fact live today?" If "nowhere" — add it. If "in module X" — reference X. **Check**: `rg` the new fact's name + synonyms repo-wide; ≥ 2 active definitions = a finding, fix the SoT before adding behavior. |
| **2. Module boundary clarity** | Each module exports a deliberate API; internal types stay internal (public-surface file re-exports the public API; a shared boundary/contracts file holds cross-module types; everything else is internal unless re-exported). **Check**: for each new/modified public type/export, `rg` all importers first — the diff must account for every consumer. A type used by ≥ 2 modules belongs in the shared boundary file, not inline in the producer. |
| **3. Producer/consumer contract** | When module A produces a value B consumes, the contract type is **named**, lives at a boundary file, and both sides reference it. **Crucially**: if a producer field is *executable* (regex / formula / expression / dotted path), the consumer must **execute** it during validation — not just structurally check the field exists with the right type. **Check**: for each contract field ask "is this interpreted later?" If yes, the consumer's validator must run that interpretation as part of accept/reject. |

### Pattern selection (industrial patterns first)

| Row | How to verify |
|---|---|
| **4. Reuse existing patterns before inventing** | Most repos have established idioms (a `Result`/error type, typed registries, factory functions, named loaders, a module-naming convention). **Check**: before a new idiom, ask "can I compose this from existing patterns?" If yes, do that. If the new idiom is cross-module / reusable / replaces an existing pattern / changes a boundary, record the rationale in durable memory (see §9 for the idiom catalog). Local helpers don't need a memory entry. |
| **5. Dispatch tables over conditional chains** | When behavior varies by enum value, prefer `dict[Key, Callable]` / `match` / typed lookup over `if`/`elif`/`else` chains — the chain is a refactor magnet at every new case; the table accepts a new case as one line. **Check**: count branch arms on a typed key. ≥ 3 is a worth-considering signal; ≥ 5 is a blocker. |

### Anti-overdesign

| Row | How to verify |
|---|---|
| **6. No speculative abstraction** | Abstract when duplication is real, not hypothetical. One caller stays inline; two may still duplicate if the logic is small; a third normally triggers extraction (exception: boundary/SoT helpers where two consumers would otherwise encode the same contract). If you defer an abstraction, record the trigger where maintainers will see it — "later" is not a trigger. **Check**: for each new abstraction (factory/dispatcher/strategy/generic), list current callers and the drift it prevents. One caller → inline it unless it's a boundary helper. |
| **7. Validate at system boundaries only** | Internal callers trust internal callers; the strength of that trust scales with the type system. Cross-process, JSON, disk, external-API, and user-input boundaries stay untrusted. Defensive checks (`assert isinstance`, `if x is None: raise`, redundant `try/except`) at every internal entry are cruft unless the boundary/type system is weak. **Check**: per validation site, ask "trusted internal caller or untrusted external boundary?" Untrusted → keep. Trusted → delete only after `git blame`/`git show` shows why it was added; if from a bug fix, prove the bug is now closed by a stronger type / caller fix / unreachable path. |
| **8. Executable hooks exercise the contract, not just mechanics** | A passing suite confirms only the hooks it runs, not every contract the spec states. Every load-bearing contract clause needs an executable enforcement hook (unit/contract test, lint, verifier, typecheck, eval gate). Hooks are artifacts too — they can be slow, flaky, over-broad. **Check**: for each load-bearing `MUST`/`MUST NOT`, name the hook that fails when it's violated. If a hook needs many mocks / global state / broad e2e to write, treat that as design feedback and re-check the contract boundary. |
| **9. Config / flag / default discipline** | Env vars, flags, thresholds, defaults are production contracts when they change behavior. Each needs one owner, one canonical default source, an explicit purpose, and a removal/stabilization trigger when temporary. **Check**: `rg` the flag/config name; confirm exactly one canonical default; confirm tests/evals cover the default path AND the changed-behavior path. Temporary → name the removal condition (not "TBD"). |
| **10. Preserve score / metric semantics** | Numeric fields driving gates, rankings, fusion, routing, or evals are semantic contracts. When touching `score`/`confidence`/`gap`/`margin`/`threshold`/`vote`/`prior`/metric names, verify producer meaning, consumer expectation, range, monotonic direction, unit, and calibration owner. **Check**: per changed load-bearing numeric field, write source, range, higher-is-better?, consumer, threshold owner, and one hook proving old/new semantics aren't silently mixed. |
| **11. Predicate branch coverage** | For new/modified **load-bearing predicates** (branches affecting validity, eval/report numbers, gate verdicts, routing, cache/write paths, contract validators), evidence must cover the documented trigger **and at least one meaningful off-axis trigger**. Examples: strict bool predicates need `True`/`False` + missing/non-bool; regex word-boundary predicates need separated + adjacent/near-miss inputs; cache/file-existence branches need warm + cold. **Check**: `rg` changed files for `is True`/`is False`/`is None`, literal equality, numeric boundaries, `re.search`/`re.match`; for each load-bearing hit name the off-axis test. Happy path only = predicate safety not verified. |

---

## 3. When to apply

- **New module**: Rows 1, 2, 3 (boundary placement + API surface).
- **Modifying a module**: the touched surfaces — producer/consumer (3), new dispatch (5), new abstraction (6), config/default (9), numeric semantics (10), new predicate (11).
- **PR review**: treat each `+` line as the object under test, surrounding context as the boundary check.
- **Before landing (author-side floor)**: Rows **1, 3, 8** minimum. For a non-trivial change (≥ 5 files OR touching boundary code — contracts/loaders/dispatchers/config/scores), run **all 11**. Skipping the floor on a non-trivial change means you read it, you didn't review it.
- **Bug-fix commits**: Rows 7 + 8 — most fixes either remove a defensive check that hid the bug or add a hook that catches the regression. If yours does neither, ask why the bug was reachable.
- **Refactor commits**: Rows 1, 4, 6 — refactor is when SoT consolidation / pattern reuse should happen. If it reduces neither SoT count nor reinvention, ask what it achieves.

### 3.1 Finding format

Every finding names: **Row violated** · **Claim being checked** · **Evidence**
(file:line, command output, test result, or an artifact you **regenerated this
session** — regenerate then `git diff`/`shasum` to confirm byte-identical; an
author-committed artifact is a claim under review, not evidence) · **Risk** (what
breaks if it lands) · **Minimal fix** · **Hook** (test/verifier/typecheck/lint/eval
gate that fails next time). *A finding without evidence is a suspicion; a finding
without a hook is likely to recur.*

### 3.2 Changed code vs affected surface

A changed line may alter an affected surface beyond the diff: public API, config
default, loader contract, dispatch behavior, snapshot shape, metric meaning, eval
lane. Review the smallest surface that can *observe* the change — `rg` the consumers
— not only the file that changed.

### 3.3 Change atomicity

Keep feature work, refactors, fixture/data edits, docs, and cosmetic renames in
separate commits when practical — one logical reason per commit, one dominant review
mode. If a mixed PR is unavoidable, list the change classes so reviewers know which
rows apply to which files.

### 3.4 Failure modes considered

For boundary / config / loader / cross-process / generated-artifact / contract-shape
changes, enumerate failure modes before treating the change as complete. For each
load-bearing failure: how it's **detected**; how it **surfaces** (`Result`,
exception, failed gate, validation error, fallback, warning); who **owns recovery**
(caller/callee/runner/operator); which executable **hook proves** it. If a failure
mode is hard to express, the contract may be under-specified — don't paper over it
with a broad e2e test.

### 3.5 Row-dispute resolution

When author and reviewer cite the same row but reach opposite conclusions, return to
the concrete check. Row application is decided by code facts: caller count, SoT
count, import graph, default location, hook coverage, metric source/range/direction,
or `rg`/test/eval output. If a row supports both sides without a command, both sides
are still at the prose layer — run the check first, then decide.

---

## 4. Anti-patterns

**Code-shape anti-patterns:**

- **"Looks robust because it's defensive."** Internal entries crammed with `try/except`/`isinstance`/`if x is None`. It hides the real failure mode, adds a site to forget when types change, and signals "this caller is untrusted" to future readers. Fix: Row 7 — validate at boundaries; if you don't trust a caller, fix the type.
- **"Generic by default."** Parameterization before the second use case. The generic is invariably too loose or too tight, the second caller never arrives, and it's maintenance overhead forever. Fix: Row 6 — write the concrete version, wait for a real second caller.
- **"Test-for-test-coverage."** Tests assert the function runs without crashing, not that it fulfills the contract. Spec contract ships unverified behind green tests. Fix: Row 8 — every load-bearing clause needs a hook that fails when it's violated.
- **"One more config flag."** A flag for hypothetical future behavior becomes load-bearing infra, permanently `default=false`. Fix: Row 9 — direct code change unless staged rollout genuinely needs a flag with an explicit removal trigger.
- **"Half-finished implementation."** A stub/TODO wired into a production path the surrounding code assumes works. Fix: don't wire a production call site to unshipped behavior; keep placeholders unreachable + tested as unreachable.

**Discipline-application anti-patterns (review-process bugs):**

- **Row-citation-as-rhetoric** — citing a row as a shield instead of applying its check (e.g. Row 6 to block an extraction that already has three real callers).
- **Mechanical row-walk** — checking row labels without running the row's check ("looked plausible" is not Row 1's `rg`).
- **Artifact-as-evidence** — reading an author-committed eval/metric artifact and treating its numbers as verified. Regenerate it (expect byte-identical) or re-run the producer end-to-end; run both states when a flag toggles.
- **Row mismatch** — applying the wrong row and fixing the wrong thing (treating an untrusted disk/JSON/HTTP read as an internal caller under Row 7 and deleting validation that should stay).

---

## 5. Worked examples (generic)

- **Row 3 (executable field not executed).** A producer declares a `naming_convention`
  regex; the consumer's loader validates "field exists, is a string" but never runs
  the regex against the IDs it governs. Two IDs that violate the regex pass
  validation. Lesson: when a field is executable, structural validation is
  insufficient — the consumer must run the interpretation.
- **Row 6 (deferred abstraction, done right).** A gate widens from one allowed key to
  two. The lookup-table refactor is the right shape at ~7 keys, not at 2 — so widen
  to set-membership now and defer the table to the slice that reaches N keys, naming
  the trigger. Lesson: the right shape at N=7 is not the right shape at N=2.
- **Row 8 (implicit contract, no hook).** "The changelog is in monotonic order" is a
  contract everyone "knows" but nothing tests; an out-of-order entry lands twice. A
  3-line `sort -c` check at pre-commit would catch it. Lesson: even cosmetic-feeling
  contracts can be tested; if it reappears in two reviews, write the test.
- **Row 11 (happy-path-only).** A regex word-boundary check passes on the spaced
  input (`tesla report`) but the off-axis adjacent-script input (`tesla报告`)
  carries the bug; a strict-bool partition passes `True`/`False` but buckets a
  missing field silently. Lesson: exercise the closest off-axis shape that would
  make the predicate lie before dismissing the concern.

---

## 6. Cost-benefit

- **Author-side per-PR check (primary).** Rows 1, 3, 8 against the diff before
  committing: **5–15 min** per non-trivial PR. Cheaper than the re-cycle it prevents
  (a Row 3 gap caught at next review costs an amendment commit + repeated reviewer
  time + future-reader doubt).
- **Reviewer-side full scan (secondary).** All 11 rows on non-trivial PRs (≥ 5 files
  or boundary code): **30–60 min**. Apply before merging boundary changes, new
  dispatch/factory/generic, or flag/default/threshold/score/metric changes.
- **Anti-pattern: confusing the two.** Author skipping the floor because "it's small"
  → bugs leak to next cycle. Reviewer checking "only what changed in this PR" →
  boundary changes whose consumers aren't in the diff escape. Complementary; neither
  substitutes for the other.

---

## 7. Stability pledge

Start at **11 rows**. A new row requires **all three**: (1) a concrete bug class the
existing rows do NOT cover ("an existing row would have caught it if applied" is
application failure, not new coverage); (2) ≥ 1 worked example showing the existing
rows are structurally insufficient; (3) cost-benefit — a new row costs every future
reader's attention forever. Goal: stay at **≤ 12 rows**; a 13th must include a
deletion candidate. The anti-pattern this guards against is
**discipline-as-evergreen-checklist**. Before proposing a row, first try to classify
the issue under the existing rows — most new findings are missed applications.

---

## 8. Relationship to spec-authoring discipline

Companion to the spec-authoring discipline (the `review-spec` skill). Both
instantiate one principle — **commands establish facts; code / specs / fixtures
state claims** — applied to different artifact classes. Code review verifies the
code's shape matches the claimed architecture + contract; spec review verifies the
prose matches the code. Findings from each cite that discipline's named rows, so
recurring rows signal which failure modes keep biting.

---

## 9. Reference: industrial patterns relied on

Standard idioms this discipline assumes (reuse them consistently rather than
reinvent — Row 4):

- **Result / typed-error type** — fallible operations return a `Result<T, E>` (or
  equivalent) instead of throwing; chain with `map`/`mapErr`/`andThen`.
- **Factory function** — centralized construction with defaults, one per major type.
- **Keyed registry** — type-safe registry for descriptors / handler registration.
- **Strategy via dispatch table** — `dict[Key, Callable]` for enum-keyed behavior.
- **Named loaders** — one loader per shape, each with a single responsibility.
- **Sentinel-as-contract** — a single source of truth for test/fixture intent that
  the loader validates rows against.
- **Module naming convention** — `index`/`types`/`contracts`/`runtime`/`policies`/
  `factories`/`service`/`builder`/`engine` map to specific responsibilities.
- **Cross-stage snapshot contract** — a canonical interchange type between pipeline
  stages; producers emit it, consumers read it.
- **Dependency direction** — runtime code doesn't import tooling/offline code;
  shared helpers live in a shared module; producers don't import consumers.
- **Ports / adapters** — external systems (HTTP, disk, model calls, APIs) isolated
  behind adapters; core logic consumes typed inputs, not env/disk/HTTP directly.
- **Versioned schema evolution** — cross-boundary data-shape changes use schema
  versions + dispatch + validation, not silent parser widening.
- **State machine / discriminated union** — status/verdict/health use closed enums /
  discriminated unions / transition tables, not boolean soup.
- **Typed error taxonomy** — fallible boundaries return typed errors / small error
  codes, not ad-hoc strings thrown from arbitrary depth.
- **Explicit state ownership** — mutable/generated state has an owner, writer,
  reader, and invalidation/rebuild trigger.
- **Composition root** — config loading, dependency construction, clients, and
  wiring live in a few entrypoints; leaf modules don't read env / init clients
  independently.
- **High cohesion / low coupling** — one reason to change per module.
- **Functional core, imperative shell** — domain logic as typed input → typed
  output; env/disk/HTTP/logging/orchestration at the edges.
- **Policy / mechanism split** — separate the rule table / threshold / policy from
  the engine that applies it, so calibration is reviewable without touching execution.
- **Open/closed through registries** — growth by schema version / signal type /
  family / stage prefers registry extension over scattered conditional edits.
- **Generated-artifact boundary** — generated aggregates / baselines / indexes are
  outputs, not authoring surfaces; review the source inputs + rebuild command, not
  the generated diff.

These are standard industrial idioms; the discipline is to reuse them consistently.
