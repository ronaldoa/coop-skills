# Engineering Principles (portable across projects)

Stack- and domain-independent rules from this project's memory + commit log; every *italic instance* is a
defect we actually paid for. **Loaded every session, in full — standing rules of engagement, not reference
material.** §-IDs are cited from source comments and must stay stable. **Ceiling: 331 lines** — adding a
principle means merging or deleting one, not appending.

> **Before adding, map the candidate onto what is already here — duplicate / complement / conflict.** Most
> "new" principles are a clause missing from an existing §, and land better inside it than beside it; the same
> check catches the inverse error of citing a clause nobody ever wrote.

- ✍️ any gate → §1 · 🗑️ deleting a protocol/field/code path → §1.3 §1.4 · ➕ **adding** one → §1.11 · 🚢 **calling a step done → §1.6**
- 🔌 changing a cross-boundary contract → §2.1 · 🤖 LLM in the loop → §2.2 · 📊 reporting a measurement → §3 · 📐 **designing** → §6.2 (complete design, sliced build)

## §1 Verification and Criteria

### 1.1 A new gate must be mutation-tested, or it may be falsely green
Break the production code on purpose; if the assertion doesn't go red, it's a fake nail. Hardest-edged for
**newly built verification machinery** — a gate has no gate above it, so mutation is the only verification.
Includes **compile-time** nails (absorbed §2.4): mutate a production file, run the type checker, record the
error code at the declaration site — whether test files type-check varies by project, so an unverified type
guarantee may be entirely vacuous. **Mutate each nail the moment you write it, never batched at the end of
a slice**: a false green you keep building on costs the whole slice (§1.6's sizing logic), and once N nails
land together, one red no longer tells you which. ⚠️ **Verify the mutation actually mutated** — one that leaves
production behaviour unchanged reports a false GREEN, and "the gate held" is the worst lesson to draw from it.
⚠️ **"THE SUITE WENT RED" IS NOT "MY NAIL WENT RED" — record which ARM.** A mutation can change behaviour and redden
something while the criterion you just wrote stays green; the ledger entry then reads verified and the nail is not.
*Instance: a loosened discriminant reddened a NEIGHBOURING arm (`[]` vs absent) while the new arm never fired —
covering it needed a different edit. Twice in one session; the second landed red for a BETTER reason than predicted
(a vacuity guard, not the ∀ check it claimed), which is the same bookkeeping error with a happy ending.*
⚠️ **A guard that cannot fire on CORRECT code is unobservable by ONE mutation**: deleting it alone comes back
green — an EQUIVALENT mutation, not a missing nail. Nail it as a PAIR (break what it guards, with the guard and
without) and record which arm each criterion covers; "nail still owed" sends the next reader hunting a defect
that is not there.
*Instances: three false greens from one pixel oracle (above the fold / unstubbed dependency / a "positive
control" that does not render); D-61's criterion, run on the spot, caught the swap firing TWICE mid-slice; a
"naive sweep" mutation that built an EMPTY set, deleted nothing, and came back green; a `traits: []` mutation
onto a fixture that was already `[]`.*

### 1.2 The control group itself can be fake
"Green" means genuinely passing, **never executed, or never decided**: a legacy field masking the native path in a
compatibility window; read-side-only fixtures letting every write-side mutation survive; a "positive control" with
no effect on the outcome. End-to-end acceptance **runs production functions on both ends** (write → store → read).
⚠️ **A score with an abstain state is maxed by always abstaining** — an all-`UNCERTAIN` classifier commits zero
false merges AND zero false splits. Gate the abstention rate itself, plus a positive control that must decide.
⚠️ **A check placed ABOVE the code that POPULATES it inspects an empty collection** — green, and never executed.
Ask of every new guard: is what fills me above me, or below?

### 1.3 Assertions silently decay into tautologies
`expect(x).not.toContain("legacy_thing")` is permanently green once the producer is deleted. Ask of every
assertion: **under what circumstances would this hold unconditionally?** Deleting a protocol ⇒ rewrite every
by-name negative assertion against the new discriminant; a new fixture format ⇒ add a **vacuity guard**
(`captureVersion`) so old corpora cannot make the new criterion vacuously green.

### 1.4 A regression corpus can only prove "old inputs still work"
Replaying recorded bytes is **structurally blind to protocol additions and deletions** — old samples still
carry the legacy fields. ⇒ **Re-record fixtures on every wire/storage protocol change**, and record a **twin
pair differing only in that one field**, compared byte-for-byte with random values stripped.

### 1.5 "Every call site must remember to do X" is a design defect
Don't add one more test — **eliminate the choice**: bind the always-paired steps into one function, plus a
**structural assertion** forbidding bare calls to the underlying API, so future call sites are covered too.
*Instance: a sidecar needed wiring at 3 emission points; we missed the two largest and unit tests stayed green
(they covered the factory and one other point). Only live running caught it.*
**A POST-CONDITION beats pre-checks**: pre-checks say "I intend not to break anything", an assertion over the
OUTPUT says "I did not" — and it holds for every later edit, not just the paths you thought of (§1.3's vacuity
guard is the special case where the output is "did I run at all").
**TYPE form — a union/enum, never an empty string, sentinel or optional field.** `url?: string` legalizes
`{}`/`""`/a dead address, so every reader owes a falsy guard and one forgets; a `{kind}` union makes the reader
that forgot **fail to compile**. Where the type cannot refuse (`Partial<Record<Kind,Impl>>` answers a missing
entry with empty), add a structural criterion. *Instance: 7 nav entries → a union, and the compiler named 3
render sites nobody had listed.*

### 1.6 A step is done only when a real run says so — so keep steps small and revertible
**Slice by a complete user flow.** Fix its inputs, expected result and completion criteria before implementation;
run request → final output early, including replies and state restoration where applicable. Contract/compiler/consumer
milestones are intermediate progress; **each step ends in a real end-to-end run**, using production functions at both ends (§1.2).
Split until each step can run e2e and be reverted independently (flag-gated / one commit). Unwired work still owes a committed
baseline against the nearest real path (§3.1). **After a local fix, rerun the same flow** to catch displaced failures.
*Instance: an intent migration's layer checks missed mixed-turn disclosure, then a menu reply reused the wrong subject.*
Emission wiring and config errors escape offline checks. **Read the port from the process's own logs**;
we once probed a process without the code under test.

### 1.7 Never hand-write the SHAPE of test data — but DO construct the INPUT
A hand-written payload gets **recognized by production code while yielding no readable fields**, degenerating
the assertion into `0 > 0` — which passes on an empty object. ⇒ Shapes come from a **builder in the shared
contract** (type-checked file) or a **real recording**; no shared contract ⇒ real capture, never fabricate.
⚠️ **THIS IS NOT A BAN ON WRITING NEW CASES, and read alone it gets misread as one.** The line is
**shape vs input**: a *payload/expected structure* is fabricated (forbidden — nothing forces it to match the
contract, and a wrong one passes); a *case input* — the query string, the user action, the field VALUE — is
**constructed on purpose, from what you need to test**, and §3.1 REQUIRES it ("inputs, never payloads";
selecting cases only from what a corpus happens to contain is the circular gate). ⇒ Construct the input,
derive the shape. A refusal to add a case "because §1.7" is this principle inverted into the defect §3.1 names.

### 1.8 A branch that only fires in a rare state must be driven there deliberately
If a budget gate / degradation banner / error branch never fires under production parameters, its criterion records
only "happened not to be exercised" and the mutation survives green. ⇒ Treat the threshold as **instrumentation**:
move it to a firing value, assert, and comment that this is not a claim about production. (3+ in this family.)

### 1.9 Two instruments disagreeing ⇒ suspect the instruments; with ONE, nothing triggers that suspicion
Assume a false positive before assuming production is broken; criteria read **authoritative fields**, never a surface
signal — an id's spelling, or a tag's presence standing in for identity. Alone, an instrument has nothing to disagree
with, and **its defect wears the symptoms of the thing measured**: a count that is low, a diff that is huge, a rate of
100%, a length of 0. Commonest form = bound to a convenient VIEW, not the lossless layer (absorbed §3.4: diagnostics
read the pipeline's OUTPUT, never raw data — projection is intentionally lossy). ⇒ Run a new comparator/probe on **one
already-known answer** before pointing it at N; until it has, its reading cannot carry a RECOMMENDATION. *Instances: a
diagnostic assuming a child id carries its parent's prefix, whose own tests minted ids satisfying it; six comparator
defects in one benchmark — a lossy view taken for the parser's output, values compared as RENDERINGS (`str(Decimal)` vs
`float`), typed dimensions filtered away — which read as "this library cannot be the producer" and INVERTED that
advice, until one known-answer case exposed three at once.*

### 1.10 Identity inferred from a SIDE EFFECT — or from a DESCRIPTION — breaks; stamp it in the data
⇒ Record the producer; never infer identity backwards. *Side-effect form: "a capture file exists" witnessed "path A ran";
a second path began producing them, and the misjudged branch deleted fresh data.* **DESCRIPTION form** — an error's fix
text or a comment: one prescription serves many artifacts ⇒ description→identity is **many-to-one, not invertible**. Read
what the code LOADS, not the prose; not staleness (§6.1) — that comment was CORRECT, about **another file's** object.
*Instance: one debt list collapsed three times in a session — error text, that comment, and the author breaking the rule while stating it.*

### 1.11 A new field is not a channel until a reader acts on it
Declaring a field / enum member / flag states intent; it does not create a path. Between producer and reader each
hop can drop it **while looking locally correct**: a sanitizer stripping unknown keys off an untrusted payload, an
`isKind(v) ? v : DEFAULT` guard folding the new value into the majority one, a signature that still takes only a
string. The diff shows none of it — every file is defensible alone. ⇒ For each new field OR invariant, walk
**producer → every hop → the reader whose BEHAVIOUR changes**, and pin that far end. **The default is the dangerous
hop**: it makes the new producer indistinguishable from the old, so every criterion over that field is permanently
green (§1.3) — including the one added to watch it. An invariant that lives only in prose is the same defect with
zero hops: name the code that goes red when it is violated, or it is a wish. ⚠️ This is a REVIEW question, not only
an authoring one — "is the new code self-consistent?" cannot see it; "does this value still exist three files later?"
can. ⚠️ **It gates CODE, never DESIGN**: a member with no reader yet stays NAMED in the design, with its slice (§6.2).
*Instances (both caught reviewing a design against the tree, before implementation): a producer stamp declared
in a union, destructured off by the payload sanitizer one layer down, then defaulted back to the old producer by the
compiler's type guard; a resolved-slots field added to a rewrite contract whose only consumer still took a bare string.*

## §2 Design Contracts

### 2.1 A cross-boundary contract has one definition; mirrors will drift
Not "don't repeat yourself" — **nothing forces two definitions to agree, so "only added it on one side" is silent**.
Shared types are defined once and imported by each side; "the client must not import server modules" is
correct but "therefore hand-copy" is not — lift the contract into `shared/`, and move whichever legacy mirror you
touch instead of growing it. ⚠️ A shared type that cannot REFUSE a bad state is half a contract (§1.5's type form).

### 2.2 The LLM proposes; deterministic code adjudicates
Dividing line = **does a unique correct answer exist**: yes → code; open semantic judgment → LLM. **Dates and numbers
never originate from an LLM** — symbolic intent only (`{grain:"quarter",rel:"last"}`), code resolves the values.
**Understanding** first, never **computation**; every LLM gate has a deterministic fallback. **It states what it
UNDERSTOOD, never OUR rules**: what code derives (a family change, which slots ship) stays out of the prompt.
⚠️ **BUT A DATE THE USER WROTE DOWN IS TRANSCRIPTION, NOT COMPUTATION, and `originate` is the word doing the work.**
Its unique correct answer is in the SENTENCE, not on the clock ⇒ by this §'s own dividing line the model may READ IT
OUT. The permission needs a GATEKEEPER or it is "the model may emit dates" with better wording: **refuse a transcribed
value that is not literally in the query.** ⚠️ **And the mirror-image failure is the PARSER's** — code that recognises
ONE end and INVENTS the other is worse than code that abstains, because it overwrites an answer the model got RIGHT; a
return type that cannot say "I matched one end" / "I am not sure" forces that invention. *Instance (D-234): `from A to
B` matched `from A`, invented today as the far end ⇒ a 2¾-year window, silently, for a six-month ask.*
**A PROMPT HAS NO SCOPE** — one edit shifts every output field, so the measurement must cover **every axis that
prompt produces**, not the one you meant to move: there are only axes you measured and axes you did not.
**AND NO LOCALITY: WHERE a rule sits changes what it moves.** ⇒ resolve an axis red by same-code A/B, never by
judgement; pin the **compiled output** too — a model can emit its own field right while moving which task carries
a NEIGHBOURING one. *Instances: a rule for ONE field scored 15/15 while the same edit took `required_data`
10/12 → 3/12, peers silently unfetched, every criterion green (`promptAxisGuard.ts`: axes from the output TYPE,
the intended one declared, any other fails). Then one bullet, wording unchanged, broke three unrelated things by
ADJACENCY — moved to its block's end, a false positive on the motivating case went 2/10 → 0/10, its own 10/10.*
**AND NO AUTHORITY OVER ITS OWN EXAMPLES — a rule the demonstrations contradict is ABSENT, not weak.** Few-shot
examples carry the output distribution and format; prose *describing* that distribution does not move it. ⇒ **the rate
a field comes back at is the rate the examples DEMONSTRATE**, which makes it a **free, static** prediction: count the
demonstrations before spending a call. Same for SHAPES — one only described comes back on the exact sentence the rule
spells out, and nowhere else. *Instance: one prompt, three fields, measured in one window — `operation` demonstrated
55/55 came back always (and is absent from the output skeleton); `metric.name` 15/55 = 27% came back 20–23%;
`requirements[]` 0/55 came back **1/225**, so the 578-byte rule teaching it was judgeable as dead at zero cost.
Completing all 55 demonstrations took it to 16/16, and the canonical 2-entry shape — described in prose, demonstrated
nowhere — arrived only after ONE example was added (6/16 → 10/16). Four separate rule↔example conflicts were authored
while fixing rule↔example conflicts; a structural criterion caught all four, eyes caught none (§1.5).*

### 2.3 Degrade additively, never subtractively
Deleting on a guess makes correctness contingent on the guess, and a wrong guess = **silent data loss with no
disclosure**. **Reorder only, never delete** — a wrong guess then costs relevance, not existence. Same family:
retiring a producer does not retire the reader; data doesn't vanish because code did. **Argue from readers, not
names.** Third member: **a state transition re-points every reader of that state** — `!== "PROPOSED"` meant
"adjudicated" until a confirm made it mean "all of them", and the rebuilder silently reverted real adjudications.
Changed a state machine ⇒ ask who still reads the old meaning.

## §3 Measurement and Adjudication

### 3.1 Silence in the corpus is not evidence — cases come from the target contract, not current reach
A corpus's silence has two indistinguishable causes: the product cannot reach that state, or nobody happened
to use it that way. **A case is admitted by the intended contract and known failure space, never by what the
current router / registry / planner / executor can already serve** — selecting by current capability is a
circular gate: unsupported shapes are dropped before the run, the measurement necessarily returns zero, and
that structural zero is misreported as evidence the capability is unneeded. If the feature doesn't exist yet, the
first observation is a **committed red / unsupported baseline**, not the absence of the query. Keep a **historical**
corpus ("do old inputs still behave the same?") separate from a **design/acceptance** one ("can the new contract
handle every required shape?"); historical silence cannot veto a design case. For a derivable defect, **construct
the input and test it**: (1) **inputs, never payloads** (§1.7); (2) the derivation **points at a specific line**,
not "feels wrong"; (3) the case is **committed**. ⚠️ A committed case may turn an existing criterion red as designed —
**replace that criterion** (it measured the absence of one shape), don't relax it. *Instance: a mechanism
measured 0/202 across 285 offline rounds, on which we wrote "insurance, not an optimization"; one constructed
sentence bit on the first try, reproduced twice ⇒ conclusion void.*
⚠️ **AND A THIRD CAUSE — NOT ABOUT THE CORPUS BUT ABOUT WHICH COPY YOU HOLD.** An UNCOMMITTED corpus (a
gitignored pool, a local cache, an object store outside the tree) **is one per machine**, so "these bytes do not
exist" is a fact about one checkout, never about the project — and it reads exactly like the structural zero above.
⇒ Ask of every fetched artifact: **would re-fetching return the same bytes?** Yes ⇒ a **CACHE**: keep it out of the
tree and commit the re-fetch instead. No ⇒ an **OBSERVATION**: commit it the moment it is captured (only the ones a
committed artifact depends on), or the evidence dies with that disk. *Instance: 15 of 25 cases were ruled
unreplayable because 12 digests "were gone"; they were intact on another machine, and the run that judged them had
started from an empty pool — its own reading said `prune 0 dropped` against a 10-round retention.*
⚠️ **AND THE SAME CIRCULAR GATE HIDES IN THE DENOMINATOR** — not in which cases you admit, but in which
AXES you can score at all. A coverage table can only count what the expectation TYPE expresses, so an axis
the contract has no field for does not read as **0%**; it **does not appear**, and nobody funds it. ⇒ Derive
the axis list from the OUTPUT, ask which of them the contract can state, **design the missing fields BEFORE
quoting a percentage**, and make the table a criterion so it cannot be hand-copied. *Instance: a hand-kept
table read `tasks` 92% — the COMPLEMENT of its real 9% — while every other cell in it meant "has gold".
`tasks` was that workstream's whole objective, so the roadmap scheduled it last; six contracts pinned five
sources each while the model emitted one or two tasks, and no gold could see the count.*

### 3.2 "Both arms are 0" = not observable, not "proven better"
The only writable claim is **"not observable at this sample size"** — and that size has a number: **0 events in n
observations bounds the true rate at ≈3/n** (95%). Compute it BEFORE sampling, to see whether the planned n could
ever support the conclusion you intend to draw; n=6 ⇒ 50%, an interval holding both "never" and "every other
time". Bursty or correlated observations shrink the effective n further. Flipping a default is justifiable by
**correctness contract + zero regressions**, never written up as "measured to be better". **An adjudication
question is not a measurement question**; state the two separately. Corollary: a metric whose run-to-run
jitter exceeds the difference between arms is not a signal (e.g. LLM output length).
⚠️ **AND A REPRODUCIBLE DIFFERENCE IS STILL NOT A DIRECTION** — observable and interpretable are separate gates.
A delta on a case with **no committed correct answer** supports "it moved", never "it got worse": both sides may
be wrong. ⇒ Read what the case COMMITS TO, and whether its gap already has an owner, BEFORE reasoning from a
reading on it; one whose target is recorded as unreachable (§3.1's committed-unsupported baseline) can only ever
report movement. *Instance: a one-word prompt edit moved 6 axis cells, reproduced by same-code A/B against a
measured noise floor — and 5 of the 6 sat on ONE multi-turn case whose own debt entry already said, in those
words, that this cell "can only report MOVED, never BROKEN". The delta was read first and the case's provenance
only when someone asked what the query meant; that ordering raised a false alarm and re-derived a filed
conclusion, and only 1 of the 6 cells ever carried a direction.*
⚠️ **COMPARING N CANDIDATES: ONE baseline, INTERLEAVED per observation.** A baseline per candidate pays for the
same information N times AND makes each comparison span a different window, so it measures drift as well as the
arm; arms run end-to-end have the same defect. Interleave, and a cheap `n` becomes legitimate for ELIMINATION
(never for direction) because each arm meets the baseline's own jitter inside one window. Let only the survivor
pay full price. *Instance: 4 candidate wordings, a fresh baseline each, ~2260 calls, none shipped — while a
zero-change re-record of that same baseline moved 6 of 120 cells on its own.*

### 3.3 Distributional facts ≠ causation; negative results must be recorded
"49% of examples omit the field" is a fact; "therefore the model will omit it" is a hypothesis — measured 62/62
emitted, rejected. ⇒ Measure before fixing, and file empty measurements under a dedicated **rejected / DON'T
BUILD** section of the knowledge index, or the same hypothesis returns in six months.

### 3.4 Don't treat raw byte volume as the volume downstream will process
"173k raw against a 30000 budget will drop 83%" — 13.8k survived projection, neither side of the budget bit, argument
void. **Measure the pipeline's intermediate states before naming a bottleneck** (which layer an instrument reads: §1.9).

### 3.5 Exact-pin tables > floor thresholds
A floor (`recall ≥ 0.9`) is a **contract**; two line-by-line pinned tables are an **instrument** — improvements also
turn them red (the diff is the evidence of the gain), and they catch "the mechanism quietly stopped running"
(tables become equal) and "the kill-switch is no longer a true fallback" (off-table drifts).

### 3.6 A blocker is a stack, not a single thing
Every layer we drilled through on one "coverage won't go up" problem exposed the next. ⇒ Measure
**saturation** first (where does it land if everything is fixed), then decide whether to drill layer by layer.

## §4 Troubleshooting

### 4.1 When an upstream returns an error, suspect your own request first
On 403/406/400, inspect the headers and parameter shapes you sent first. The other side telling you the
correct shape via its own error code is common — a 400 once handed back the correct field structure outright.

### 4.2 Distinguish failure modes: "returns empty" vs "returns wrong numbers"
Empty is explicit and downstream notices; **wrong numbers are silent** and travel to the user. Record the two
separately when evaluating a data source — only the latter is disqualifying.

### 4.3 Field names must be checked against a real response
Upstreams rename keys and docs disagree with what's returned. The symptom of the wrong field name is
**silently `undefined`**, then nulls all the way down.
⚠️ **AND A UNIT TEST CANNOT BUY THIS ONCE IT SHARES THE NAME WITH PRODUCTION.** Lifting the key into one
constant is right for every other reason (§1.5) — but the test then builds its fixture from the same
string production reads, so a typo moves BOTH sides together and stays invisible: mutating it is an
equivalent mutation (§1.1), green and meaningless. Offline you can only judge that the name is a **key of
the registry the ingest writes by**; the name↔upstream half comes from a real response and from nothing
else. *Instance: `ebit`→`ebt` on such a constant left 5/5 green — beside a comment in that very file
asserting the shared constant made a typo impossible, i.e. the criterion was authored next to a sentence
claiming it covered what it structurally cannot.*

## §5 Collaboration and Workflow

- **Never push automatically.** Pushing is a human action.
- **`git add` file by file**; never `git add -A` — it swallows untracked local files (e.g. `.env`).
- **Technical debt goes in one register, with stable IDs** (D-xx); plan documents carry pointers only.
- **Session handoff files** open with a fixed block — HEAD / baseline numbers (test count, type check) /
  reproduction commands / next-step candidates / 🛑 do-not-do list — then process notes. Those baselines must make
  it **obvious at a glance whether the environment is broken**.
- **In reports, separate "verified" from "not measured" into distinct sections.** The honest-boundaries section
  stands alone and has more long-term value than the conclusion itself.

## §6 Scope and Judgment

### 6.1 State the assumption, or stop and ask — an inherited claim is not a verified one
Don't hide confusion, and don't pick silently between readings: if two interpretations change the work,
present both. The dangerous case is not "I don't know" but **a claim adopted from a doc, a memory or a
previous session and then reasoned from as fact**. *Instance: a memory and five docs called `Equity/` an
"untracked copy of this repo"; it was a DIFFERENT repository, and the disproof sat in output I had already
read — 44 cases vs this repo's 42 in the same-named file, and a copy cannot differ.*
⚠️ **A RESTATEMENT IS A MIRROR (§2.1), and the clause it drops is the load-bearing one.** Four times in one
session: an axis written `A / B` collapsed to `A`; the other party's position weakened into a strawman that duly
lost; a premise adopted whole while the real hole was 4× bigger; a citation to a §-clause nobody wrote. ⇒ Quote
the original when acting on it, and offer the other party's own words as one of the options.
⚠️ **A CODE COMMENT IS HISTORY, NOT AN API** — best source for WHY, no evidence of what runs today (§1.10 has the other
failure). ⇒ Walk the real path: who writes this field, at which STAGE, does my reader run before or after that hop?
*Instance: one said an operation authority "must" still be built — it had shipped, and the axis read it a stage early.*
⚠️ **AND A SIZE READ OFF THE CODE IS A HYPOTHESIS THAT FAILS LOW** — it prices the slice AND fixes what acceptance covers.
⇒ Name the instrument already in the tree that refutes it in minutes, then **pin the number as a criterion; prose does not
bind** (§1.5; §3.1). *Instance: "two sources, 100 rounds" measured 12 sources / 409 pairs, 108 breaking that slice's own rule.*

### 6.2 Minimum implementation; and judge RULE-WORK by the work it unblocks, not by the rules it adds
**New findings do not automatically block the current slice.** Only defects affecting its promised user result, violating its
established contract, or invalidating acceptance evidence block it; record and schedule the rest, parking evidence-blocked work.
Prefer removing competing decisions, closing flow gaps and reusing instruments; do not build another mechanism for every edge case.
Judge rule-work by whether the next real work finishes faster and more credibly, never by rule count; rule revision must not become a standing prerequisite.
*Instances: repeated rules grew to 42% of `CLAUDE.md`; 3 candidate pairs became 7 doc sections and 5 criteria groups,
every finding real, while measurement never advanced.* Ask whether a senior engineer would call the implementation overcomplicated.
⚠️ **MINIMUM IMPLEMENTATION, NEVER MINIMUM DESIGN.** A design names every arm of the space it claims — each union member,
each owner, each EXIT for what does not fit ("out of scope", "in scope but unrepresentable") — with its boundary against
its neighbours; only the BUILD is sliced, and each deferred arm records the slice that lands it. Complete means **every
input has a destination** (an explicit exit counts), not a mechanism per edge case — so this clause does not license the
overbuilding above. Complete in BREADTH, not depth: an unbuilt arm is drawn to its boundary and destination, its insides
stay a sketch and a HYPOTHESIS that the first slice's readings revise. A design complete only for what ships today
cannot tell "not yet" from "never", and its gaps have no owner. *Instances (2026-10-08): checking the intent space for
"does every input land somewhere honest" found no exit for an in-domain question no family fits — it is folded into the
nearest one, invisible to every corpus (§3.1); a proposed grammar gave one meaning two arms (`Modal(EXPECTED, p)` /
`SpeechAct(_, expect, p)`), breaking identity and conflict keys — seen only with every arm side by side.*

### 6.3 Surgical changes: touch only what the request needs, clean up only your own mess
Don't "improve" adjacent code, comments or formatting; match the surrounding style even where you would choose
differently. Remove imports/variables **your** change orphaned — and when you spot unrelated dead code, say so
instead of deleting it (§2.3: retiring a producer does not retire the reader). The test: every changed line traces
to the request. *Instance: "add a design case and re-run the A/B" turned into six instrument changes; most were
load-bearing (the instrument WAS the deliverable, and broken), but two flags were features I added without asking.*
