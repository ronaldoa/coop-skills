---
name: review-code
description: Run a structured reviewer-pass on a code change, applying the code-review discipline's 11-row verification taxonomy as an executable contract. Default target = the uncommitted git diff; also accepts paths, a commit/range, or a PR number. Use when reviewing a diff/PR, before committing non-trivial code, or as a pre-PR self-check. Output = findings keyed to named rows in the Row/Claim/Evidence/Risk/Minimal-fix/Hook format.
when_to_use: review this code / diff / PR; check my change before committing; structured code review; verify architecture/contract adherence; pre-PR self-review
---

# review-code

Run a **structured reviewer-pass** against a code change using
[references/code-review-discipline.md](references/code-review-discipline.md) as the
verification framework. The change to review is `$ARGUMENTS` (default = the
uncommitted working-tree diff).

This is the discipline applied as a contract, not as advice. Code can pass tests and
compile cleanly while drifting on architecture (SoT fragmentation, boundary leaks,
premature abstraction, defensive cruft) and on contract adherence (tests assert
mechanics, not the contract). The output is findings keyed to specific rows. The two
sibling disciplines share the same fact-trace stance, different target: `review-spec`
verifies the prose matches the code; `review-fixtures` verifies a fixture's data
matches its declared testing intent. Code review verifies the code matches the
claimed architecture + contract.

## Hard rules

1. **Read the code, not the prose.** Before treating ANY architectural claim
   (boundary, dispatch, SoT, contract surface) as true, re-derive it from source
   with the smallest mechanical check (`rg`, `git log -p`, type-check, narrow test).
2. **Runtime claims = re-run the producing command end-to-end.** Any metric, count,
   "N tests pass", "byte-unchanged", gate PASS/FAIL — re-derive by running the
   test/probe/lint/typecheck, NOT by reading the author-committed artifact (it's a
   claim under review). **When a flag toggles behavior, run BOTH states.**
3. **Re-read the §2 row list before starting** (11 rows). Every finding MUST cite
   one row by name. A finding fitting no row is evidence the row set is incomplete OR
   the finding is out of scope.
4. **No findings invented to fill the report.** If clean, say so — a short clean
   verdict is correct.
5. **Changed code ≠ affected surface** (§3.2). `rg` the consumers/importers; review
   the smallest surface that can *observe* the change, not only the changed file.
6. **Coverage floor scales with the change** (§6). Floor = Rows **1, 3, 8**. For a
   non-trivial change (≥ 5 files OR touching boundary code — contracts/loaders/
   dispatchers/config/scores), run **all 11 rows**.

## Step 1 — resolve the target + load context

Resolve `$ARGUMENTS` to a concrete diff:

- **empty** → uncommitted: `git --no-pager diff` (+ `--staged`); if both empty, `git show HEAD`.
- **path(s)** → `git --no-pager diff -- <paths>` (or `git show HEAD -- <paths>` if committed).
- **a commit / range** → `git --no-pager show <commit>` / `git --no-pager diff <range>`.
- **a PR number** → `gh pr diff <n>` (+ `gh pr view <n>` for intent).

Then read, in order: (1) the diff — classify each file by review mode (feature /
refactor / fixture-data / config / docs, §3.3); (2)
[references/code-review-discipline.md](references/code-review-discipline.md) §2 rows
+ §3.1 finding format + §3.4 failure-modes + §4 anti-patterns; (3) for each touched
module, the call sites / importers (`rg` the changed symbols) so the affected
surface is in view; (4) any runtime-contract / durable-memory invariant the change
touches.

## Step 2 — re-run runtime claims (Section A)

For every runtime claim the change rests on or asserts, re-derive it by running the
producing command (rule 2). Use the project's own commands — its test runner, type
checker, linter, and the specific probe/eval that produces any cited number. For
"byte-unchanged" / "no-op" claims, run both flag states and diff the outputs; for an
artifact, regenerate it and `git diff`/`shasum` to confirm byte-identical.

Output Section A as a table:

```
| Claim (where asserted) | Command re-run | Fresh result | Verdict |
|---|---|---|---|
```

✅ = matches; ❌ = mismatch (promote to Section C). A claim with no re-runnable
producer is marked un-verified and flagged — never accepted on the artifact's word.

## Step 3 — re-derive architecture / boundary claims (Section B)

For every architectural claim, run the concrete check (rule 1):

- **SoT (Row 1)** → `rg` the new fact + synonyms; ≥ 2 active definitions = finding.
- **Boundary (Row 2)** → `rg` importers of each new/modified public type; used by ≥ 2 modules → belongs in the shared boundary file.
- **Producer/consumer (Row 3)** → for each contract field, is it executable? If yes, does the consumer **execute** it (not just structurally validate)?
- **Dispatch (Row 5)** → count branch arms on a typed key; ≥ 3 worth-considering, ≥ 5 blocker.
- **Config default (Row 9)** → `rg` the flag/default; confirm exactly one canonical default.

Section B = a short bulleted list of checks + ✅/❌. Each ❌ is a finding for Section C.

## Step 4 — apply §2 rows to the diff (Section C)

Map each changed surface to the rows that govern it:

| Change kind | Apply row(s) |
|---|---|
| New module / API surface | 1 SoT, 2 boundary, 3 producer/consumer |
| Modified producer↔consumer boundary | 3 (esp. executable-field execution) |
| New conditional branching on a typed key | 5 dispatch table |
| New abstraction / factory / generic / helper | 6 no speculative abstraction |
| New/removed validation or `try/except`/`isinstance` | 7 validate at boundaries only |
| New `MUST`/`MUST NOT` contract clause | 8 executable hook exercises the contract |
| Env var / flag / threshold / default | 9 config/flag/default discipline |
| `score`/`confidence`/`gap`/`margin`/`threshold`/`vote`/`prior`/metric | 10 preserve score/metric semantics |
| New/modified load-bearing predicate (`is True/False/None`, literal eq, numeric boundary, `re.search`/`match`, cache/file existence) | 11 predicate branch coverage |
| Boundary / config / loader / cross-process / generated-artifact / contract-shape change | §3.4 failure-modes pass |

**Predicate dismissal rule (Row 11):** to decline a candidate predicate concern as
refuted, the evidence MUST show the happy-path trigger AND ≥ 1 meaningful off-axis
trigger. Only one shape checked → keep it as a finding/open question.

Each finding uses the §3.1 format, with an ID (F1, F2, …) and severity:

```
F<N> — <one-line title> (<severity>, Row "<row name>")

- Claim being checked: <architectural / contract claim under review>
- Evidence: <file:line + command output / test result / regenerated artifact (this session, byte-identical confirmed) — never an un-re-derived committed artifact>
- Risk: <what breaks if this lands>
- Minimal fix: <smallest change that closes the gap>
- Hook: <test / verifier / typecheck / lint / eval gate that fails next time>
```

Severity: **HIGH (BLOCKER)** mechanism/contract/SoT error shipping wrong behavior
(typically Rows 1, 3, 8, 10) · **MEDIUM** boundary-clarity / dispatch-shape /
config-default / overdesign drift that rots (Rows 2, 5, 6, 9) · **LOW** cosmetic ·
**INFORMATIONAL** sound but out-of-scope.

## Step 5 — summary verdict (Section D)

One paragraph + one recommendation line. Verdicts: **CLEAN** (ready to land) ·
**FINDINGS — fix-and-land** (only MEDIUM/LOW; same PR, no re-review) · **FINDINGS —
re-review needed** (≥ 1 HIGH, or a large MEDIUM set) · **BLOCKED** (structural
problem it can't resolve alone — escalate). End with one concrete next-action
sentence (e.g. "Fix F1 (Row 3); fold F2 same PR; F3 INFORMATIONAL — land.").

## Step 6 — final output

```
Code reviewer-pass — <target> (<N files, dominant modes>)

A. Runtime claims — <all PASS | N findings>
<table of re-run commands + fresh results>

B. Architecture / boundary re-derivation — <all PASS | N findings>
<bulleted rg / import-graph / dispatch-count checks>

C. Findings (keyed to §2 rows)
<F1..Fn in §3.1 format with severity>

(Optional) Failure modes considered — <for boundary/config/loader/contract-shape changes>
<per load-bearing failure: detection / surfacing / recovery owner / hook>

D. Summary
<verdict + recommended next action>
```

Keep prose tight; the value is in surfaced findings, not narrative.

## Anti-patterns (the discipline can be misused — §4)

Artifact-as-evidence (re-run the producer; both states on a flag) · mechanical
row-walk (run the row's check, don't read its label) · row-citation-as-rhetoric
(applying a row as a shield) · row mismatch (deleting boundary validation as if it
were an internal caller under Row 7) · prose-only review (every Section A row needs a
re-run, every Section B bullet an executed check) · severity inflation (HIGH is for
mechanism/contract/SoT failures only) · reviewing changed lines only (`rg` the
consumers).

## When the change has no obvious discipline fit

If a finding fits no row, surface it as a meta-finding: "Candidate finding X fits no
current row — either out of scope, or a coverage gap. Per §7, propose a new row ONLY
with a concrete uncovered bug class + worked example + a deletion candidate (cap ≤
12)." Most apparent gaps are missed applications of an existing row — re-attempt
classification first.
