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
| 2. record and launcher, 3. role and context guard | 300k | read at the guard's first real run (292k) |
| 4. restart and keep going | 342k | |
| 5. live pass | ~370k | |
| 7. the page | 384k | built before part 6, the smaller part first |

## Done

- Part 1, the reality sort: `work_bundle.py sort`, at `f408c9e466` and `cf3fe8f324`.
- Parts 2 and 3: the record, the lane's grouping, `./pipe bundle`, the role's commands and `work_bundle.py context`, at
  `4909b0eff4`. The role text is the Conductor's (`60ed8da703`); this build added only its commands section.
- Part 4: the restart branch in `left_open_continue.py`, at `aafc60da65` and `ae0656172f` (end line, gated replaced).
- Part 5: `work_bundle.py live`, at `40e3d9db51`. Real run: UNRUN, both games held by BENCH runs (2026-11-25 00:25 PST).
- Part 7: the page block on MATURATION_NOW and MATURATION_DETAIL, at `8c0c85ad9f`.
- Proof by use: `WB-pipeline-judges-20261125-082122` launched by `./pipe bundle pipeline:judges` (3 members, 1 left out
  with its wait). The lane itself launched three bundles of one from 00:02 PST on.

## Learned

- `close --sha` refuses a ledger-only build: the sort closes with `--no-code` and names the build in the text.
- A ticket can name a passing selftest in `## verify` while it says `Acceptance test: none`
  (`RIMMANDRAKE_KILL_LIVE_HOLDER_RESUME_AFTER_FIRST_SESSION`); a named script counts only when added with its ticket.
- Most tickets have no runnable test: FlowWorks 66 of 67, Pyrelands 4 of 4, pipeline:maturation 13 of 15 (dry sorts,
  2026-11-24). The sort closes little; step 1 (the worker's class) does most of the reality work.
- The one green check found (`RIMMANDRAKE_SLIM_TICK_MEMORY_PAGE_BUILD_HITS_ONE_GIG_TICK_TOOK_FIVE_MIN`) is refused by
  its own guard gate (a fix that died once owes a class guard test). The sort reports that and keeps the ticket.
- `boundary_check.py` wants each promise's test named inside `main()`; promises of unbuilt parts sit under PLANNED.

- A `killed:` result is both a hand stop (`pipe stop --kill` writes its reason) and a death (`killed: signal`); a bare
  `systemctl stop` reads as a death, so the bundle restarts it.
- `argparse.REMAINDER` after a positional swallows later options: `live` splits at `--` first (seen on real use).
- The Conductor wrote `roles/bundle_worker.md` mid-build; refusals there start `REFUSED BY BUNDLE:`, which the code reads.

## Next

- Part 6: the steward routes a mod's road-back failures as ONE bundle (maturation_autonomy / maturation_dispatch).
- Watch `WB-pipeline-judges-20261125-082122` end: its line in `D:\ClaudeWork\rimmandrake\conductor\log.md`.
