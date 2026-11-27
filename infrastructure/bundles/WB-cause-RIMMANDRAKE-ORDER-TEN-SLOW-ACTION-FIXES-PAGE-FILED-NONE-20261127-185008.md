# WB-cause-RIMMANDRAKE-ORDER-TEN-SLOW-ACTION-FIXES-PAGE-FILED-NONE-20261127-185008: state

Members (7). Order: lane checks, tick and page, stream collect memo, deploy listing, scratch reap, run seconds, publish line.

## Done

- `RIMMANDRAKE_RUN_LANE_CHECKS_ONCE_193_OF_218_SECONDS`: REAL, fixed at 30f91fb7d9f3. `check_once.py` + `check_reads_hook/`
  (page `design/specs/2026-11-27-check-once/boundary.md`). Offline: real 81 checks, first beat 83 s, second 42 s (56 kept,
  16 unnamed: git children, shell loops), load 45. Live reading of both timers owed (the `checks` field of
  `<dispatcher state>/list_effect/reading.json` and the list_dispatch reading) and the slow-actions page line.
  Context after the group: 231 k of 1,000 k.

- `RIMMANDRAKE_CUT_TICK_PAGE_REPEAT_WORK_716_LAST_WORDS`: REAL, fixed at 3d37c19c24 (local; sha changes on publish).
  last_words index, run records and out-file facts kept by stat, mod_tokens memo, PNG digest skip and zlib default.
  Same window, load ~45: tick 62.5 -> 41.5 s wall (16.7 -> 12.5 s CPU); page 94 -> 31 s wall (35 -> 16.5 s CPU).
  Page `design/specs/2026-11-27-tick-repeat-work/boundary.md`. Not shared yet: the two ledger replays per process
  (trend 9 s, fleet_mods 2.5 to 4.7 s). Context after the group: about 420 k of 1,000 k.
- `RIMMANDRAKE_MEMO_SUBJECT_ALIASES_THREE_MILLION_CALLS_A_RUN`: REAL, fixed at 7948c8515a (local). artledger.aliases_held
  around streams.art_queue. Same load 26.6: collect 82 -> 54 s wall, 31 -> 15.3 s CPU.

## What the next context needs

- Publish waits 2 to 16 min (pipeline checks 991 s once). Put a polish commit with the next group's publish.
- Polish done: list-shape self-loop (92a4d15479); maturation-record token_unit line deleted. The list-dispatch line was
  deleted on origin by another run (db422438f6), so this run's commit for it was dropped before publish.
- Polish kept: `design/specs/2026-11-23-one-failure-classifier/polish.md` CYCLED count: changing it changes what
  selftest_maturation_now case 9 checks (cycled 4 with killed runs).

## Next

`RIMMANDRAKE_SPEED_DEPLOY_PLAN_RELATIVE_STAT_ENOMEM_SILENT`, then scratch reap, run seconds, publish line; then the live
readings of the three timers and the slow-actions page lines; then close each member.
