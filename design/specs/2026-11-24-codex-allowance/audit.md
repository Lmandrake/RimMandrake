# Audit of the Codex night: every commit, ticket and patch, 2026-11-24 9:05 AM PST

Item: `RIMMANDRAKE_AUDIT_CODEX_NIGHT_FIXES_INTEGRATED_AND_TICKETS_CLOSED`. Scope: the two runs of
`RIMMANDRAKE_SPEND_CODEX_ALLOWANCE_BEFORE_TUESDAY_RESET_48_LEFT`. Readings are measured unless a line says otherwise.

- All 40 commits that the two runs named are on origin/main.
- 52 selftests that the fixes touch ran on main: 51 PASS. The red one, `selftest_order_wait.py`, could not run on
  Archmagi; its repair is `a5dcd5bfd0` (PASS; red with a planted fault). `selftest_testq_gaps.py` was red once under
  load and PASS alone. The three SteveDesktop acceptance scripts read 11/11, 6/6 and 8/8.
- The bundle of the second run's clone holds no tracked work, only git-ignored views.

## Integrated and closed

| ticket | commit |
|---|---|
| `RIMMANDRAKE_NAME_GAME_ON_WRAPUP_DEBTS_ARCHBIG_VOIDS_ALL` | `d9e88fc8f9`, `1d03212cce` |
| `RIMMANDRAKE_TRACE_FLOWWORKS_HELD_RAIDER_LEFT_DRAINED_MOAT` | `3944c20b4c` (fresh reader recorded) |
| `ART_XDELETE_FIX_UNLINK_BEFORE_RECEIPT_TOO` | `d3df46dd64` |
| `RIMMANDRAKE_FIX_PIPE_UNDO_LEAVES_KILL_TIMER_ARMED`, `RIMMANDRAKE_UNHANG_ARTPIPE_STATE_FIND` | `caf6eb8af5` |
| `FLYERMASTER_VET_OWNER_SHEETS_UNREAD`, `RIMMANDRAKE_FIX_SLOT_SCAN_BLIND_TO_TEXPATH_PATCHES`, `RIMMANDRAKE_WIDEN_RESTORE_CHECK_VARIABLE_SETTINGS_ARGS_SLIP_PAST`, `CANON_GAPFILL_FIX_SLOT_TRUSTS_THE_TITLE` | `49a3139e96` |
| `RIMMANDRAKE_LET_LOCK_CLAIM_PASS_HIS_HOLD_STAGING_RAN_UNLOCKED` | `2e9cff556b` |
| `RIMMANDRAKE_WAIT_AND_WAKE_ON_ONE_LANE_JOB` | `8307b126c8` |
| `RIMMANDRAKE_READ_OPS_LEDGER_AT_ORIGIN_NOT_BENCH_LAG`, `RIMMANDRAKE_KEEP_ALARM_ITEMS_OPEN_FOUR_OF_SIX_POINT_AT_CLOSED` | `5083b5e6b4`, `852e0cd378` |
| `RIMMANDRAKE_WARN_STEVEDESKTOP_LOGIN_DEADLINE_ARCHMAGI_ONLY_WATCHED` | `c96efbd3bc` |
| `RIMMANDRAKE_RESTORE_ART_EVAL_REGRESSION_PICTURES_FIVE_ROWS_POINT_AT_NOTHING` | `80c8910b85`, finished by `cf1138197c` |
| `TAILSTATE_SHRINK_WHEN_SPOOL_FULL_BLOATS` | `a60c81fcb1` |
| `RIMMANDRAKE_APPLY_FACING_RESCALE_NOT_REGEN_FOUR_ALL_TALL` | `26cdbc68a9` |
| `RIMMANDRAKE_BUILD_SCENE_JUDGE_OUTSIDE_GAME_FROM_KEPT_TRACE` | `03a158941e` |
| `RIMMANDRAKE_WATCH_INGAME_VISIT_OWED_NO_DRIVER_UNSEEN` | `c3a60f061a` |
| `RIMMANDRAKE_FIX_STEVE_WORKER_VALIDATES_JOB_BEFORE_PULL` | `80268a7572` |
| `RIMMANDRAKE_CLEAR_HELD_NIGHTLY_RED_AFTER_FIX_PROVES_GREEN_WAITS_A_DAY` | `de28709aab` |
| `RIMMANDRAKE_RETIRE_FOUNDRY_SLOT_KEY_INDEX_NAMED_A_GHOST` | `f090327ad2` |
| `RIMMANDRAKE_TICKET_LANE_CAUSE_ONCE_THIRTEEN_FOR_ONE`, `RIMMANDRAKE_FINISH_TICKET_LANE_CAUSE_ONCE_THREE_SPEC_PARTS_UNBUILT` | `f86902c8e7`, `f97db855eb`, `ba7109b975` |
| closed by this audit: `RIMMANDRAKE_FENCE_ARTPIPE_SELFTEST_OUT_OF_PROFILE_169_LEAKS`, `WAKE_LIST_FIX_OLD_MAIL_MARKED_LATE`, `RIMMANDRAKE_FIX_BRIDGE_RELEASE_WRAPUP_RESTORE_TRACEBACK_EXIT_ONE` | `200755349a`, `e9efb41a65`, `61e38119d3` (each test run today) |
| eight stale tickets and the Friday judge | six re-run today, PASS; `enact_*` folders 0; `oldest_h` reads 488.5 |

Review fixes with no ticket, on main: `bde6d4ae9d`, `9f5835b8ef`, `7aa1752ee4`, `e0cba017d6`, `fe2fcefa3a`, `f792bd7b76`,
`61f1aabc81`, `bd87258ddd`.

## Mod fixes: their readers and touched checks

| mod | commits | reader | touched checks (`build_match.py check`) |
|---|---|---|---|
| GimmeSomeSlack | `f6be36c45e`, `66f251bb97`, `f4d5517ca1` | Codex reread; its two faults became `f4d5517ca1` | 207 of 207 count |
| FlowWorks | `49224d51e7`, `78f51ace1d`, `3944c20b4c` | Codex reread; its three faults became `78f51ace1d`; the moat fix by its own reader | 29 of 30 count; `sc_walk` waits for ArchBig |
| ExplosiveKnockback | `1acc05e0ed`, `e089dc2573` | `visit_6/fix_reviews.jsonl`, sound | 56 of 56 count; the deployed folder on ArchBig is not the source, a deploy is owed |
| Pyrelands | `a6f05380df` | OWED: the program asks it at the exit of visit 9 (17e206ef79) | ten UNRUN rows; visit 9 runs them now |

## Open, with the next act and who does it

- `STATIC_CALL_THINGID_FIX_DIGIT_EATS_ITSELF` and `RIMMANDRAKE_REPAIR_FRAME_HIST_READS_THREE_WAYS_WRONG`: on main and in
  both deployed Archmagi companions. One live reading each, at the next free game.
- `TILE_TEMP_CACHE_RESET_TOOL_1`: built; its criterion A1 needs a live reading.
- `RIMMANDRAKE_BUILD_GAME_WATCHER_NAMES_THE_BROKEN_STATE`: on main, not in either deployed companion. The Conductor deploys
  after the two visits, reads three states, wires the stop timer.
- `RIMMANDRAKE_BUILD_DEVIATION_RECORD_SETTINGS_FIELD_JOINS_FIRST`: patch NOT landed, for a fault: its guard stops a mod's
  own `WriteSettings` for the life of the process, and three live tests of ours need that call. A builder fixes the
  guard; it lands after both visits. The patch that applies on main is named on the ticket.
- `RIMMANDRAKE_WIRE_ASK_LANE_HOST_FACTS_CLOSED_WITH_FIVE_PARTS_UNWIRED`: most parts landed at `14d6f09491`. The SteveDesktop
  run takes the kept companion for each source hash from the `askgate2` patch, or builds its own.
- `RIMMANDRAKE_CUT_TICK_DRVFS_WALK_OF_DEPLOYED_BIOMES_STATS_TEN_THOUSAND`: the Conductor decides. The three lines are on the
  ticket.
- `LEFTOVERS_CHECK_FIX_SAFE_ON_UNSAFE_FOLDER`, `TELEMETRY_HARDEN_FIX_FOUR_EDGE_CASES`, `TRACE_MKDIR_HARDEN_STAT_OUTLIVES_IT`: nothing
  landed; back in the ready pool for the List Pipeline.
- `JUNK_RESKIN_REDO_REDRAW_NINE_LIVES`: four pictures judged KEEP; the art ledger installs them next.

## Patches not landed on purpose

- `gss4`: landed whole as `f4d5517ca1`; not a remainder.
- `fw_pit_hold`: the moat run landed a wider fix. `fw_rivers` weir part and `pyr` automatic foam: dropped by the helper
  (rare; a vanilla patch). Their polish lines were missing; this audit wrote them.
- `launch_perm` publish selector (a launch line in a non-pipeline file is not checked at `./publish`): put on the polish
  list by the first run. The nightly look still sees it.
- `leftovers`, `telem4`, `mkdirtrace`: test lines only.

## Fresh read of the lane's pipeline fixes (owed by the second run)

This audit's run made none of them. It read the production lines of `2e9cff556b`, `8307b126c8`, `5083b5e6b4`,
`c96efbd3bc`, `de28709aab`, `80268a7572`, `a60c81fcb1`, `26cdbc68a9`, `c3a60f061a`, `d28602ad11`, `03a158941e` (last 5 % not),
`f090327ad2` (hook lines in part), `d3df46dd64`, `01bc9212f2`, `caf6eb8af5`, `49a3139e96`. Nothing significant.
`f97db855eb` was read by the SteveDesktop run. Not read: the test files, `80c8910b85`.

## The 8:07 AM PST stop: what it cut

Item: `RIMMANDRAKE_VERIFY_CODEX_STOP_HE_SAID_DO_NOT_INTERRUPT`. Read 2026-11-25 9:10 AM PST from the ledger and
`infrastructure/state/control/acts.jsonl`.

- His words at 8:07 AM PST 2026-11-24: "Please release the requirement to use up CODEX. I will be spending it
  elsewhere, so our usage of it can resume the normal rate. Thanks." These words do not say "do not interrupt work in
  progress". His only words of that day about interrupting came at 8:27 AM PST and are about walks: "Don't interrupt
  mod work for a walk."
- The act was `ct_000169`, a stop of the builder-lane unit in mode `at_easy_spot`.
- Work was cut: the run ended its four newest Codex jobs; three were killed about two minutes into their tickets, one
  had finished. The three partial diffs held selftest lines only.
- Nothing is lost:
  - `LEFTOVERS_CHECK_FIX_SAFE_ON_UNSAFE_FOLDER` and `TRACE_MKDIR_HARDEN_STAT_OUTLIVES_IT` were built again by the Codex
    lane and landed at `c9679e3046` (closed 2026-11-24 3:05 PM PST; red on the old code, green on the fix).
  - `TELEMETRY_HARDEN_FIX_FOUR_EDGE_CASES` has been parked by his card since 2026-11-01. The lane should not have taken
    it, so its cut job cost nothing that is owed.
- Not cut by the stop: the deviation record and the rest of the ask lane were built before 8:07 AM. They are listed
  above under "Open".
