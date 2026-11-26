# BOUNDARY: every fresh helper's start is the same bytes as the last one's, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/detached_helper.py` (`SHARED_PROMPT`, `shared_start_plan`, the shared-start lines of
`launch_argv`, `session_of`), `src/RimMandrake/rimflow/stop_resume.py` (`session_of`), and the outcome check
`src/RimMandrake/Utils/helper_start_share.py`. Item: `RIMMANDRAKE_SHARE_HELPER_START_ONE_STATUS_LINE_REWRITES_IT`, from
the experiment `design/experiments/2026-11-19-night-hypotheses/04-shared-start.md`. Each promise has a test of its name
in `src/RimMandrake/rimflow/selftest_shared_start.py`.

Why: Claude Code writes into a run's first request, in this order: the auto-memory folder path (the cwd's), `Contents
of <cwd>/CLAUDE.md`, the git status block, then the prompt. Each one made every helper's ~60,000-token start a new
cache write (an Opus pair at 01:10 PST, 2026-11-26: read 11,343, wrote 115,717). With auto-memory off, the project
CLAUDE.md in the system prompt (same text, no path), no git block, the project's MCP set and one fixed prompt, the
first path-bearing text is message 1's environment block. Two starts from two clones then share all before it
(measured 2026-11-26: read 52,401, wrote 12,849, share 0.803).

The item's title asked for one fixed path (each clone bind-mounted there in its own user and mount namespace). That
was built and measured first (share 1.000) and then dropped: inside a user namespace a helper cannot read the
`environ` or `cwd` of any process outside it (139 of 140 of this uid's processes refused, against 5 outside: the
kernel's ptrace check across user namespaces), which blinds every `/proc` scan a helper runs (`clone_in_use` before a
clone is reused, `scan_marked_live`, the reap selftest at `./publish`). The 0.2 of a start that a fixed path would add
is not worth a helper that cannot see the processes beside it.

## ACCEPTS (the only inputs this is built for)

- **a-fresh-detached-run.** A `detached_helper.py launch` that does not `--resume` a session, on any host.
- **a-clone-with-its-claude-md.** The run's clone holds the project `CLAUDE.md` and `.mcp.json` (a clone without one
  launches without that flag).

## DOES NOT SURVIVE (not promised)

- **a-resume.** A `--resume` run keeps its own start; its transcript already holds one.
- **sharing-across-models-or-accounts.** A cache entry serves one model on one account.
- **two-starts-far-apart-or-at-different-claude-md.** Starts more than an hour apart (the cache life), or from clones
  whose CLAUDE.md text differs, write the start new.
- **the-message-1-tail.** Message 1 (the environment block with the cwd, the hook text, the tool and skill lists) is
  written new by each run; that is the ~13,000 tokens a start still writes.

## PROMISES (each one is owed a test of the same name)

- **a-fresh-run-gets-a-shared-start.** `shared_start_plan` names the session and writes the prompt file, and
  `launch_argv` gives claude `--session-id`, stdin from the fixed prompt (the brief is in no argument), `RM_BRIEF` naming
  the brief, `CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS=1`, `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`, the project CLAUDE.md by
  `--append-system-prompt-file` with that file in `claudeMdExcludes` (the stop channel's PostToolUse hook kept in the
  same settings), and the project's MCP set alone.
- **a-resume-keeps-its-own-start.** A resume leaves the record with `shared_start_off` and its why, and `launch_argv`
  is the old argv: the brief on stdin, none of the flags above.
- **the-first-prompt-is-the-same-bytes.** The prompt files of two runs of two items hold the same bytes, and they
  name no item, unit, clone or brief path.
- **a-shared-start-transcript-is-found-by-its-session.** `detached_helper.session_of` and `stop_resume.session_of`
  find a shared start's transcript by the session named at launch, though its first prompt names no item.
- **the-outcome-check-reads-the-newest-pair.** `helper_start_share.py` takes the newest fresh start on the model
  (default opus) and the earlier one on that model inside the window, passes on a share at or over the bar, fails
  under it, reads EMPTY (4) when there is no such pair, and COULD NOT LOOK (3) on empty records or a missing
  transcript.

Later lists beside this page: `polish.md` (none yet).
