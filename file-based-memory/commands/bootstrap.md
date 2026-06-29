---
description: Install the file-based-memory scaffold into this repo — router, dashboard, and four-layer durable memory — filling what's known from the repo and leaving honest TODOs for the rest
argument-hint: [optional path to repo root; defaults to the current working directory]
---

Bootstrap a repo so a future agent can cold-start with zero conversational context.
Follow the **"Bootstrap a repo"** section of the `file-based-memory` skill
(`SKILL.md` + `references/bootstrap.md`); this command runs that protocol on demand.

Target repo root = `$ARGUMENTS` if given, else the current working directory.

## Step 1 — check before you write

- If `AGENTS.md` / `CURRENT_STATUS_AND_NEXT_STEPS.md` / `project-memory/` already
  exist, **do not clobber them**. Report what's present and stop, unless the user
  asked to re-scaffold a specific missing file. Bootstrap is a one-time install.
- Confirm you're at the intended repo root (look for `.git`, a manifest, source dirs).

## Step 2 — survey the repo (so placeholders get filled, not invented)

Gather just enough to fill the templates truthfully:

1. `README.md` + top-level layout → Project Overview + repo map.
2. The build/test/run/lint manifest (`package.json` scripts, `Makefile`, `justfile`,
   `pyproject.toml`, …) → Commands.
3. `ls docs/` (or equivalent) → seed the doc router (one route per active doc; mark
   archived/superseded). If there are no docs yet, leave the router empty with a TODO.

For the full per-section sourcing recipe and the doc-router Explore-agent survey, see
the skill's `references/agents-rebuild.md`.

## Step 3 — copy the templates, then fill what you know

Copy the `file-based-memory` skill's templates into the repo root, dropping the
`.tmpl` suffix:

```
templates/AGENTS.md.tmpl                      -> AGENTS.md
templates/CURRENT_STATUS.md.tmpl              -> CURRENT_STATUS_AND_NEXT_STEPS.md
templates/project-memory/README.md.tmpl       -> project-memory/README.md
templates/project-memory/architecture.md.tmpl -> project-memory/architecture.md
templates/project-memory/decisions.md.tmpl    -> project-memory/decisions.md
templates/project-memory/experiments.md.tmpl  -> project-memory/experiments.md
```

(The templates live in the installed plugin at
`${CLAUDE_PLUGIN_ROOT}/skills/file-based-memory/templates/` — read them from there, or
locate them via the `file-based-memory` skill.)

Then fill the placeholders from Step 2. **Do not invent content** — leave the template
placeholder and a `TODO` wherever you don't yet know the answer. An honest empty
section beats a confident wrong one. Keep the dashboard's first "next step" concrete
(an actual command), even if it's just "read X and decide Y".

## Step 4 — report

List the files created (and any skipped because they already existed), name the
sections left as TODO, and state the cadence-hook env vars in effect
(`SAVE_STATUS_CADENCE`, default 5; `CHECKPOINT_FILE`). Remind the user that
`/file-based-memory:save-status` is the checkpoint command for every session after this.
