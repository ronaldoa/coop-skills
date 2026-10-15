# Prior art & attribution

- **File-as-memory / "Manus-style" agents** — write important state to disk and re-read it;
  the context window is a cache over durable files.
- **`planning-with-files`** (OthmanAdi) — a portable skill keeping plan / findings /
  progress files across context resets, with a save cadence. This plugin shares that core
  and adds the routed entrypoint, memory split by decay rate, supersede-don't-delete, per-line
  handoff blocks, and the precommit gates. https://github.com/OthmanAdi/planning-with-files
  (accessed 2026-06-28)
- **Anthropic Agent Skills + Plugins** — the packaging (`SKILL.md`, `plugin.json`,
  `hooks/hooks.json`). https://code.claude.com/docs/en/skills (accessed 2026-06-28)

Marketing figures that circulate with this lineage (e.g. acquisition valuations) are
unverified and not claimed here.
