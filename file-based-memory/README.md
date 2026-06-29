# file-based-memory

A persistent, resumable **file-based memory** for agentic coding, packaged as a
Claude Code plugin. It lets an agent cold-start a repo with zero conversational
context and keeps long-running work from drifting as the context window fills.

It generalizes a battle-tested in-repo mechanism into a repo-agnostic kit:

- **Router entrypoint** (`AGENTS.md`) — points at truth, never stores it.
- **Operational dashboard** (`CURRENT_STATUS_AND_NEXT_STEPS.md`) — what's active, blockers, exact next commands.
- **Four-layer durable memory** (`project-memory/{architecture,decisions,experiments}.md`) — invariants, rejected approaches, measurement trail.
- **Size discipline** — 5–10 lines per entry, link to docs instead of compressing them (optional precommit gate).
- **Supersede, don't delete** — wrong/old entries keep a trail.
- **Auto-checkpoint cadence** — a non-blocking `Stop` hook nudges you to checkpoint when commits pile up.

## Install / try

Local test (no install):

```bash
claude --plugin-dir ./file-based-memory
```

Self-use across all your repos (auto-load): drop this directory under
`~/.claude/skills/` so it loads as `file-based-memory@skills-dir`.

Validate before sharing:

```bash
claude plugin validate ./file-based-memory --strict
```

## Use

- `/file-based-memory:save-status` — run the checkpoint protocol on demand.
- The skill auto-activates when you bootstrap memory, checkpoint, or resume.

## Config (env)

- `SAVE_STATUS_CADENCE` — cadence-hook commit threshold (default `5`; `0` disables)
- `CHECKPOINT_FILE` — dashboard filename (default `CURRENT_STATUS_AND_NEXT_STEPS.md`)

## Prior art

This follows the file-based-planning / "Manus-style" lineage (e.g.
`planning-with-files`). See `skills/file-based-memory/references/prior-art.md`.

## License

MIT.
