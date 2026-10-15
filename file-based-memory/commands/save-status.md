---
description: Checkpoint engineering state (dashboard or one line's §0.0 handoff block, plus project-memory/) for a resumable, cold-start handoff
argument-hint: [optional line name (multi-workline mode) or one-line focus hint]
---

Read the `file-based-memory` skill's `references/checkpoint-protocol.md` and execute it
in full, including the confirm-before-writing step, the six-question cold-resume check and
the re-verification of every number left behind.

`$ARGUMENTS`, if present, is the focus hint. In multi-workline mode the target is that
line's `§0.0` block and dashboard row; if `$ARGUMENTS` names no line and the session
touched more than one, ask which.
