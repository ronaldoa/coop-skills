---
name: review-spec
description: Run a structured reviewer-pass on a spec / design / measurement doc, applying the spec-authoring discipline's verification taxonomy as an executable contract. Every load-bearing claim is re-derived from source. Use when reviewing or ratifying a doc, before committing a spec edit, or when verifying a design proposal against the codebase. Output = A. numbers / B. references / C. findings keyed to named rows / D. verdict.
when_to_use: review this spec / design doc; verify a doc's claims against code; ratify a spec; check my doc edit before committing; reconcile a design proposal against the codebase
---

# review-spec

Run a **structured reviewer-pass** against `$ARGUMENTS` (the path to a doc) using
[references/spec-authoring-discipline.md](references/spec-authoring-discipline.md) as
the verification framework.

This is the discipline applied as a contract, not as advice. Every load-bearing claim
in the target doc gets re-derived from source; the output is findings keyed to
specific rows with severity. The two sibling disciplines share the same fact-trace
stance, different target: `review-code` verifies the code matches the claimed
architecture; `review-fixtures` verifies a fixture's data matches its declared
testing intent. Spec review verifies the prose matches the code.

## Hard rules

1. **Commands establish facts; the doc states claims.** Do NOT trust a number,
   line-ref, commit hash, regex, path, or arithmetic in `$ARGUMENTS` until you've
   re-derived it from source (`rg`, `git log/show/diff`, `python3 -c`, `node -e`,
   `jq`, `ls | wc -l`, or the narrowest project test/eval).
2. **Plausibility is the trap** (§4). If a claim "feels obviously right" you must
   still verify — the obvious cases are where the author skips checking.
3. **Re-read the §2 row list before starting.** Each finding MUST cite one row by
   name. A finding fitting no row is evidence the row set is incomplete OR the finding
   is out of scope.
4. **No findings invented to fill the report.** If clean, say so — a single-paragraph
   clean verdict is acceptable.
5. **Fresh-reader stance.** Run the pass as if you did not author the doc and don't
   know the intended fix. Do not trust cycle-log claims that a finding was folded;
   re-check the affected claim across the whole doc and sibling docs. If this is
   author self-review / same-context, label the result **PRE-FLIGHT** only —
   ratification still requires a fresh-reader pass.

## Step 1 — load context

Read, in order: (1) `$ARGUMENTS` — note its status, parent doc(s), and which siblings
it references by path; (2)
[references/spec-authoring-discipline.md](references/spec-authoring-discipline.md) §2
rows + §3 when-to-apply + §4 anti-patterns; (3) any sibling docs the target cites by
path — the cross-reference surfaces where drift hides; (4) the target's parent doc, if
any.

## Step 2 — verify load-bearing numbers (Section A)

Walk every numeric claim. Findings come from: file/case/row counts (`find … | wc -l`,
`wc -l`, `python3 -c`); per-cohort counts (verify against the canonical aggregate, not
another prose doc); metrics / ranks / scores / `sha256` — **re-run the producing
command and match its fresh output; do NOT `jq`/read the committed result JSON** (§1.0;
reading the artifact is fidelity, not verification — recompute a `sha256`, don't read
a stored hash); arithmetic subclaims (re-add yourself); test counts (re-run the runner
if load-bearing).

Output Section A as a table:

```
| Claim site | Claim | Re-derived | Verdict |
|---|---|---|---|
```

✅ = match; ❌ = mismatch → the row IS the finding; promote to Section C with the row
name. A number with no re-runnable producer is marked un-verified and flagged.

## Step 3 — verify references & paths (Section B)

Walk every `path:NNN-MMM` citation, commit hash, function/constant/regex/env-var name,
and "X exists" claim: open the file and confirm the lines; `git show --stat <hash>`
confirms a commit exists + matches the narrative; `rg -n '<name>'` confirms a symbol;
`ls`/`find` confirms a path. Section B = a short bulleted list of checks + ✅/❌. Each ❌
is a Class A (mechanism-correctness) finding for Section C.

## Step 4 — apply §2 rows to the doc body (Section C)

For each modified / load-bearing section, apply the appropriate §2 row(s):

| Doc section type | Apply row(s) |
|---|---|
| Mechanism / pseudocode | Code-vs-spec contract · Function/constant names · Default values · Line numbers |
| Phase tables / closure criteria | Cross-stack contracts · Cross-reference drift |
| Cycle log / status header | Cross-reference drift (status-state propagation) · Source-of-truth hierarchy |
| Acceptance / closure gates | Interpretive scope/framing · Measurement-surface alignment · Proxy-vs-direct-measurement |
| Measurement / closeout reports | Report-vs-data integrity · Execution-derived claims |
| Multi-stage fix scoping | Root-cause stage attribution |
| Fixture / registry batch authoring | Source-of-truth hierarchy · "X exists" claims |
| Ratification after folds | Fresh-reader ratification · Cross-reference drift |
| **Design spec proposing new types / enums / functions / flags / stages / contracts** | **Design-vs-codebase reconciliation** — `rg` each proposed name for an existing equivalent + confirm each proposed flow stage resolves to a real call site |
| Any load-bearing conclusion / recommendation / proposed idea | Dual-grounding (empirical + theoretical) · Industry-practice anchor (for external state-of-practice claims) |

**Mandatory reconciliation pass for new-artifact designs.** If the target *proposes*
new artifacts (it's a design spec, not a measurement/closeout doc), you MUST run the
"Design-vs-codebase reconciliation" row: for every proposed name, `rg` the codebase
for an existing equivalent/synonym; for every proposed flow stage, `rg` the
handler/call site to confirm it exists in the real path. A proposed artifact that
duplicates an existing definition, creates a second SoT, or assumes a non-existent
stage is a finding reachable only by checking the design against code.

**Behavioral dismissal rule.** To decline a candidate behavioral/predicate concern as
refuted, the evidence must show the happy-path trigger AND ≥ 1 meaningful off-axis
trigger. One shape only → keep it as a finding/open question; don't silently dismiss.

Each finding gets an ID, severity, and a concrete fix:

```
F<N> — <one-line title> (<severity>, <Class A | Class B>, Row "<row name>")

<2-4 sentences of evidence: what the doc says, what source says, how they differ.>

Fix: <concrete edit — exact text to change or section to add.>
```

Severity: **HIGH (BLOCKER)** mechanism error / factual drift — Class A · **MEDIUM**
sibling cross-reference drift, stale status, count mismatch in a cited table — Class B
· **LOW** cosmetic · **INFORMATIONAL** faithfully-quoted from a sibling, not
actionable here. For each author-flagged open item, give a one-paragraph read with
severity — these are judgment calls returned to the author, NOT findings; don't merge
the two surfaces.

## Step 5 — summary verdict (Section D)

One paragraph + one recommendation line. Verdicts: **CLEAN** (ready for approval) ·
**FINDINGS — fold-and-approve** (small Class B / cosmetic set; fold in the same
commit) · **FINDINGS — re-review needed** (Class A present, or a large Class B set) ·
**BLOCKED** (a structural problem the target can't resolve alone — escalate). End with
one concrete next-action sentence.

## Step 6 — final output

```
Verification walk-through — <doc short name> <state>

A. Load-bearing numbers — <all PASS | N findings>
<table or per-claim verification>

B. References & paths — <all PASS | N findings>
<bulleted list of checks>

C. Reviewer-pass findings
<F1..Fn with severity + row + fix>

(Optional) Author-flagged opens 1..n — reviewer read
<one paragraph per open item>

D. Summary
<verdict + recommendation>
```

Keep prose tight; the value is in surfaced findings, not narrative. A clean doc gets a
short report — that's correct.

## Anti-patterns

Inventing findings to fill rows (all ✅ → write "all PASS") · prose-only review with no
command runs (every Section A row needs a re-derivation, every Section B bullet an
executed check) · reading the committed result-artifact and calling it verified
(re-execute the producer; a sha-pinned JSON is still a prior artifact) · skipping row
attribution (a finding without a row name can't drive discipline evolution) · severity
inflation (status-lag is MEDIUM; HIGH is for mechanism / code-vs-spec failures) ·
conflating findings with author-flagged opens.

## When the target doc has no sibling discipline doc

If the target is in a different domain (e.g. a runtime contract doc with no discipline
sibling), surface a meta-finding: "Target has no canonical discipline sibling;
reviewer applied spec-authoring-discipline by analogy. Recommend filing a
discipline-doc sibling if this class of artifact has multiple instances."
