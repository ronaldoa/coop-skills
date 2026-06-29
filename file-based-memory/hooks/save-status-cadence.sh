#!/usr/bin/env bash
#
# Stop hook: auto-checkpoint cadence nudge (file-based-memory plugin).
#
# Analogue of the "2-action rule" from file-based planning skills: rather than
# relying on the agent remembering to checkpoint, this measures how stale the
# operational checkpoint is and nudges when work has accumulated past it.
#
# Signal: number of commits that have landed since the last commit that touched
# the checkpoint/dashboard file. Many new commits with an untouched dashboard ==
# the resume state is lagging reality, which is exactly the cold-start hazard the
# checkpoint exists to prevent.
#
# Mechanism: NON-BLOCKING. Always exit 0 (the turn ends normally). When the
# threshold is crossed it emits JSON on stdout with:
#   - hookSpecificOutput.additionalContext -> injected for the agent (system reminder)
#   - systemMessage                        -> surfaced to the user in transcript
# It never sets `decision`, so the stop is always allowed (no stop-loop risk).
#
# Config (env):
#   SAVE_STATUS_CADENCE  commit threshold (default 5; 0 disables)
#   CHECKPOINT_FILE      dashboard filename (default CURRENT_STATUS_AND_NEXT_STEPS.md)

set -uo pipefail

ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
cd "$ROOT" || exit 0

# Drain stdin (the Stop hook JSON input) so the hook never blocks on a pipe.
cat >/dev/null 2>&1 || true

THRESHOLD="${SAVE_STATUS_CADENCE:-5}"
[[ "$THRESHOLD" =~ ^[0-9]+$ ]] || exit 0      # non-numeric -> disabled
[[ "$THRESHOLD" -eq 0 ]] && exit 0            # 0 -> disabled

git rev-parse --git-dir >/dev/null 2>&1 || exit 0   # must be a git repo

CHECKPOINT_FILE="${CHECKPOINT_FILE:-CURRENT_STATUS_AND_NEXT_STEPS.md}"

# Last commit that touched the checkpoint file. No history -> no baseline -> bail.
last="$(git log -1 --format='%H' -- "$CHECKPOINT_FILE" 2>/dev/null)"
[[ -n "$last" ]] || exit 0

count="$(git rev-list --count "${last}..HEAD" 2>/dev/null)"
[[ "$count" =~ ^[0-9]+$ ]] || exit 0

[[ "$count" -lt "$THRESHOLD" ]] && exit 0

# Stale: nudge. Non-blocking advisory (no `decision`); exit 0.
msg="${count} commit(s) have landed since ${CHECKPOINT_FILE} was last checkpointed (threshold ${THRESHOLD}). Consider running /file-based-memory:save-status to refresh the resume dashboard before the operational state drifts further from a cold-start reader."

printf '{"systemMessage":"save-status cadence: %s","hookSpecificOutput":{"hookEventName":"Stop","additionalContext":"%s"}}\n' \
  "$msg" "$msg"

exit 0
