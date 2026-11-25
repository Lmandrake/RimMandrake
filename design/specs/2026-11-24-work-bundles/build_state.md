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
| 6. the Maturation Pipeline (holder = the mod's bundle) | 437k | |
| two fresh readers, their fixes, the item's acceptance test | 470k | the readers' own contexts are not in this figure |

## Done

- Part 1, the reality sort: `work_bundle.py sort`, at `f408c9e466` and `cf3fe8f324`.
- Parts 2 and 3: the record, the lane's grouping, `./pipe bundle`, the role's commands and `work_bundle.py context`, at
  `4909b0eff4`. The role text is the Conductor's (`60ed8da703`); this build added only its commands section.
- Part 4: the restart branch in `left_open_continue.py`, at `aafc60da65` and `ae0656172f` (end line, gated replaced).
- Part 5: `work_bundle.py live`, at `40e3d9db51`. Real run: UNRUN, both games held by BENCH runs (2026-11-25 00:25 PST).
- Part 7: the page block on MATURATION_NOW and MATURATION_DETAIL, at `8c0c85ad9f`.
- Part 6: a pilot mod's road-back holder is the mod's one bundle, at `9b2aabb5ed`.
- Proof by use: `WB-pipeline-judges-20261125-082122` (`./pipe bundle pipeline:judges`, 3 members, 1 left out with its
  dated wait). ENDED 2026-11-25 1:25 AM PST: 3 of 3 closed done, 0 restarts, one run of 3840 s, 1,012,508 weighted
  tokens (Opus), its own fresh reader, its state file `infrastructure/bundles/WB-pipeline-judges-20261125-082122.md`,
  context 161,502 after its one group [measured]. About 337k weighted tokens per member closed, against 2.27M per ticket
  fixed in the 8 one-ticket runs of the week (design section 8) [measured, one bundle: not yet a rate].
- The lane launched bundles of one on its own from 00:02 PST on (part 2 live).
- Fresh reader 1 found 2 significant faults, both fixed test first at `a16f94dce5`: the progress guard read 0 on every
  real restart (a restart that ended none would restart for good), and a restart that never started left the bundle
  `restarting` (live) for good. Its polish line 5 was significant too (a raised launch left a live `launching`
  record), fixed in the same commit. Fresh reader 2 on the fixes: nothing significant.
- The item's acceptance (five tickets, two fixed, one run) is `t_five_tickets_two_fixed_one_run`, at `01630f9219`.
- Deviation: non-pilot mods keep one fixer per road-back item. Every advancing mod is a pilot (ExplosiveKnockback,
  GimmeSomeSlack, FlowWorks), so ordinary operation does not reach it now (test 1).

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
- A new store read inside an old pipeline function is reached by that function's old selftests: the store refuses a
  test process with no store of its own (a fake `WB-mod-WreckedMachines` record leaked once, deleted).
- `argparse.REMAINDER` after a positional swallows later options: `live` splits at `--` first (seen on real use).
- The Conductor wrote `roles/bundle_worker.md` mid-build; refusals there start `REFUSED BY BUNDLE:`, which the code reads.

## Next

- Nothing in this build. Owed by use: the first restart of a real bundle (none restarted yet), the first mod bundle
  (the next pilot road back), and a live pass that finds a free game.
