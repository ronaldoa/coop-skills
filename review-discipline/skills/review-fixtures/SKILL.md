---
name: review-fixtures
description: Run a structured reviewer-pass on a test-fixture / eval-dataset change, applying the fixture-authoring discipline's sentinel-as-contract taxonomy as an executable contract. Verifies each fixture file's data matches its declared testing intent. Use when reviewing a fixture/eval-data change, before committing new or edited fixtures, or when instrumenting a fixture tree with intent sentinels. Output = findings keyed to named checks in the Check/Claim/Evidence/Risk/Minimal-fix/Hook format.
when_to_use: review this fixture / eval-dataset change; check my fixture edit before committing; verify testing intent matches fixture data; add intent sentinels to a fixture tree; bulk-backfill eval fixtures
---

# review-fixtures

Run a **structured reviewer-pass** against a test-fixture / eval-dataset change using
[references/fixture-authoring-discipline.md](references/fixture-authoring-discipline.md)
as the verification framework. The change to review is `$ARGUMENTS` (default = the
uncommitted working-tree diff, restricted to fixture / eval-data files).

This is the discipline applied as a contract, not as advice. Fixtures load cleanly and
pass CI while their **testing intent drifts from their data** — the file claims (by
name or convention) to test one thing, the rows exercise another, and a reader misreads
what's under test. The output is findings keyed to specific checks. This is the third
sibling of the review disciplines: `review-code` verifies the code matches the claimed
architecture; `review-spec` verifies prose matches code; **`review-fixtures` verifies
each fixture's data matches its declared testing intent.**

## Hard rules

1. **Run the check, don't read the convention.** A case-id slug, a directory name, or
   a prior sentinel is a *hint*, never evidence. Before treating "this file tests X" as
   true, re-derive it from the case data + the loader's contract validator.
2. **Absent key ≠ key-present-with-null.** The canonical bug: `dict.get` returns `None`
   for both, so "field absent" and "field null" get conflated. When verifying
   `fields_absent_intentionally`, confirm the **key is missing**, not present-with-null.
3. **Re-run the loader / verifier; don't trust CI's word.** For any "validator passes"
   / "aggregate in sync" / "N files instrumented" claim, re-run the producing command
   (the loader on the changed file, the batch verifier `--all`, the aggregate
   `--check`) — never accept a committed result artifact.
4. **Re-read the §1 sentinel fields + §2 walk-through before starting.** Every finding
   MUST cite one check by name. A finding fitting no check is evidence the check set is
   incomplete OR the finding is out of scope.
5. **No findings invented to fill the report.** If clean, say so — a short clean
   verdict is correct.
6. **Coverage floor scales with the change.** Single-file → the §2 5-step walk-through.
   Multi-file / new-schema / new-directory / bulk → the §5 backfill template + batch
   verifier as the acceptance gate.

## Step 1 — resolve the target + load context

Resolve `$ARGUMENTS` to a concrete set of fixture files:

- **empty** → uncommitted fixture/eval files in `git --no-pager diff` (+ `--staged`).
- **path(s)** → `git --no-pager diff -- <paths>` (or `git show HEAD -- <paths>`).
- **a commit / range** → `git --no-pager show <commit>` / `diff <range>`, fixture files only.
- **a PR number** → `gh pr diff <n>` (+ `gh pr view <n>` for intent), fixture files only.

Then read, in order: (1) the diff — classify each file (new file / added case / removed
case / cohort move / schema change); (2)
[references/fixture-authoring-discipline.md](references/fixture-authoring-discipline.md)
§1 sentinel contract + §2 walk-through + §3 cross-file + §6 anti-pattern; (3) the
project's **loader** (how it dispatches on `schema_version` and what its contract
validator actually executes) and **batch verifier** if one exists; (4) the design /
contract doc the sentinels reference.

## Step 2 — re-run loader / verifier claims (Section A)

For every runtime claim the change rests on, re-derive it by running the producing
command: load the changed file through the loader with contract validation on; run the
batch verifier (`--all`); run the aggregate `--check`. For "byte-unchanged aggregate"
claims, regenerate and `git diff` / `shasum`.

```
| Claim (where asserted) | Command re-run | Fresh result | Verdict |
|---|---|---|---|
```

✅ = matches; ❌ = mismatch (promote to Section C). A claim with no re-runnable producer
is marked un-verified and flagged.

## Step 3 — per-file walk-through (Section B)

For each changed file run the §2 5-step pass as concrete checks:

- **id ↔ `naming_convention`** → run the regex against every id; zero false negatives AND zero unintended matches.
- **data ↔ `fields_populated` / `fields_absent_intentionally`** → every populated path non-null; every "absent" path a **missing key** (rule 2).
- **`expected.*` ↔ `expected_behavior`** → reviewer-judged consistency (often not mechanically enforced).
- **`case_count_at_authoring` ↔ actual** → re-count rows.
- **single-shape per file** → every row exercises the declared `input_shape`.

Section B = a short bulleted list of checks + ✅/❌. Each ❌ is a finding for Section C.

## Step 4 — cross-file + findings (Section C)

Apply §3 (cohort uniqueness, single-SoT-per-cohort, no second prose SoT) and §4.1
(symmetric-eval, **only if** the PR loosens gold / adds predicate gold / adds a
one-directional canary). Map each change kind to the checks that govern it:

| Change kind | Apply check(s) |
|---|---|
| New fixture file | sentinel contract (§1), cohort uniqueness (§3), naming-convention reverse-cross-product |
| Added / removed case | data↔fields, case-count, single-shape, id↔naming |
| Cohort move / file split | single-shape, cohort uniqueness, "don't widen shape to fit" (§2.5) |
| Schema-version change | loader dispatch (unknown version fails loud), validator registry, §5 ratify-before-author |
| Gold loosening / new canary | §4.1 symmetric-eval checklist |
| Bulk / full-tree backfill | §5 template — audit → ratify → staged author → per-key gate flip → batch verifier |

**Dismissal rule.** To decline a candidate intent-vs-data concern as refuted, the
evidence MUST show the populated/expected shape AND ≥ 1 meaningful off-axis shape (e.g.
the absent-key case AND a present-with-null case). One shape only → keep it as a finding.

Each finding uses this format, with an ID (F1, F2, …) and severity:

```
F<N> — <one-line title> (<severity>, Check "<check name>")

- Claim being checked: <intent / data / contract claim under review>
- Evidence: <file:line + loader/verifier output (re-run this session) — never an un-re-derived committed artifact>
- Risk: <what a reader misreads, or what regression escapes, if this lands>
- Minimal fix: <smallest change — fix the data, fix the sentinel, or move the case>
- Hook: <loader contract validator / batch verifier / aggregate --check that fails next time>
```

Severity: **HIGH (BLOCKER)** sentinel-vs-data drift that makes a reader misread what's
under test, or a leak the eval can no longer catch · **MEDIUM** count/cohort/shape drift
or a missing reverse-direction check that rots · **LOW** cosmetic · **INFORMATIONAL**
sound but out-of-scope.

## Step 5 — summary verdict (Section D)

One paragraph + one recommendation line. Verdicts: **CLEAN** (ready to land) ·
**FINDINGS — fix-and-land** (only MEDIUM/LOW; same PR) · **FINDINGS — re-review needed**
(≥ 1 HIGH, or a large MEDIUM set) · **BLOCKED** (structural problem it can't resolve
alone — e.g. no schema ratified for a new shape; escalate). End with one concrete
next-action sentence.

## Step 6 — final output

```
Fixture reviewer-pass — <target> (<N files, dominant change kinds>)

A. Loader / verifier claims — <all PASS | N findings>
<table of re-run commands + fresh results>

B. Per-file walk-through — <all PASS | N findings>
<bulleted §2 checks + ✅/❌ per file>

C. Findings (keyed to discipline checks)
<F1..Fn with severity>

D. Summary
<verdict + recommended next action>
```

Keep prose tight; the value is in surfaced findings, not narrative.

## Anti-patterns

Convention-as-evidence (the id slug "looks right" — §6; trace the data + validator) ·
silently adjusting the sentinel to fit a misplaced case (§2 — fix the data or move the
case, don't loosen the claim) · widening `input_shape` prose to accept a mixed cohort
(§2.5 — split the file) · regex-plausibility (a `naming_convention` that "looks" right
but was never run against the real id list, both directions) · reading a committed
verifier artifact instead of re-running it (rule 3) · hand-authoring N sentinels before
the audit + schema ratification (§5 — scales quadratically) · one-directional eval
tuning (§4.1 — pair the canary with a reverse cohort).

## When the change has no obvious discipline fit

If a finding fits no check, surface it as a meta-finding rather than forcing it. Most
apparent gaps are missed applications of an existing check (usually the absent-key /
single-shape / convention-vs-data ones) — re-attempt classification first. If the
fixture format genuinely differs (e.g. `.json` modules vs first-row `.jsonl`
sentinels), note that the sentinel-as-contract *shape* transfers and recommend adapting
the schema, not inventing a parallel discipline.
