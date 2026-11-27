# WB-cause-RIMMANDRAKE-ORDER-TEN-SLOW-ACTION-FIXES-PAGE-FILED-NONE-20261127-185008: state

Members (7). Restart 1 is owed (context 559 k of 1,000 k at 3:05 PM PST, past the 500 k line). Every member's code and
test is written and committed; what is left is landing, live readings, the slow-actions page lines and the closes.

## Done (code, tests red-then-green, boundary page; commit shas change on publish: find them by subject)

- `RIMMANDRAKE_RUN_LANE_CHECKS_ONCE_193_OF_218_SECONDS` (first member, claimed): LANDED at 30f91fb7d9f3.
  `check_once.py` + `check_reads_hook/`; page `design/specs/2026-11-27-check-once/boundary.md`. Live since about
  12:30 PM on the dispatch clone: rm-list-effect 129 to 192 s before, 53 to 74 s after; rm-list-dispatch 370 to 480 s
  before, 86 to 203 s after (one 379 s). Offline, real 81 checks: first beat 83 s, second 42 s (56 kept, 16 unnamed run
  every time: git children, shell loops), load 45. Follow-up commit (not yet landed): list_dispatch's reading carries
  `checks`. Close it with the landed sha of that follow-up, `--evidence` the timings above.
- `RIMMANDRAKE_CUT_TICK_PAGE_REPEAT_WORK_716_LAST_WORDS`: commit "tick and page stop repeating work". Same window, load
  ~45: tick 62.5 -> 41.5 s wall (16.7 -> 12.5 s CPU); page 94 -> 31 s wall (35 -> 16.5 s CPU). Page
  `design/specs/2026-11-27-tick-repeat-work/boundary.md`. Not done: the two ledger replays per process (trend 9 s,
  fleet_mods 2.5 to 4.7 s) are not shared; say so at close or file it.
- `RIMMANDRAKE_MEMO_SUBJECT_ALIASES_THREE_MILLION_CALLS_A_RUN`: the Codex lane's build LANDED first (db371e01aa). This
  bundle's own build was dropped before publish. Measured with this bundle's build: collect 82 -> 54 s wall. Check the
  ticket's state; close it on db371e01aa if still open.
- `RIMMANDRAKE_SPEED_DEPLOY_PLAN_RELATIVE_STAT_ENOMEM_SILENT`: commit "deploy plan lists relative to each folder".
  `deploy_def_guard.listing` (scandir of a dir fd, ENOMEM waits, ListingFailed, plan exit 2). Interleaved at load ~30,
  Gimme Some Slack on ArchSmall: base 97.7 and 98.0 s, new 60.3 and 54.5 s, same plan text. Page
  `design/specs/2026-11-27-deploy-listing/boundary.md`.
- `RIMMANDRAKE_SPEED_SCRATCH_REAP_FOLDER_TIME_TWO_MILLION_LSTAT`: commits "find clones from each folder's listing" and
  "the borrower find is named". Cause measured: find_clones walked 870 k folders, 806 k in 100 publish_check_* folders
  left by killed publishes; now not entered and swept as day-old fixtures. candidates() 288 s (load 26) -> 127 s (load
  42). Dry run 723 s at load ~40: live 322 s (the borrower find 314 s), judge 254 s, fixtures 108 s; git children 32 s.
  A folder's own time is not a safe judge (a deep in-place write leaves it), so no folder-time shortcut. Page
  `design/specs/2026-11-27-scratch-reap-listing/boundary.md`.
- `RIMMANDRAKE_RECORD_MODEL_AND_TOOL_SECONDS_833_HOURS_UNSPLIT`: commit "each finished run's record carries its tool and
  model seconds". `run_seconds.py`, `detached_helper.seconds_of`, record field `seconds_split`. This run at 2:40 PM:
  span 13,335 s, tool 10,940 s, model 2,395 s. Page `design/specs/2026-11-27-run-seconds/boundary.md`. Owed for the
  spec: a split of the 7 days' runs (loop seconds_of over the records of the week) on the slow-actions page.
- `RIMMANDRAKE_MEASURE_PUBLISH_SLOT_DANGER_BEFORE_ANY_CHANGE`: `design/specs/2026-11-26-slow-actions/publish_line.md` and
  `publish_line_measure.py`. Recommends SLOTS stays 2; door-reads records per test and tree (46 % of selected runs are
  "another version", caused by unlanded trees overwriting the one per-machine record); name the 61 always-unknown
  tests' reads. File the door-reads change as its own item (with its acceptance test) when closing.

## Found on the way (no ticket before)

- The Codex lane sent four members of this live bundle to Codex (13:11 to 13:33 PM): fixed, commit
  "RIMMANDRAKE_KEEP_CODEX_LANE_OFF_LIVE_BUNDLE_MEMBERS" (codex_lane.plan skips a live bundle's member, a live run's item,
  and all while runs cannot be read; test t_a_member_of_a_live_bundle_or_run_is_never_sent red first). Codex builds of
  cut-tick, deploy, scratch and run-seconds are landing in their own clones (`/home/mandrake/rm/runs/clones/<ID>.det`).
  Whichever lands second must reconcile: keep one build per file. Read origin first.
- `selftest_stage6_checks.py` is red on origin (PRE-EXISTING at the door): not this bundle's.

## Polish

- Done: list-shape self-loop (`list_shape.own_check`); the maturation-record token_unit line deleted. The list-dispatch
  line was deleted on origin by another run.
- Kept: `design/specs/2026-11-23-one-failure-classifier/polish.md` CYCLED count (a change would change what
  selftest_maturation_now case 9 checks).

## Next, in order

1. Read `git log origin/main` for this bundle's subjects and for the Codex landers' subjects; land what is not landed
   (`./publish`; the line held 7 ahead at 3 PM). Reconcile with a Codex build that landed first on the same files.
2. Write each member's before/after line on `design/specs/2026-11-26-slow-actions/one_page.md` (rows 2 to 10; the
   numbers are above), and the 7-day split from `seconds_of`.
3. Close each member with its landed sha and its evidence; file the door-reads change; the bundle's end files the
   fresh reader (do not file it by hand).
