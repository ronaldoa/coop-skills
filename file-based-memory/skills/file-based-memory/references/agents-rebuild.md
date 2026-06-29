# Rebuilding the router (`AGENTS.md`) from its sources

`AGENTS.md` is the **handbook** layer of the four-layer model (see
[memory-model.md](memory-model.md)). It is *reconstructible* from underlying sources —
losing it costs rebuild time (2–4 hr by an experienced agent), **not** engineering
memory. The truly irreplaceable layers are `CURRENT_STATUS_AND_NEXT_STEPS.md` and
`project-memory/{architecture,decisions,experiments}.md`. This split is the point:
treat the router as a derived index you can regenerate, and never let it accrue truth
that exists nowhere else.

Read this when: `AGENTS.md` was lost and `git checkout` isn't an option (fresh fork,
cross-repo copy); a maintenance audit needs to verify each section is fresh against its
source of truth; or you're adding a section and need to decide whether it belongs in
the router or in a layer it should point at.

## Each section = a source of truth + a rebuild cost

A router has a small fixed set of sections. For each, the content is *derived* from a
named source — so rebuilding is re-deriving, not authoring from memory.

| Section | Source of truth | Rebuild cost |
|---|---|---|
| Project Overview | `README.md` + project knowledge (1–2 sentences) | trivial |
| Session Bootstrap | the four-layer model — copy the reading order from [memory-model.md](memory-model.md) | trivial |
| Commands | the build/test/run/lint manifest (`package.json` scripts, `Makefile`, `justfile`, …) | low |
| Architecture | the actual source tree — read **structurally**, cite `path:line`, do NOT inline implementation | medium (1–2 hr) |
| Workspace / repo map | the workspace manifest (`pnpm-workspace.yaml`, `Cargo.toml`, monorepo config) | trivial |
| Key Config | the env template (`.env.example`) cross-checked against the code's config defaults | low |
| Design Specs (doc router) | a survey of all `docs/**/*.md` + judgment | **highest** (1–2 hr, Explore agent + review) |
| Maintenance rules | this file + the four-layer model | trivial |

## The doc-router section (the hard one)

This is the only section that needs an agent-driven survey. The recipe:

1. Enumerate: `find docs -type f -name "*.md" | sort`.
2. For each doc read **only the first 10–15 lines** (frontmatter + first heading +
   first paragraph) to determine status — one of `ACTIVE / ARCHIVED / SUPERSEDED /
   CLOSED / RATIFIED-DESIGN / DRAFT / PLAN / README / AMBIGUOUS`. **Never read past
   line 15** — that's compression, not routing.
3. Group by directory. For each `ACTIVE` doc relevant to a future change, write one
   line: `<path> — read when <one phrase>`. For each `ARCHIVED`/`SUPERSEDED` doc
   *plausibly mistakable for current*, one line with an explicit marker.
4. Identify same-topic competing docs; name the canonical one in an "Authoritative
   resolutions" sub-section.
5. Add a "Do NOT read as current" wrap-up listing archive dirs + partially-shipped
   DRAFTs.

Run the survey with a read-only **Explore** subagent (`subagent_type: Explore`) to keep
the main context clean. Hard constraints for the prompt: read ≤ 15 lines/doc; do NOT
summarize content (the "read when" phrase comes from title + first paragraph); read in
parallel; cap the report length.

**Router-row contract (size discipline for this section).** One route = one line:
`<trigger> → <doc path> + STATUS label (+ at most one load-bearing clause)`. Phase
trajectories, eval numbers, commit chains, and session narrative do NOT belong here — a
status *change* updates the label (DRAFT → RATIFIED → CLOSED), it never appends
narrative to the row. This is the [enforcement.md](enforcement.md) doc-budget gate
applied to the router.

## What does NOT belong in `AGENTS.md` (route, don't store)

If you want to add any of these, it's the wrong file — point at the layer that owns it:

- Detailed spec content → lives in `docs/`.
- Status narrative inside a router row → update the STATUS label; narrative lives in
  the dashboard or the doc's own Status block.
- Calibration / baseline numbers → `project-memory/experiments.md` (or baseline files).
- Rejected approaches + rationale → `project-memory/decisions.md`.
- "Do not change" invariants → `project-memory/architecture.md`.
- Operational status / blockers / next commands → `CURRENT_STATUS_AND_NEXT_STEPS.md`.
- User personal preferences → user-/personal memory.
- Tool-specific behavior → a tool overlay (e.g. `CLAUDE.md`), which *references*
  `AGENTS.md`, never duplicates it.

The test: an `AGENTS.md` edit that adds a doc-content summary, a threshold table, or a
"we tried X and rejected it" note is misfiled. Move it to the layer above and leave a
one-line route.

## Maintenance triggers (audit cadence)

Update the matching section when: a new build/test command lands (Commands); a new env
var / config knob (Key Config); a new workspace (repo map); a new doc under `docs/`
(doc router — add a "read when" entry); a doc moved to `archive/` (mark ARCHIVED +
update Authoritative resolutions); a design slice ratified (mark RATIFIED); an
architecture refactor — new/removed subsystem or moved boundary (Architecture).

## Full rebuild from scratch

If `AGENTS.md` is gone and `git checkout` isn't an option:

1. Create the skeleton sections (per the table above).
2. Fill Project Overview + Session Bootstrap + repo map + Maintenance rules from this
   recipe + the four-layer model (~10 min).
3. Fill Commands from the build manifest (~15 min).
4. Fill Key Config from the env template + code defaults (~15 min).
5. Fill Architecture by reading the source tree structurally (~1–2 hr).
6. Fill the doc router via the Explore survey above (~1–2 hr incl. review).
7. Cross-check against the four-layer model so Session Bootstrap + Maintenance rules
   align and the router *points at* truth rather than restating it.
8. First commit pins the source-of-truth files used, so the rebuild is auditable.

Total: **2–4 hours**. Compare against the irreplaceable layers, which no recipe can
regenerate — that asymmetry is why the router is allowed to be lossy and the durable
memory is not.
