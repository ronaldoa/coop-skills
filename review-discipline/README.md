# review-discipline

Two **structured reviewer-pass** disciplines, packaged as a Claude Code plugin. Both
apply a fixed verification taxonomy as an *executable contract* — run the check, don't
read the claim — and emit findings keyed to named rows with severity and a verdict.

- **`review-code`** — verifies a code change against architecture + contract hygiene
  (11 rows: SoT, boundaries, producer/consumer, dispatch, no speculative abstraction,
  validate-at-boundaries, executable hooks, config discipline, metric semantics,
  predicate coverage). Default target = the uncommitted git diff; also accepts paths,
  a commit/range, or a PR number.
- **`review-spec`** — verifies a spec/design/measurement doc's prose against the code,
  data, and math it describes (line refs, counts, formulas, contracts, measurement
  surface, cross-reference drift, design-vs-codebase reconciliation, plus two
  reasoning-grounding rows).

The shared spine is the **iron rule**: *no conclusion from reading or memory — run the
producing command end-to-end against current state; a committed result-artifact is a
claim under review, not evidence; run both states when a flag toggles.*

## Install / try

```bash
claude --plugin-dir ./review-discipline       # local test
claude plugin validate ./review-discipline --strict
```

Self-use across repos: drop this directory under `~/.claude/skills/` to auto-load as
`review-discipline@skills-dir`.

## Use

- `/review-discipline:review-code [paths | commit | range | PR#]` — default = uncommitted diff
- `/review-discipline:review-spec <path-to-doc>`

Both also auto-activate by task context.

## Prior art

Generalized from an in-repo `code-review-discipline.md` + `spec-authoring-discipline.md`
pair. Companion to the `file-based-memory` plugin.

## License

MIT.
