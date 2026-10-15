#!/usr/bin/env bash
#
# PreToolUse(Bash) hook: before an agent-issued `git commit` / `git push`, run the ledger
# gate (ledger_check.py) and block the command (exit 2) if it fails.
# Honors LEDGER_BYPASS=1 when set on the gated command itself.

set -uo pipefail

input="$(cat)"
if command -v jq >/dev/null 2>&1; then
  cmd="$(printf '%s' "$input" | jq -r '.tool_input.command // empty' 2>/dev/null || true)"
else
  cmd=""
fi
[ -z "$cmd" ] && cmd="$input"

case "$cmd" in
  *"git commit"*|*"git push"*) ;;
  *) exit 0 ;;
esac
case "$cmd" in
  *"LEDGER_BYPASS=1"*) exit 0 ;;
esac

exec python3 "${CLAUDE_PLUGIN_ROOT:-$(dirname "$0")/..}/hooks/ledger_check.py"
