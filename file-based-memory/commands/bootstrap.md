---
description: Install the file-based-memory scaffold into this repo — router, dashboard, and four-layer durable memory — filling what's known from the repo and leaving honest TODOs for the rest
argument-hint: [optional path to repo root; defaults to the current working directory]
---

Target = `$ARGUMENTS` if given, else the current working directory.

1. **Don't clobber.** If `AGENTS.md`, `CURRENT_STATUS_AND_NEXT_STEPS.md` or
   `project-memory/` exist, report what is present and stop, unless the user asked for a
   specific missing file.
2. **Copy the templates** from `${CLAUDE_PLUGIN_ROOT}/skills/file-based-memory/templates/`
   to the repo root, dropping `.tmpl`:
   `AGENTS.md`, `CURRENT_STATUS.md` → `CURRENT_STATUS_AND_NEXT_STEPS.md`,
   `project-memory/{README,architecture,decisions,experiments}.md`.
   If the repo has (or the user names) more than one parallel line of work, also create
   `docs/<LINE>.md` per line from `WORKLINE.md.tmpl` and fill the dashboard's worklines
   table; otherwise delete that table.
3. **Fill from the repo, never invent.** README → overview and repo map; the build
   manifest → Commands; `docs/` → router rows (for the survey constraints see
   `references/agents-rebuild.md`). Where you don't know, leave the placeholder and a
   `TODO` — an honest empty section beats a confident wrong one. The dashboard's first next
   step must be a concrete command.
4. **Report** files created and skipped, sections left as TODO, and the cadence-hook
   settings in effect. `/file-based-memory:save-status` is the checkpoint from now on.
