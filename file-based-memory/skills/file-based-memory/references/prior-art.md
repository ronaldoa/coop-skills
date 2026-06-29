# Prior art & attribution

This skill did not invent file-based agent memory. It packages a discipline that has
emerged independently in several places, generalized from a working in-repo
implementation.

## Lineage

- **File-as-memory / "Manus-style" agents** — the broad idea that an agent should
  write important state to disk and re-read it, rather than relying on the context
  window alone. The context window is treated as a cache over durable files.
- **`planning-with-files`** (OthmanAdi) — a portable skill that maintains a small set
  of markdown files (a plan, findings, a progress log) across context resets, with a
  "write anything important to disk" rule and a cadence for saving. This skill shares
  that core and adds: a routed entrypoint, a four-layer durable memory with distinct
  decay rates, supersede-don't-delete history, and an optional size-discipline gate.
  https://github.com/OthmanAdi/planning-with-files (accessed 2026-06-28)
- **Anthropic Agent Skills + Plugins** — the packaging substrate (`SKILL.md`,
  `.claude-plugin/plugin.json`, bundled `hooks/hooks.json`). See
  https://code.claude.com/docs/en/skills and `/en/plugins` (accessed 2026-06-28).

## What's original here

The contribution is not the idea but the *structure*: separating the index (router)
from truth, splitting memory by decay rate (operational vs invariant vs decision vs
experiment), making "supersede don't delete" a rule, and pairing it all with two
hooks — a non-blocking cadence nudge and an optional size-discipline gate.

## A note on claims

Earlier descriptions in this lineage have carried strong marketing claims (e.g.
specific acquisition valuations). This skill makes no such claims; treat any such
figure as unverified marketing, not a technical fact.
