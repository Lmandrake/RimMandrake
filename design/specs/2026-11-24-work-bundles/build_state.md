# Build state of the work-bundles build (the first bundle-shaped run)

Item: `RIMMANDRAKE_BATCH_ONE_MODS_OPEN_WORK_INTO_ONE_RUN_PIPELINE_SPLITS_PER_TICKET`. Design `design.md`, page
`boundary.md`, both beside this file. A fresh session that restarts this build reads this file first.

## Context per part (the first measurement for design section 5)

The window is 1,000,000 tokens (`contextWindow` in the run result files of `claude-opus-5-5`, measured 2026-11-24).
The figure is the context of the last main-thread turn (`detached_helper.context_tokens`).

| part | context after the part | note |
|---|---|---|
| read once (design, list_dispatch, list_home, list_effect, left_open_continue, detached_helper parts) | 176k | |
| 1. reality sort | 251k | includes 3 publish refusals repaired (could-not-look lint, page check, close form) |

## Done

- Part 1, the reality sort: `work_bundle.py sort`, at `f408c9e466` and `cf3fe8f324`.

## Learned

- `close --sha` refuses a ledger-only build: the sort closes with `--no-code` and names the build in the text.
- A ticket can name a passing selftest in `## verify` while it says `Acceptance test: none`
  (`RIMMANDRAKE_KILL_LIVE_HOLDER_RESUME_AFTER_FIRST_SESSION`); a named script counts only when added with its ticket.
- Most tickets have no runnable test: FlowWorks 66 of 67, Pyrelands 4 of 4, pipeline:maturation 13 of 15 (dry sorts,
  2026-11-24). The sort closes little; step 1 (the worker's class) does most of the reality work.
- The one green check found (`RIMMANDRAKE_SLIM_TICK_MEMORY_PAGE_BUILD_HITS_ONE_GIG_TICK_TOOK_FIVE_MIN`) is refused by
  its own guard gate (a fix that died once owes a class guard test). The sort reports that and keeps the ticket.
- `boundary_check.py` wants each promise's test named inside `main()`; promises of unbuilt parts sit under PLANNED.

## Next

- Part 2: the bundle record and the launcher (`list_dispatch` grouping, `work_bundle.py launch`, `./pipe bundle`).
