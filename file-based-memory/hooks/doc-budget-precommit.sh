#!/usr/bin/env bash
#
# PreToolUse(Bash) hook: when the agent is about to run `git commit` or `git push`,
# run the doc-budget gate and the doc gates first and block the command (exit 2)
# if either fails. The checks live in doc_budget_check.py and doc_gates.py.
#
# Honors DOC_BUDGET_BYPASS=1 / DOC_GATES_BYPASS=1 when set on the gated command
# itself, e.g.  DOC_BUDGET_BYPASS=1 git commit -m "deliberate oversize: <why>"

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

HOOKS="${CLAUDE_PLUGIN_ROOT:-$(dirname "$0")/..}/hooks"
status=0

# Each gate honours its own bypass, declared on the gated command itself.
case "$cmd" in
  *"DOC_BUDGET_BYPASS=1"*) ;;
  *) python3 "$HOOKS/doc_budget_check.py" || status=$? ;;
esac
case "$cmd" in
  *"DOC_GATES_BYPASS=1"*) ;;
  *) python3 "$HOOKS/doc_gates.py" || status=$? ;;
esac
exit "$status"
