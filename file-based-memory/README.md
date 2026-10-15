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
- **Multi-workline mode** — several parallel lines of work each own a `§0` handoff block in their design doc; the dashboard becomes a router of lines.
- **Doc index + gates** — `> STATUS:` stamps, `path#symbol` pointers instead of line numbers, one live entry point per doc, checked by `hooks/doc_gates.py` before agent commits (criteria: `tests/test_doc_gates.py`).

## Install / try

Local test (no install):

```bash
claude --plugin-dir ./file-based-memory
```

Self-use across repos: install or load the **plugin root directory** (the directory
that contains `.claude-plugin/`, `commands/`, `hooks/`, and `skills/`). Do not copy
only `skills/file-based-memory/` if you expect `/file-based-memory:*` commands or
hooks to work; the skill subdirectory by itself only carries the skill instructions
and templates.

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
