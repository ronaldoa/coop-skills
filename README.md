# Coop Skills

A local Claude Code **plugin marketplace** (`coop-skills`) holding three discipline
plugins distilled from the `equityResearchAgent` project into reusable, repo-agnostic
kits.

| Plugin | Skills | Commands | What it gives you |
|---|---|---|---|
| **file-based-memory** | `file-based-memory` | `/file-based-memory:bootstrap` · `/file-based-memory:save-status` | Persistent, resumable memory: routed `AGENTS.md` entrypoint, an operational dashboard, a four-layer durable `project-memory/`, size discipline, supersede-don't-delete history, and an auto-checkpoint cadence hook. Survives `/clear` and context resets. `bootstrap` installs the scaffold; `save-status` checkpoints each session. |
| **review-discipline** | `review-code` · `review-spec` · `review-fixtures` | — (invoke the skills) | Structured reviewer-passes: apply a fixed verification taxonomy as an *executable contract* (re-run the producer, don't trust the artifact) and emit findings keyed to named rows/checks with severity + a verdict. review-code = code-vs-architecture/contract; review-spec = prose-vs-code; review-fixtures = fixture-data-vs-declared-intent. |
| **eval-as-code-governance** | `eval-as-code-governance` | — (invoke the skill) | Govern a retrieval / ML eval suite as code: decouple gold from the corpus surface (predicate over stable semantic keys, not doc-ID + rank), the L1–L8 design checklist, the deterministic failure→action loop, four coverage detectors, the looseness-symmetry guardrails, and the two-lane rule. |

The three are layered: `review-fixtures` keeps one fixture file's intent matching its
data; `eval-as-code-governance` governs the whole suite above it; all three reviewer-
passes sit on top of the `file-based-memory` substrate.

---

## Use in another project

These are standard Claude Code plugins, so the cleanest route is to install them from
this directory as a local marketplace — that auto-wires the skills **plus**
file-based-memory's hooks and `/save-status` command.

### 1. Add the marketplace (once)

In Claude Code, type the slash command (any project):

```
/plugin marketplace add /home/ronaldo/Code/Coop/Skills
```

### 2. Install the plugins you want

Three independent plugins — install only what you need:

```
/plugin install review-discipline@coop-skills
/plugin install file-based-memory@coop-skills
/plugin install eval-as-code-governance@coop-skills
```

After install:

- **Skills are auto-discovered**, invoked namespaced: `/review-discipline:review-code`,
  `/review-discipline:review-spec`, `/review-discipline:review-fixtures`,
  `/eval-as-code-governance:eval-as-code-governance`. The model can also auto-trigger
  them from their `description`.
- **file-based-memory's hooks + `/save-status` command auto-register** (`hooks/hooks.json`
  + `commands/save-status.md` live at the plugin root — enabled = active, no
  settings.json wiring needed).
- **Scope**: `/plugin install` defaults to **user** scope (all projects). To scope a
  plugin to just one project, set it to project scope via the `/plugin` menu (writes to
  that project's `.claude/settings.json`).

### 3. Bootstrap the memory scaffold (file-based-memory only)

Installing the plugin doesn't populate anything — bootstrap writes the scaffold into the
target repo. In the new project, run `/file-based-memory:bootstrap` (or just ask the
agent to "bootstrap this project with file-based-memory"). It creates:

```
AGENTS.md
CURRENT_STATUS_AND_NEXT_STEPS.md
project-memory/{README,architecture,decisions,experiments}.md
```

Cadence hook env vars: `SAVE_STATUS_CADENCE` (default 5 commits between nudges; `0`
disables) · `CHECKPOINT_FILE` (dashboard filename).

---

## Alternative: copy a single skill (no plugin machinery)

If you only want one reviewer-pass and don't need hooks/commands, copy the skill
directory — Claude Code auto-discovers `.claude/skills/<name>/SKILL.md`:

```
cp -r /home/ronaldo/Code/Coop/Skills/review-discipline/skills/review-code  <project>/.claude/skills/
```

Then `/review-code` works; `references/` subdirs and relative links are supported. Put
it under `~/.claude/skills/` instead for global availability.

**Caveat:** hooks and `/save-status` do **not** come along with a copy (that's plugin-only),
so install **file-based-memory** via the marketplace route, not by copying.

### Which route

| | marketplace install (recommended) | copy single skill |
|---|---|---|
| review-discipline / eval-as-code | ✅ clean, namespaced | ✅ fine, lightweight |
| file-based-memory | ✅ **required** (needs hooks + `/save-status`) | ❌ loses hooks/command |
| updating | bump `version`, then `/plugin marketplace update coop-skills` | re-copy |
| multi-project reuse | ✅ add once, install anywhere | copy per project |

---

## Maintaining this marketplace

- The marketplace manifest is `.claude-plugin/marketplace.json`; each plugin's manifest
  is `<plugin>/.claude-plugin/plugin.json`.
- **Versioning matters for local paths.** Claude Code decides whether to pull an update
  by the `version` field. After editing any skill, **bump the `version` in both** that
  plugin's `plugin.json` **and** its entry in `marketplace.json`, or
  `/plugin marketplace update coop-skills` won't see the change.
- To distribute beyond this machine, turn `Skills/` into a git repo and `add` it by git
  URL instead of a local path; everything else is identical.

## Layout

```
Skills/
├─ .claude-plugin/marketplace.json          ← the coop-skills marketplace manifest
├─ file-based-memory/
│  ├─ .claude-plugin/plugin.json
│  ├─ commands/save-status.md
│  ├─ hooks/{hooks.json, *.sh, doc_budget_check.py}
│  └─ skills/file-based-memory/{SKILL.md, references/, templates/}
├─ review-discipline/
│  ├─ .claude-plugin/plugin.json
│  └─ skills/{review-code,review-spec,review-fixtures}/{SKILL.md, references/}
└─ eval-as-code-governance/
   ├─ .claude-plugin/plugin.json
   └─ skills/eval-as-code-governance/{SKILL.md, references/}
```
