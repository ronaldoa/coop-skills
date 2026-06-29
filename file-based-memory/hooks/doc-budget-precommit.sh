#!/usr/bin/env bash
#
# PreToolUse(Bash) hook: when the agent is about to run `git commit` or `git push`,
# run the doc-budget gate first and block the command (exit 2) if it fails, so
# oversized doc/memory entries never reach a commit. The checks live in
# doc_budget_check.py.
#
# Honors DOC_BUDGET_BYPASS=1 when set on the gated command itself, e.g.
#   DOC_BUDGET_BYPASS=1 git commit -m "deliberate oversize: <why>"

set -uo pipefail

input="$(cat)"

# Extract the command from the PreToolUse JSON (.tool_input.command); fall back to
# the raw stdin if jq isn't available or parsing fails.
if command -v jq >/dev/null 2>&1; then
  cmd="$(printf '%s' "$input" | jq -r '.tool_input.command // empty' 2>/dev/null || true)"
else
  cmd=""
fi
[ -z "$cmd" ] && cmd="$input"

case "$cmd" in
  *"git commit"*|*"git push"*) ;;   # gate these
  *) exit 0 ;;                        # everything else: allow immediately
esac

# Respect an explicit bypass declared on the gated command itself.
case "$cmd" in
  *"DOC_BUDGET_BYPASS=1"*) exit 0 ;;
esac

ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
exec python3 "${CLAUDE_PLUGIN_ROOT:-$(dirname "$0")/..}/hooks/doc_budget_check.py"
