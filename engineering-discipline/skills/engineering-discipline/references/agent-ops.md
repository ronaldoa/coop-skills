# Agent operations: the field rules

Distilled from personal-memory entries of months of parallel Claude sessions on one
codebase (two machines, paid LLM calls, shared databases). Each rule keeps its incident in
one line so it can be judged at its edges; project names, ports and tables are stripped.

## A. Parallel sessions on one worktree

1. **A snapshot is never a premise.** `git status` clean and `ps` showing nobody describe
   one second. Every rule below guards the window *after* you looked. *(Relaxing them on a
   clean snapshot was corrected by the user the same day.)*
2. **Commit with an explicit path list** (`git commit -F - -- <files…>`), never `git add` +
   `git commit`, never `git add -A`. Edges: a new file still needs its own `git add`; a path
   commit takes the **worktree** version, not what you staged; it does **not** protect a file
   two sessions both edited — `git diff -- <each path>` before committing, every path, not
   just the ones you expect to collide. *(One commit of 31 paths carried another session's
   production change because 3 were checked.)*
3. **Mid-slice, re-check that your edits are still there.** Another session can restore a
   file under you; the compiler found it, not you.
4. **Don't `git rm`** (stages the deletion immediately — another session's commit swallowed
   84 deleted lines) and **don't `git stash`** in a shared tree (stashes everyone's edits);
   build the "before" arm in a `git worktree`.
5. **Never chain a destructive sync after a failable git command.** Derive sync path lists
   only from two commits (`git diff --name-only <old> <new>`) after proving `<new>` exists;
   stop at the first "foreign edit" warning. *(An empty `<new>` turned the diff into "all
   worktree changes" and erased five of another session's uncommitted docs.)*
6. **Edit code that writes shared state in a private worktree**, not the shared tree — the
   shared working copy *is* the code other sessions are running. Put worktrees **outside**
   the repo directory (tools that scan the repo otherwise count files twice). A new
   worktree has no env file or dependencies, so probes read "cold" and look like bugs —
   link them temporarily and never commit the links.
7. **Don't copy a whole shared-tree file into a private worktree to commit it** — it carries
   other sessions' uncommitted edits. Apply your own diff.
8. **Someone else's commit took your change?** Don't rewrite history; say so in your own
   commit message.

## B. Processes and configuration

9. **Never kill by pattern** (`pkill -f <generic name>`, or `ps | grep | kill` — the same
   thing). Stop what you started, by its PID / process group / task id. *(Killed another
   session's server twice; a pattern that structurally could not match left an 83-minute
   stale process that silently took the port.)*
10. **Read the port from the process's own log.** An explicit `PORT=` is a starting point —
    the server may move up if it is taken. No file watcher ⇒ a running process has old code;
    start a second process for the changed arm. Shared log files get rotated by others —
    give your run a private log sink.
11. **Print the effective value before measuring anything behind a flag.** An env file may
    override the command line (the app's own loader), and an env file value beats a changed
    code default. In scripts, load env **before** importing modules that read it (ESM
    imports are hoisted).

## C. Test and measurement instruments

12. **"Green" includes "skipped" and "0 tests ran".** Read the count that ran. A missing
    env var turns a gated suite into "N skipped"; in zsh an unquoted multi-file variable is
    **one** argument, so a mutation loop runs zero tests and reports all green (`${=VAR}`).
13. **Uniform fallback output = suspect the environment first.** Missing credentials made a
    suite pass while every answer was the same "Unable to generate…" template. The opposite
    also happens: loading the full env into the whole suite produced ~80 fake reds (fake
    timers froze the DB driver). Keep the baseline in the project's canonical mode.
14. **Hand mutations: back up → mutate → run → restore from the backup → `cmp`.** Never undo
    with `git checkout` (it erases your uncommitted work in that file). Parallel agents must
    not mutate the same file in one worktree — whole-file backups write each other's
    mutations back.
15. **Capture tools can overwrite committed fixtures** with degraded local data — check
    `git status` after every capture run.
16. **Tests sharing one database assert only their own rows**; run a changed one three times
    before trusting it.
17. **Full temp dir looks like flaky tests** (ENOENT, missing output). `df` first; clean only
    your own, older entries — recent ones may belong to a running session.
18. **Probe ports with a real socket**, not a shell builtin (`/dev/tcp` is bash-only and
    reports every port closed under zsh).

## D. External services and cost

19. **Quota or balance exhaustion can fall back silently** to a keyword path whose readings
    look plausible. Before reading any LLM measurement, grep the run for 402 / 429 /
    fallback. *(A polluted axis baseline was one step from being committed.)*
20. **Report the call count before spending, and scope the run** to the turns the change can
    actually reach; arms with identical bytes share one call. State in the record which
    cases were skipped "by construction, not measured". *(User: "花钱太多了".)*
21. **Rate limits are often your own amplification** — count requests before blaming quota
    (three questions once produced 120k requests).
22. **External state used to drive a rare branch rots** (a ticker with no calendar, a flaky
    endpoint). Re-probe with production functions **plus a positive control** each time;
    the reusable thing is the probe, not the value written down.
23. **Before DDL on a shared table, check locks and set a lock timeout** — an `ALTER` queued
    behind a long writer blocked every later session for ten minutes.

## E. Claims and reports

24. **Verify every claim against its source** — definitions, "industry practice", a
    subagent's candidates — and record how (verbatim / summary / unverified). *(A spot check
    found 9 of 35 wrong.)*
25. **Conditions belong in data fields, not prose caveats**: the environment snapshot, the
    timestamp, which dependencies were live — stored with the reading, so they travel with
    it. Before reporting: am I counting requests or log lines? Is this measured or inferred?
    (Asking before a flag flip: decision-ledger, `open-questions.md`.)
26. **When the user asks "didn't you record that?", check your own records first** — they are
    often right.

## F. Two machines, one developer

27. **Commit before switching machines** (pushing stays a human action); observations are
    committed the moment they are captured; each machine rebuilds its own caches; data
    parity is checked by committed fingerprints, not by trust.

## G. LLM-application design rulings (from the origin project's user)

These were corrections of the agent's designs; they generalize to any LLM-backed product.

28. **Semantic recognition belongs to the model; code does only conversions with a unique
    answer.** Don't build a word list to decide what "recently" means — the model emits a
    symbol, code converts symbol → length → date in one place.
29. **Layer prompts: generic / task / data**, never one long string; pin the split with a
    structural test (generic layer has no task words, task layer restates no generic rule).
30. **One flow per class of question.** Don't exclude a question class from the flow because
    its data source differs; put the difference inside the fetch node.
31. **The planner compiles the request; the provider says whether it can answer**, by its own
    declaration. Don't judge a provider's capability in the planning layer.
