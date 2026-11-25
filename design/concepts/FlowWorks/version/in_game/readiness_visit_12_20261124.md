# Is the pipeline ready for the next in-game visit of FlowWorks 0.1.0?

Written 2026-11-24, 4:30 PM PST, by the detached helper of
`RIMMANDRAKE_LIST_FLOWWORKS_READINESS_VISIT_TWELVE_TENS_LIST_IS_STALE`. The rule is
`design/RimMandrake/standing_rulings.md` §No mod runs forward on a broken pipeline. The form follows
`readiness_visit_10_20261124.md`.

**The next visit is visit 11, not visit 12.** Visit 11 opened at 9:27 AM PST. Its folder holds only the test lane's rows, and
the pipeline reads that as "no driver yet" (`ingame_facts`: visit 11, owed `run`, exit `absent`) [measured]. The file keeps
the name that the item gives.

Ticket states come from the ledger replay at 3:00 PM PST (1,470 open items [measured: proposed, built, ready, validated, doing]). I read the states of the
visit 10 list's tickets, and every item filed after that list, by title. I opened those that can touch this path.

Tags: [measured] = a command, a test or a code read in this run. [guess ~N%] = not proved. Classes: BLOCKS, RARE and
NOT ON PATH, as the rule defines them.

## Holds and waits above the tickets

| What | State | Whose act |
|---|---|---|
| His holds | no hold on FlowWorks or on a game: `./pipe show` ALL ON at 3 PM, and both game holds of his Explosive Knockback walk are lifted [measured, `./pipe log`] | none |
| Ceiling | about 27.9M weighted tokens spent plus a 10.5M cap passes the 25.0M ceiling, and its release is spent [measured 2:45 PM]. Read `./pipe why FlowWorks` again after this run ends: the figure moves with this run's spend [guess ~50%]. Until this run ends, plus 180 s, the tick shows this run as live and the ceiling line does not show [measured] | the Conductor's release |
| Launch | `_is_ingame_item` reads this run's item as no in-game run, so it is not a hand run of visit 11 [measured] | none |
| Games at 4:22 PM | ArchBig FREE, left running on the 13-mod `flowworks` tier. ArchSmall HELD by BENCH since 4:01 PM, for the Pyrelands walk save [measured] | none |
| Account | lukas 10% left (resets in 23 h), steven 97% left (22 h), system 3% left (20 h), Codex 99% left; jpl-genai: not on this machine [measured 3:42 PM]. The live account is lukas, so the visit may meet the account switch; the account plan handles it | none |

## What changed since the visit 10 list

| Change | Reading |
|---|---|
| Mod fix 55e9b3b0ea (reach labels stale while paused) | in the source DLL. ArchSmall holds it (DLL c5c6dc5a), ArchBig holds the old one (DLL 0cf1ed66, the 78f51ace1d build) [measured]. Its live check is owed (`unrun.jsonl`); the brief names it [measured] |
| Test change 68cd40dd4e (X8c retired) | it touches `validation_v2.py`, so `sc_canal_fire`, `sc_ways_out` and `sc_hole_prison` run again [measured] |
| `sc_hung_bridge` row of visit 10, UNRESOLVED, held by nobody | **it would have held visit 11's exit whatever visit 11 read, and the brief did not say so** [measured]. Fixed twice, see below |
| Five Steve2 rows "the build identity could not be read" | **not a fault of the identity.** All five are chain jobs. A chain job runs on modcheck's own mod list, which is no tier's list, so its row never counts (promise `a-chain-job-counting` of the Stage 6 lane page) and never replaces a row that counts [measured]. The words were false; fixed at 6e6a3d7bd4 |
| Two `sc_hung_bridge` runs lost to the site hold | `RIMMANDRAKE_RELOAD_SITE_AFTER_A_CHAIN_KILLS_ITS_COLONIST` is closed, but it does not reach FlowWorks: a dead colonist that the run starts with is no reload. The path is the lane's chain job only; the driver runs `suspension_bridge_proof.py` itself, with no site hold of modcheck [measured: code]. The FlowWorks cause stays on `HARNESS_REPAIR_CAUSE_4AFBF8A2_3` |
| `sc_walk` on the small list | it resolves 20 mods on ArchBig and on ArchSmall [measured]. Steve1 and Steve2 cannot take it: three of its mods are absent there (Dubs Bad Hygiene Lite, More Ritual Seats, VFE-Chemfuel) [measured: `visit-feed --dry`]. "Needs ArchBig" is out of date. It never ran on this list: the first run is the visit's |
| 346 UNDECLARED files against 26 changed files | **harmless.** `relate` takes the union over every row's own commit, back to `sc_river`'s of visit 2; git's 26 are since 78f51ace1d only. The count changes no verdict and no exit code (`main` reads rerun, read and deploy) [measured: code]. A check with no declared C# reruns, which is the safe side |
| Visit 11's lane rows | `sc_trench_cover_pawns`, `sc_toss_flame`, `sc_islands_walker` PASS on Steve2 at 55e9b3b0ea, untouched since [measured]. The driver runs them again anyway: the brief reads visits 1 to 10. Waste of minutes, not a wrong result (polish line) |
| `E6_rain_fills_unroofed` FAIL in the chain job of 12:02 PM | the B6 phase, off on purpose: `B6_FLOOD_FIX_RAIN_FILL_LEFT_OFF`. `sc_canal_fire`'s entry is `_x10_canal_fire` alone [measured: table] |

## The hold on `sc_hung_bridge`, and what was done

- Fixed for every mod: the in-game brief now names each earlier run that nobody classed. Ticket
  `RIMMANDRAKE_NAME_UNCLASSED_RUN_IN_VISIT_BRIEF_IT_HOLDS_LATER_PASS`, closed at 6e6a3d7bd4; `selftest_live_kinds` 28 tests PASS
  and 26 planted faults caught; red on the base [measured].
- Classed for FlowWorks: the row now reads MOD FAILURE. On ArchBig's undeployed 78f51ace1d DLL, one load of 28 read 8 of 18
  lanes `reach=False`, `view=floor`, `found=False` for 5 s with the clock standing, and True after 60 ticks, every cell
  already dug [measured]. That this fault caused the visit 10 run is inferred [guess ~90%]. Evidence, with the repeat that
  read 0 of 14 loads: `visit_10/evidence/und_oldbuild/`.
- The class is the one against the mod. With it, a PASS of `sc_hung_bridge` on the fixed build counts: simulated on
  `live_kinds.reading`, passes True, nothing held [measured].

## Components and open tickets

| # | Component | Looked? | Open ticket and what it can do | Class |
|---|---|---|---|---|
| 1 | Dispatch tick | yes: `decide_ingame` read; ticks of 34 to 54 s, peak 400 to 508 MB of 1 GB at 4:09 to 4:12 PM; no OOM, kill or failure line in 3 h (2,341 journal lines read); `selftest_maturation_dispatch` ALL PASS, `selftest_dispatch_two_games` 0 failed [measured]. `maturation_dispatch.py` changed 336 lines since the visit 10 list; `decide_ingame` was read, the rest by test | `RIMMANDRAKE_SLIM_TICK_MEMORY_PAGE_BUILD_HITS_ONE_GIG_TICK_TOOK_FIVE_MIN` (fix landed, check waits), `RIMMANDRAKE_SHRINK_TICK_DEPLOY_PLAN_PEAK_HIT_ONE_GIG` (composed mods only) | RARE |
| 1 | | | `OPS_INGAME_VISIT_DRIVE_DPOF` and `OPS_MATURATION_MOD_PAUSED_FYEB` (this ceiling), `OPS_MATURATION_MOD_STALLED_KHOT`, `RIMMANDRAKE_FIND_WHY_ARCHSMALL_SITS_FREE_TWO_MODS_AT_IN_GAME`, the three ceiling-unit items of the visit 10 list | NOT ON PATH |
| 2 | Certificate before the visit | yes: `certificate FlowWorks --to in_game` OK, 53 bars [measured] | none. Four live harnesses have no empty-game adapter; the certificate does not refuse on it | clean |
| 3 | Detached launch, clone, run end | by test and log, not line by line: `detached_helper.py` changed 133 lines since the visit 10 list; `selftest_detached_helper` PASS, `selftest_launch_wait_and_deploy` 0 failed; detached runs launch and end on it today; 435 GB free [measured] | `RIMMANDRAKE_FIND_SIX_RUNS_SHARED_ONE_PYRELANDS_CLONE`, `RIMMANDRAKE_KILL_LIVE_HOLDER_RESUME_AFTER_FIRST_SESSION` | RARE |
| 3 | | | `RIMMANDRAKE_CONTINUE_A_RUN_THE_CONDUCTOR_STOPPED_VOIDED_MEANS_NO_CARRY_ON`: only a run that the Conductor stops | RARE |
| 4 | Deploy to the game | yes: FlowWorks is stale on ArchBig only in its DLL and `.srchash`; the companion is stale on ArchBig and fresh on ArchSmall [measured]. Since a5ce93337e (11:07 AM) the tick's deploy runs in its own unit, `rm-game-deploy-*`: its page read, `selftest_game_deploy_unit` 0 failed, and one live run ended 0 in 5 min 42 s after two waits (exit 75), Explosive Knockback's walk build, kind `walk` [measured]. A `visit` kind run of it is UNRUN | `RIMMANDRAKE_REMOVE_GRANT_EXPIRY_CHECKS_ONCE_FOUR_COMPANIONS_REDEPLOYED`, `RIMMANDRAKE_PROVE_CANONICAL_GUARD_LIVE_AFTER_NEXT_DEPLOY`, `BRIDGETOOLS_DLL_REBUILD_THREE_TOOLS_MISSING` | RARE |
| 4 | | | not a ticket: a visit on ArchSmall with the walk save still in ArchBig's Saves ends with the DEPLOY line (ArchBig's copy must be the source). It is one deploy and reruns no check, and since 9f802d6866 the tick does it. A visit on ArchBig does not meet it: its launch deploys that copy | RARE |
| 5 | Driver's brief | yes: generated and read whole, then again with the new section [measured] | none open. It names 13 of 30 checks and the owed live check | clean |
| 6 | Bridge client and game lock | yes: claimed, stopped, launched and released ArchBig in this run; `selftest_game_instance` 0 failed, `selftest_game_lock` 0 failed [measured] | `RIMMANDRAKE_BIND_BRIDGE_CLIENT_TO_ITS_GAME_TWICE_HIT_WRONG_ONE` | RARE |
| 7 | Bridge tools of the 13 checks | partly: the tools of the under-deck scene ran today on ArchBig in 13 whole runs [measured]; `selftest_static_call_args_core` 38 of 38; no `[Tool(` line left the companion since 8dd570e9fa [measured: diff]; no tool's code was read again | `RIMMANDRAKE_PROVE_COMPANION_REFUSALS_THE_MINIMAL_LIST_CANNOT`, `BRIDGE_CALL_EVIDENCE_WIRE_LOST_REPLY_UNKNOWN`, `RIMMANDRAKE_ISOLATE_GAME_FREEZES_SMALLEST_LIST_BEYOND_ONE_MOD` | RARE |
| 8 | Scenes and scene library | yes: the 13 entries, their tiers and their deciders [measured] | `RIMMANDRAKE_SHRINK_FLOWWORKS_SCENES_HUNG_BRIDGE_RAN_27_TIMES`: parked to 2026-11-25; do not start it during the visit | RARE |
| 8 | | | `RIMMANDRAKE_STOP_FLOWWORKS_ORDERS_WAITING_OUT_A_PAUSED_CLOCK`, `B6_FLOOD_FIX_RAIN_FILL_LEFT_OFF`, `REVIEW_MAP_SELFTEST_FIX_SIZELESS_STATION`, `RIMMANDRAKE_RESTORE_FLOWWORKS_PIT_PROOF_SETTINGS_FOUR_NEW_LEAKS` (a setting left changed when a proof throws; the visit reads settings back per check [guess ~80%]), `RIMMANDRAKE_TRACE_FLOWWORKS_BOTTLE_LOOP_EMPTY_GONE_NONE_FILLED` (a filler chain, no Stage 6 check) | NOT ON PATH |
| 8 | | | mod work that a visit finds and routes: `RIMMANDRAKE_CLASS_DROID_AND_JAWA_GONE_IN_SHALLOW_TAR`, `RIMMANDRAKE_WARN_WHEN_RAIN_IS_FILLING_AN_OCCUPIED_PIT_KEEP_THE_FLOOD`, `RIMMANDRAKE_REPAIR_FLOWWORKS_HARNESS_SEVEN_RED_OR_BLIND_ROWS`, `RIMMANDRAKE_REPAIR_FLOWWORKS_WRONG_CHECKS_SIX_OLD_TICKETS`, `RIMMANDRAKE_PROVE_FLOWWORKS_NINE_LIVE_ROWS_OWED_ONE_VISIT` | RARE |
| 9 | Test table, rerun decision, build match | yes: `build_match check --visit 10` read whole, `rerun_relation` read; `selftest_build_match` 0 of 78 failed, `selftest_rerun_relation` 0 of 97 failed [measured] | `RIMMANDRAKE_KEEP_ROWS_WHEN_MOD_LIST_SHRINKS_TICK_OWED_196_AGAIN`: voids rows when a tier's list changes. The `flowworks` tier did not change (17 rows still count [measured]), and no check needs the full list | NOT ON PATH |
| 9 | | | `RIMMANDRAKE_FIX_CHANGE_RELATION_BLIND_TO_CSHARP_NINE_ROWS_MISSED` (its run still holds Pyrelands rows) | RARE |
| 10 | SteveDesktop lane | yes: `visit_rows.py`, the lane page and the feed's dry run read; `selftest_stage6_checks` PASS, `selftest_steve_worker` 0 failed, `selftest_steve_visit_feed` PASS [measured]. A second route: the driver can run all 13 on Archmagi | `RIMMANDRAKE_RAISE_LANE_JOB_TIMEOUT_THAT_KILLED_A_LIVE_RUN_TWICE`, `OPS_TESTQ_UNSTICK_ECPK_LZZW`, `STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO`, the FlowWorks `HARNESS_REPAIR_CAUSE_*` items (chain jobs; a row that could not look never replaces a row that counts) | RARE |
| 11 | Exit reader | yes: `read_ingame_exit` run on visits 10 and 11 and read; `selftest_live_kinds` PASS [measured] | none. Two facts for the driver, not faults: visit 11 opened before 10:20 AM, so the exit does not check the walk save's list; the VISIT4 save is on his full list. The brief tells the driver to stage a new one on the small list | clean |
| 12 | Routing and the road back | by test: `maturation_autonomy.py` changed 74 lines since the visit 10 list; `selftest_maturation_autonomy` ALL PASS; the visit 10 steward run and Pyrelands visit 9's route ended on this path today [measured: log]. `_route` and `_road_back` were not read line by line | `RIMMANDRAKE_PASS_OWNER_ITEMS_ON_ROAD_BACK_ULLAI_HELD`, `RIMMANDRAKE_SIZE_TICK_FIXER_CAP_REBUILD_STOPPED_AT_TEN`, `RIMMANDRAKE_RESUME_CAPPED_FIXER_WITH_PROGRESS_SLACK_CAPPED_TWICE_TONIGHT`, `RIMMANDRAKE_PASS_PILOT_ALIAS_TO_THE_LAUNCH_GATE` (a Test Pilot sitting) | RARE |

## Could not look

- The code of each bridge tool, and `_route` and `_road_back` line by line (as in the visit 10 list).
- The `visit` kind of the deploy unit, and `sc_walk` on the small list: UNRUN, the visit runs both.
- The open items older than the visit 10 list that no word of that list's search matched [guess ~10% that one is on the path].

## What the visit owes, and where each check can run

| Check | ArchBig | ArchSmall | Steve1, Steve2 (lane) |
|---|---|---|---|
| `sc_trench_cover_pawns`, `sc_toss_flame`, `sc_islands_walker` | yes | yes | yes; PASS at 55e9b3b0ea, untouched |
| `sc_moat_walkers`, `sc_hole_prison` | yes | yes | yes; PASS before the fix, so run again |
| `sc_canal_fire`, `sc_pit_reads`, `sc_covered_pit`, `sc_sluice`, `sc_hung_bridge` | yes | yes | a chain job only; its row never counts |
| `sc_ways_out`, `sc_pit_crowd` | yes | yes | no testq block |
| `sc_walk` | yes | yes | no: three of its mods are absent |

`sc_hung_bridge` also owes the live check of 55e9b3b0ea (`unrun.jsonl`: `loop_und.sh 12` and the shallow plant). The fault comes
about once in 28 loads, so 12 clean loops do not show the fix; the offline sweep does. The loops look for a red run.

READY. No BLOCKS ticket is open on this path. The release is the Conductor's act. ArchBig first: its launch also deploys the walk copy.
