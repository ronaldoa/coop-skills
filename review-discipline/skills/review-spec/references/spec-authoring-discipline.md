# Spec Authoring Discipline — Verification Walk-Through

A reviewer-pass discipline for spec / design / measurement docs. The failure surface
is **fact-attribution drift**: prose that reads plausibly but is *false* against the
code, data, or math it describes — wrong line numbers, wrong counts, reversed
formula direction, stale wording, a claim sourced from another doc instead of from
ground truth.

**First requirement — commands establish facts; docs state claims.** Before treating
any code-grounded prose claim as true, re-derive it from the source of truth with the
smallest mechanical check (`rg`, `git`, `python3 -c`, `node -e`, `jq`, `ls | wc -l`,
a project test, an eval runner). A document tells you where to look; it cannot prove
another document's claim. Treat every modified paragraph as the object under test.

---

## 0. Why this exists

Standard line-by-line proofreading verifies that writing is *grammatical*; it does
not verify that writing is *true*. The two canonical bug classes:

- **Fact attribution** — a mechanism is cited at the line that *feels* right
  (e.g. "short-circuits via `isinstance` guards at line 192") when the real mechanism
  is elsewhere. The author cited without opening the file.
- **Logic direction** — a formula's direction is stated backwards (e.g. "`p10`
  excludes 90%" when gate `>= p10` *admits* 90%). The author didn't substitute
  concrete values to check direction.

Both emerge from rewriting a section without verifying the new text against actual
source / mathematical semantics.

---

## 1. The discipline

### 1.0 First rule (iron rule): run before you conclude

> **No conclusion from reading or memory.** Before stating any conclusion about how
> the current system behaves — a number, a mechanism, a pass/fail, an "it is X"
> attribution, a feasibility / capability verdict ("circular" / "can't do X without
> Y" / "degrades to Y" / "the runtime can't see Z") — run the current code or command
> against current state and read its output. Docs, prior artifacts, git history, and
> your own recollection tell you *what* to run; they never substitute for *running*
> it. A conclusion that cannot be run right now is provisional and must say so.
>
> **This explicitly includes committed result-artifacts** (diagnostic JSON, eval
> output, baseline files) — yours or another agent's, sha-pinned or not. To verify a
> cited number you **re-execute the computation that produces it** and confirm the
> output; reading or `jq`-ing the stored artifact confirms only that the doc quotes
> the file faithfully, which is **not** verification (the file is itself an
> un-re-derived prior artifact). If a cited value has no producing computation left to
> re-run, treat it as **un-verified-by-this-pass and flag it**, rather than trusting
> the stored number. A re-run only verifies if performed under the **same pinned
> run-config** (model / mode / dataset + checksum / device / env flags / determinism
> controls) — see the §2 "measurement-surface alignment" row.

**The runnable-but-unrun tell.** Feasibility / capability verdicts *feel* like
deduction rather than empirical claims — which is exactly why they evade the rule. A
load-bearing verdict you *could* run but didn't, with no command + output next to it,
is not a verdict; downgrade it to "to-measure" until you run it. The recurring
failure is not ignorance of the rule but the default posture: reading or inferring a
result that is *consistent* with a claim and treating consistency as verification.
**Consistency with a number is not evidence for the claim that produced it. When in
doubt, run it.**

After any spec modification, run a verification walk-through on the modified section:

> Read the new text as if you've never seen the spec. For every concrete claim —
> every number, line reference, file path, formula, contract assertion — verify it
> against the actual source. Walk the logic; don't just look at the words.

Identify the source of truth for each load-bearing claim: code behavior → code or
execution; counts → the underlying files; history → `git`; cross-document
consistency → `rg` over the related docs *plus* the underlying source. If a claim can
only be supported by another prose document, it is still unverified.

This is the author's own pre-commit check. It is **not** line-by-line proofreading,
**not** only a reviewer's job, **not** a separate PR step (it happens inline before
commit), and **not** optional for "small" edits (typos sometimes hide deeper
attribution errors).

### 1.1 Code-shape review belongs to the code-review discipline

This discipline verifies spec **prose truth** (line refs, counts, formulas, contract
claims, measurement framing, cross-doc drift). For maintainability / boundary /
single-source-of-truth review of production **code shape**, use the `review-code`
skill. Conversely, the §1.0 iron rule is **cross-cutting and canonical** — it governs
every *runtime* conclusion in a code review too (metrics, "N tests pass",
"byte-unchanged", gate PASS/FAIL): re-run the producing command end-to-end, both
states when a flag toggles, never read the committed artifact. The rule has one home,
not two that can drift.

---

## 2. What to verify

Each row names a bug class (or a standard); the right column states the verification
obligation. Every finding must cite one row by name. §2.5 gives the executable
companion hooks.

| Category | How to verify |
|---|---|
| **Source-of-truth hierarchy (doc-vs-command)** | For every code-grounded claim, name the underlying source of truth and run the command that re-derives it. Prefer the smallest mechanical check. A second prose doc is a pointer, not evidence; trace one level deeper to code, data, git history, or executable output. |
| **Line numbers** (`file.py:712-717`) | Open the file; confirm the cited lines contain what the spec says. Don't trust prior cycles. |
| **Metric / dotted paths** (`a.b.c`) | Resolve the path against a real payload (`jq` / `python3 -c`). |
| **Directional formulas** (percentiles, thresholds, deltas) | Substitute concrete example values; check the result *direction* matches the claim (e.g. for "gate `>= p10` excludes 90%", try a 5-element distribution and count). |
| **Function / class / constant names** | `grep`/`rg` the codebase; confirm spelling + location. |
| **Default values** (`= 0.5`) | Check the actual source default, not the value you intended to write. |
| **Cross-stack contracts** (assertions, wire formats) | Read **both** sides — producer AND consumer. Two distinct primitives: (a) each named field exists on the interface (`grep` each name); (b) every prose `{a,b,c}` enumeration is *complete* (count against the interface field-set). (a) does not imply (b). |
| **"X exists" claims** (functions, fields, env vars, files) | Confirm the asset exists at the claimed location BEFORE writing it as if it does. |
| **"X behaves like Y" comparisons** | Read X's code AND Y's code; verify the analogy holds. |
| **Code-vs-spec contract** (implementation phase) | When code claims to fulfill a spec section, read the spec contract AND the implementation side-by-side. Compilation / test-pass verifies mechanics, not contract adherence — confirm the signature, every `return` shape, and that the reason-code/enum set matches the spec exactly. |
| **Report-vs-data integrity** (measurement / closeout) | **Re-execute the computation that produces the number; don't read the committed result file** (§1.0). For a model-dependent / derived value, verification is re-running the producer and matching its fresh output. `jq`/reading the stored file is fidelity, never verification. For a `sha256`, recompute it. No producer left to run → flag the number un-verified. |
| **Execution-derived claims** (behavior under config) | For behavior keyed on config ("gate fires when X", "flag-OFF byte-equivalent"), RUN the code with that config; don't infer from reading. **Mechanism / attribution claims ("the win came from Y", "the residual is a Z problem") fall under §1.0**: an artifact merely *consistent* with mechanism Y does not verify Y if it confounds Y with a rival cause, reports only a downstream aggregate, or varies more than one factor. Drill to the component and isolate one factor (single-variable control) before the claim lands. |
| **Runnable-snippet expected-output alignment** | When a doc shows a snippet AND an expected-output block, execute or mechanically inspect the snippet's literal output against the expected. Don't stop at "it runs" — verify field truncation, ordering, count, rounding, identifier shape. |
| **Baseline/current measurement-surface alignment** | Before comparing a baseline to a current run, verify both sides are measured on the SAME surface: model name + version, corpus/index checksum, env flags, gate mode, query form, fixture cohort, and **determinism controls (seed / tie-break / thread-count / device)**. **Run-config pin:** any number produced by *executing* a program must record the surface that *determines* its output (at the cite site or in the artifact's metadata) so the §1.0 re-run is faithful. A neutralized knob is recorded as the neutralization *property* (`hash_seed_dependence: none`), not its volatile ambient value; a knob that still affects output stays in the recorded set. If surfaces differ, the result is INVALID for regression attribution unless it's explicitly a surface-delta experiment. **Write-time inline-pin convention:** every baseline number cited in prose carries its full source path inline, e.g. `0.6923 (baseline.json: retrieval.byFamily.comparison.recall@5)`; the pin prevents silent surface conflation when the same key exists under multiple top-level blocks (pre- vs post-rerank). |
| **Proxy-vs-direct-measurement** (regression / waiver gate design) | When a gate's pass/fail — or a failure's disposition (WARN / out-of-scope / known-gap) — is defined, the criterion MUST be a directly-measured `baseline` vs `treatment` delta on the **same input**, NOT a structural **proxy** for scope (coverage / language / family / rank-window). A scope-exclusion label is a claim *about the baseline* (it asserts the baseline ALSO fails) → RUN the baseline on that exact input to verify; never infer from a correlate. A surfaced regression may be ACCEPTED, but only as a named exception with rationale, never auto-suppressed by the proxy. |
| **Interpretive scope / framing claims** | When a claim summarizes a finding ("this surprised us", "X provides no benefit", "Y is the issue"), bound its SCOPE against the measurement: on which fixture / cohort / config / time-window. Singular framing of a multi-fixture finding is the trap. Verify by running the same query against EACH source and noting where the claim holds and where it doesn't. |
| **Root-cause stage attribution** (multi-stage pipelines) | Before authoring a fix scoped to Stage N, trace 1–2 representative failing cases upstream. For each prior stage, ask whether the wrong output is already present there or whether Stage N introduces it. Scope the fix to the **earliest** wrong stage — symptom-stage measurement is not root-cause evidence. |
| **Cross-reference drift after a fold** | After changing any count, status, row-id set, cycle/version number, scope phrase, or disposition, `rg` BOTH the old and new wording across the touched doc and the routing/status docs that repeat it. Catches the Class B failure: one section corrected while siblings keep the old claim. |
| **Verification axis variation** | When dismissing a candidate behavioral/predicate finding, the evidence must show ≥ 2 meaningful trigger shapes: the documented happy path AND one off-axis trigger. Applies to behavior/refutation claims, not pure fact checks. One shape only → keep the concern as a finding/open question. |
| **Fresh-reader ratification stance** | A spec cannot be approved on author self-review alone. Run the pass from a fresh-reader stance: treat prior cycle notes, claimed folds, remembered intent, and the author's own review output as untrusted until re-derived. After any fold, re-scan sibling occurrences of every changed number, status, row ref, path, call-site name. Author self-review is useful as **preflight**, not as approval evidence — label same-author/same-context output **PRE-FLIGHT** only. |
| **Dual-grounding (empirical + theoretical anchor)** *(reasoning standard)* | Every load-bearing conclusion / explanation / recommendation / proposed idea must carry BOTH anchors: (1) **empirical** — grounded in actual code/data, run + cited (`file:line` or command+output) with a concrete worked example (the §1.0 leg); (2) **theoretical** — the first-principles / domain mechanism that makes it true (the *why*, the general property), NOT a restatement of what the code does. The bug class is the **single-anchored claim**: empirical-only = a true-here number with no transferable *why* (fails to generalize when the scenario shifts); theory-only = an elegant mechanism that may not match real behavior. If only the number exists, add the mechanism; if only the principle exists, run/cite the code confirming it holds here. |
| **Industry-practice anchor (cited, dated)** *(reasoning standard)* | Any load-bearing claim about **external state-of-practice** — "the standard / mainstream / recommended / idiomatic way", a library / framework / algorithm / pattern / API choice, "SOTA", "best practice" — must be backed by a **live web source with a URL + access date** (`WebSearch`/`WebFetch`), NOT training memory (which has a cutoff and can confidently surface a stale option). Applies to prose AND code: when proposing an API / lib / pattern, cite the mainstream approach first, then justify following or deviating. **Scope guard:** triggers ONLY on claims whose truth-condition is *what the industry does*; claims about *what this repo does* stay on §1.0. Verify by naming the URL + access date and confirming the source supports *that exact* claim, not a page merely mentioning it. No source → it is a hypothesis. |
| **Design-vs-codebase reconciliation (reuse-before-redefine)** | When a design spec **proposes** a new artifact (type / enum / function / constant / flag / pipeline-stage / contract), reconcile it against the existing codebase **before approval** — this is the `review-code` discipline's Rows 1 (SoT) / 2 (boundary) / 4 (reuse) / 6 (no speculative abstraction) applied at *design* time. **Check**: for each proposed name, `rg` for an existing equivalent/synonym; for each proposed flow stage / integration point, `rg` the handler/call site to confirm it exists in the real execution path. An existing equivalent → the spec must reuse it or name the single SoT + justify divergence; a non-existent stage → re-anchor to the real integration point. The bug class is **redefine-without-checking** — reachable only by checking the design against code, never by a prose-only read. |

---

### 2.5 Mechanical-check companions

Executable companion surface for §2. Authoring time: run the relevant hook before
commit. Review time: prefer these hooks before prose judgment.

Mechanizability levels: **FULL** (a deterministic command proves the claim class
given the path/symbol/value), **PARTIAL** (a command proves existence/shape/output
but a human still judges semantic completeness), **JUDGMENT-ONLY** (a forced shell
command would mostly produce false confidence; the row needs reading / substitution /
causal reasoning).

| §2 row | Level | Mechanical hook | Pass condition |
|---|---|---|---|
| Source-of-truth hierarchy | PARTIAL | `rg -n '<symbol>' <path>` / `jq '<path>' <json>` / `git show <rev> -- <path>` | every code-grounded claim names a SoT command that exits 0 / returns the cited value |
| Line numbers | PARTIAL | `sed -n 'N,Mp' <path>` | cited range exists + contains the referenced block |
| Metric / dotted paths | PARTIAL (fidelity only) | `jq '<path>' <json>` confirms the quote; **value verification needs the producer re-run** (§1.0) | `jq` matches AND a fresh re-run reproduces the value |
| Directional formulas | JUDGMENT-ONLY | optional: substitute a tiny distribution in `python3 -c`/`node -e` | direction matches the prose |
| Function / class / constant names | FULL | `rg -n '<name>' <scope>` | ≥ 1 hit at the claimed location |
| Default values | FULL | `rg -n '<var>\s*[:=].*<value>' <scope>` | the actual default matches the cited value |
| Cross-stack contracts | PARTIAL | `rg -n '<field>' <producer>` + `<consumer>`; inspect the interface field-set | every named field exists both sides; every prose enumeration counted against the field-set |
| "X exists" claims | FULL | `test -f/-d <path>` or `rg -n '<name>' <scope>` | exit 0 / ≥ 1 hit at the claimed location |
| "X behaves like Y" | JUDGMENT-ONLY | optional: `sed -n` both implementations side-by-side | analogy holds across the claimed dimensions |
| Code-vs-spec contract | PARTIAL | spec: `rg` the contract term; code: `rg` the function/type/reason-code; run the narrowest contract test | cited names exist + tests pass; branch/boundary semantics judged |
| Report-vs-data integrity | PARTIAL (fidelity only) | fidelity: `jq`/`wc -l`; **verification: re-run the producer** (§1.0); `sha256sum` recomputed | fresh re-execution reproduces the value |
| Execution-derived claims | PARTIAL | run the cited command with the cited flags; for equivalence, produce artifacts + `diff`/`sha256sum` | exit 0 + output/diff matches the claim |
| Runnable-snippet output | FULL (literal) / PARTIAL (semantic) | execute the snippet, or inspect with `jq`/`python3 -c` | names/ordering/counts/rounding/truncation match the expected block |
| Measurement-surface alignment | PARTIAL | `jq` each inline-pinned path; extract surface metadata both sides | pinned values match + encoded surface dimensions equal (unless a declared surface-delta experiment) |
| Proxy-vs-direct-measurement | PARTIAL | run `baseline` + `treatment` on the SAME input + compare; `rg` the gate for any branch classifying by a structural attribute | every disposition decided by measured delta; no out-of-scope label without a baseline run |
| Interpretive scope / framing | JUDGMENT-ONLY | optional: run the query against each cohort/config independently | claim bounded to where it holds |
| Root-cause stage attribution | JUDGMENT-ONLY | optional: run the stage-isolated trace for representative failures | fix assigned to the earliest wrong stage |
| Cross-reference drift | FULL | `rg -n '<old>'` + `rg -n '<new>'` across the doc-set incl. routing/status docs | old wording 0 unintended hits; new wording in every required location |
| Verification axis variation | JUDGMENT-ONLY | optional: two inputs showing happy-path + off-axis behavior | ≥ 2 distinct shapes for the behavioral claim |
| Fresh-reader ratification | PARTIAL | check review provenance; `rg` old/new for every folded claim | same-author → PRE-FLIGHT; folded claims have no sibling drift |
| Dual-grounding | JUDGMENT-ONLY (empirical leg PARTIAL) | empirical leg reuses SoT/execution hooks; theoretical leg has NO mechanical hook | command reproduces the value AND a first-principles mechanism accompanies the claim |
| Industry-practice anchor | PARTIAL (existence) / JUDGMENT (mainstream-ness) | `WebSearch`/`WebFetch` + record URL + access date | a live dated source supports the specific state-of-practice claim |
| Design-vs-codebase reconciliation | PARTIAL (existence FULL; reuse JUDGMENT) | `rg -n '<name-or-synonym>'`; `rg` each proposed stage's handler/call site | each proposed artifact shows no equivalent (or an explicit reuse/divergence note); each stage resolves to a real call site |

---

## 3. When to apply

- **Authoring a new spec section** → pass on the new content.
- **Amendment / fold** → pass on *every* amendment before commit, not just high-severity ones.
- **Single-line typo / "quick" wording cleanup** → still pass; wording shifts meaning, and typos co-locate with attribution errors.
- **Re-using prior text verbatim** → still pass; the prior text may have been wrong in a way the original reviewer missed.
- **Before writing code-grounded prose** → first list the commands that will establish each load-bearing fact. No command → mark the claim as interpretation and bound it.
- **Design / architecture spec** → apply this discipline for prose truth AND run the "Design-vs-codebase reconciliation" row (`rg` each proposed name for an existing equivalent; confirm each proposed stage resolves to a real call site) before approval.
- **After changing a repeated claim** → cross-reference `rg` for BOTH old and new terms before commit (counts, version numbers, id lists, deferred/closed labels, router rows are drift-prone).
- **Any prose citing a baseline / measurement number** → apply the inline-pin convention: every number carries `(<source-path>: <dotted-path>)` inline.
- **Measurement data / closeout report** → re-run to confirm reproducibility (execution-derived row) / every cited number traces to data in seconds (report-vs-data row).
- **Baseline / regression / acceptance-runner changes** → prove baseline and current are same-surface before classifying any failure as regression / waiver / drift.
- **Batch fixture / registry authoring (N large)** → a one-time programmatic verifier substitutes for manual walk-through.

---

## 4. Anti-pattern: "looks right because it sounds right"

Plausibility is the trap. If a claim *feels* obviously right, that's exactly when to
verify — the obvious cases are where the author skips checking.

- **"Test passes → code is correct."** Tests verify the assertions they encode, not the contract. A test asserting a WRONG expected value passes happily.
- **"My report numbers come from the JSON, so they're right."** They may be from the wrong column / wrong config run / a stale cached file. Re-derive in the moment.
- **"Another doc already says X, so X is true."** Documents preserve claims, not proof. Use the other doc as a search hint, then verify against code/data/git/output. If two docs disagree, the disagreement is itself a finding.

---

## 5. Worked examples (generic)

- **Line-number attribution.** A spec cites a mechanism at lines 192/222/283 (which
  are dict-guards); the actual mechanism is a numeric-leaf check at line 154. Caught
  only by opening the file. Lesson: cite what the file says, not what feels right.
- **Formula direction.** "Gate `delta >= p10` excludes 90% of agreement" — but `p10`
  is the 10th percentile, so `>= p10` *admits* 90%, the opposite of intent.
  Substituting a 5-element distribution and counting catches it instantly.
- **Confounded mechanism claim.** "The win came from the reranker" — but the cited
  artifact reports only the fused top-5 (reranker + projection together) and the run
  also changed the corpus. Consistent with the claim, but it confounds two causes and
  varies two factors. Drill to per-channel scores + a single-variable control before
  the claim lands.
- **Measurement-surface mismatch.** A baseline froze metric X under config A;
  the regression test ran current under config B → false failures misdiagnosed as
  "environment drift". Proving same-surface first dissolves the phantom regression.

---

## 6. Cost-benefit — two distinct usage patterns

- **Author-side per-section check (primary).** Walk the section you just modified
  before committing: **5–15 min**. Cheaper than the review cycle it prevents (a bug
  caught at next review costs an amendment commit + repeated reviewer time +
  future-reader doubt).
- **Reviewer-side full-spec scan (secondary, more expensive).** Walk each §2 category
  against every claim regardless of which cycle introduced it: **~60–90 min** on a
  1000–1500-line spec; `grep`-batched checks scale sub-linearly. Apply before final
  approval, when a review found a bug in an un-touched section (signal others may
  carry similar bugs), or when taking over someone else's spec.
- **Anti-pattern: confusing the two.** Author skipping the per-section check because
  "it's small" → bugs leak forward. Reviewer checking "only what changed this cycle"
  → latent bugs in untouched sections persist. Complementary; neither substitutes.

---

## 7. Relationship to external review

External review by another reader catches the author's blind spots (design judgment,
architectural fit, coverage gaps). The walk-through is the author's **own pre-commit
check** — it catches the author's *unverified claims* (facts, math, line refs in
their own text). Skipping the walk-through forces external review to do work that
should have been caught at authoring — that's how a 1–2 round review turns into 3–6.

---

## 8. Stability pledge

A new bug-derived row requires **all three**: (1) a concrete bug class the existing
rows do NOT cover ("an existing row would have caught it if applied" is application
failure, not new coverage); (2) ≥ 1 worked example showing the existing rows are
structurally insufficient; (3) cost-benefit — a new row costs every future reader's
attention forever. The anti-pattern this guards against is
**discipline-as-evergreen-checklist**; at maturity, **application discipline matters
more than framework expansion**. Before proposing a row, first try to classify the
issue under the existing rows — most new findings are missed applications.

**Owner-directed standards are a separate, exempt category.** The 3-part bar governs
the *agent* reflexively adding bug-derived rows; it does not gate an owner setting an
explicit authoring/reasoning standard. The **Dual-grounding** and **Industry-practice
anchor** rows are such standards — reasoning/communication contracts, not
cycle-caught bug classes — recorded as standards for provenance honesty rather than
presented as bug-derived.
