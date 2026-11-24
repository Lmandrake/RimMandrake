# Is the pipeline ready for FlowWorks 0.1.0's in-game visit 10?

Written 2026-11-24, 5:41 AM PST, by the detached helper of
`RIMMANDRAKE_READ_FLOWWORKS_READINESS_BEFORE_VISIT_TEN_CEILING_RELEASE`. The rule is
`design/RimMandrake/standing_rulings.md` §No mod runs forward on a broken pipeline. The form follows
`readiness_visit_2_20261119.md`. The clone was at 43b06bf72c (5:17 AM), and the later commits to 5:40 AM were read by log.
Ticket states come from the ledger replay (1,539 open items [measured]). I searched those items by name and title for this
path, and I opened the ones that can touch it. I did not open all 1,539. A ticket that no word of mine matched is not
listed [guess ~10% that one such ticket is on the path].

Tags: [measured] = a command, a test or a code read in this run. [guess ~N%] = not proved. Classes: BLOCKS, RARE and
NOT ON PATH, as the rule defines them.

## The path, in order

1. The Conductor releases the ceiling. The tick launches the driver on the first free game (ArchBig, then ArchSmall).
2. `launch_mod` checks the bridge, the companion and the game's FlowWorks copy. A stale companion or copy is repaired in
   one game-down window. The driver gets its brief.
3. The driver runs 29 of the 30 Stage 6 checks, and the lane sends 24 of them to Steve1 and Steve2 as well.
4. `read_ingame_exit` and the build match read the visit. A steward run routes the result, or the road back takes a line.

## Holds and waits above the tickets

| What | State | Whose act |
|---|---|---|
| His holds | FlowWorks is not in `mod_owner_hold.json` [measured] | none |
| Switch | `./pipe show` reads ALL ON, FlowWorks ON [measured] | none |
| Ceiling | 24.0M weighted tokens spent, plus a 7.5M cap (Opus), passes the 25.0M ceiling; the old release is spent [measured] | the Conductor's release. Read `./pipe why FlowWorks` again first: its `--read-tokens` figure can move after this run ends [guess ~50%] |
| This helper | it reads as live on FlowWorks until it ends, plus 180 s [measured: `decide_ingame`]. Its name is not an in-game run's, so the tick will not read it as a hand run [measured] | a wait |
| Games | ArchBig HELD by BENCH since 4:29 AM (Gimme Some Slack visit 3). ArchSmall FREE [measured 5:33 AM] | a wait for ArchBig, or ArchSmall now |
| Which game | on ArchSmall the visit cannot meet its exit: `sc_walk` needs the full list, and no other Stage 6 check decides its bars `inv_settings` and `walk_moat_season` [measured]. A later visit that owes only `sc_walk` waits for ArchBig by itself (`full_list_only`) [measured: code read]. Each such visit needs its own ceiling release | the Conductor: release when ArchBig is free to finish in one visit, or release now and pay a second, small visit |
| Account | lukas 49% left, steven 97% left, system 3% left, Codex 20% left [measured 5:26 AM]; jpl-genai: not on this machine | none |

## Tonight's events, weighed

| Event | Reading |
|---|---|
| edddd2f2d5, the false pause | fixed. `ingame_facts` reads `owed run`, exit `absent`, with 20 lane rows (28 at 5:40 AM) in `visit_10/rows.jsonl`. `selftest_maturation_dispatch` ALL PASS, `selftest_stage6_checks` PASS [measured] |
| `RIMMANDRAKE_FIX_CHANGE_RELATION_BLIND_TO_CSHARP_NINE_ROWS_MISSED` | both halves landed: 5e1ee7c2d0 (5:05 AM, the relation) and ffa6f22a57 (5:25 AM, the walk gate). `selftest_rerun_relation` 0 of 71 failed [measured]. The FlowWorks relation now reruns `sc_trench_cover_pawns` and `sc_islands_walker`, which name no C# [measured]. The one check kept is `sc_river`: `exercises.json` lists `Source/Rivers/` for it, and no commit touched that folder since its PASS at 65926ef481 (visit 2) [measured]. So the visit names the right 29 |
| `sc_pit_crowd`, the raider rescue | `sc_pit_crowd` has no row, so it is in the 29 [measured]. Its offline selftest passes 10 cases [measured]. It decides no bar. The raider rescue has no live scene while raid tests are paused, and its bars moved to 0.2.0 (the brief's steward decision of 2026-11-23). Mod work, not a pipeline fault |
| the scene that read COULD NOT LOOK on Steve1 | `sc_source_pays`: its river site is built on the `fw_gss_sitting` tier and ran on `flowworks`. Fixed at fb32ce8cd7 (5:12 AM); its second run (J20261124T130715Z-246d95) was sent before the fix and read the same; not run since [measured] |

## Components and open tickets

| # | Component | Looked? | Open ticket and what it can do | Class |
|---|---|---|---|---|
| 1 | Dispatch tick | yes: code read of `decide_ingame`, `pick_game`, `reserve_refused`; ticks of 37 to 57 s, peak 396 to 588 MB of 1 GB at 5:23 to 5:27 AM; no OOM kill, failure or timeout line in 24 h [measured] | `RIMMANDRAKE_SLIM_TICK_MEMORY_PAGE_BUILD_HITS_ONE_GIG_TICK_TOOK_FIVE_MIN`: a killed tick; fe171bf3ca landed 5:11 AM | RARE |
| 1 | | | `RIMMANDRAKE_SHRINK_TICK_DEPLOY_PLAN_PEAK_HIT_ONE_GIG`: a tick that runs a composed biomes deploy can hit 1 GB; FlowWorks is not composed | RARE |
| 1 | | | `OPS_DISPATCH_CLONE_BEHIND_UNSTICK_YUYW` (the clone reads level now), `OPS_MATURATION_MOD_PAUSED_FYEB` (this ceiling), `OPS_MATURATION_MOD_STALLED_KHOT`, `RIMMANDRAKE_CUT_TICK_DRVFS_WALK_OF_DEPLOYED_BIOMES_STATS_TEN_THOUSAND` (slow only) | NOT ON PATH |
| 1 | | | `RIMMANDRAKE_NAME_STAGE_CEILING_DANGER_OR_REMOVE_THE_LIMIT`, `RIMMANDRAKE_KEEP_STAGE_CEILING_IN_TOKENS_NOT_LIST_DOLLARS`, `RIMMANDRAKE_PRICE_CEILING_AND_DESIGNER_TOKENS_FOR_PINNED_MODEL`: units and reason only; the driver is Opus | NOT ON PATH |
| 2 | Certificate before the visit | yes: `certificate FlowWorks --to in_game` OK, 53 bars [measured] | none. Four live harnesses have no empty-game adapter (DID NOT RUN); the certificate does not refuse on it | clean |
| 3 | Detached launch, clone, run end | yes: `game_env` code read | `RIMMANDRAKE_FIND_SIX_RUNS_SHARED_ONE_PYRELANDS_CLONE`: seen once, needs overlapping launches of one item | RARE |
| 3 | | | `RIMMANDRAKE_KILL_LIVE_HOLDER_RESUME_AFTER_FIRST_SESSION`, `RIMMANDRAKE_LIFT_VOID_HOLD_ON_DONE_RUN_NOT_MIDNIGHT` (Designer), `RIMMANDRAKE_STOP_SHARED_COPIES_OUTLIVING_THEIR_LENDER`, `RIMMANDRAKE_RECONCILE_POOL_CAPS_SIXTEEN_CLONES_OUTWEIGH_70_GB` (433 GB free [measured]) | NOT ON PATH, the first RARE (only a killed visit) |
| 4 | Deploy to the game | yes: the copy and the companion read stale on ArchBig and ArchSmall [measured]; `launch_mod` repairs both in one window (code read); `selftest_launch_wait_and_deploy` 0 failed [measured]. The repair itself is UNRUN on this build | `RIMMANDRAKE_REMOVE_GRANT_EXPIRY_CHECKS_ONCE_FOUR_COMPANIONS_REDEPLOYED`, `RIMMANDRAKE_PROVE_CANONICAL_GUARD_LIVE_AFTER_NEXT_DEPLOY`, `BRIDGETOOLS_DLL_REBUILD_THREE_TOOLS_MISSING` (the repair rebuilds the DLL) | RARE |
| 5 | Driver's brief and role file | yes: the brief generated and read whole [measured]. There is no role file for an in-game driver: the brief is the whole | none. The brief offers the driver 24 checks to queue on the lane and does not say that 12 already read PASS there on the current build 78f51ace1d tonight. Waste, not a wrong result | clean |
| 6 | Bridge client and game lock | yes: `game_env` carries the game's whole environment and WSLENV into python.exe [measured: code]; `game_lock` read; `selftest_game_instance` 0 failed [measured] | `RIMMANDRAKE_BIND_BRIDGE_CLIENT_TO_ITS_GAME_TWICE_HIT_WRONG_ONE`: the launcher half is done; a shell with no game named could still reach ArchBig. The brief tells a driver to eval the env | RARE |
| 6 | | | `RIMMANDRAKE_LET_LOCK_CLAIM_PASS_HIS_HOLD_STAGING_RAN_UNLOCKED` (no hold stands), `RIMMANDRAKE_FIX_BRIDGE_RELEASE_WRAPUP_RESTORE_TRACEBACK_EXIT_ONE` (its note of 5:16 AM says fixed at 61e38119d3) | NOT ON PATH |
| 7 | Bridge tools the 29 checks call | yes: every `jawa/` tool that the scene files name is in the companion source [measured]; `jawa/order_pawn` read; `selftest_static_call_args_core` 38 of 38 [measured]; 12 FlowWorks checks read PASS on Steve1 in jobs queued 4:14 to 5:11 AM PST [measured], on the companion of those jobs' commits, the last after the newest companion commit caf6eb8af5 [guess ~90% that it is today's companion, no hash read back]. Not each tool's code | `RIMMANDRAKE_FIX_BRIDGE_STEPPED_PAWNS_DRAWN_ON_OLD_SQUARE`: a capture can draw a walked pawn on its old square. Looks only; the rows I opened read state | RARE |
| 7 | | | `RIMMANDRAKE_PROVE_COMPANION_REFUSALS_THE_MINIMAL_LIST_CANNOT`, `BRIDGE_CALL_EVIDENCE_WIRE_LOST_REPLY_UNKNOWN`, `BRIDGE_RECONCILE_WIRE_CLOSED_NOT_CURED` (both built), `RIMMANDRAKE_ISOLATE_GAME_FREEZES_SMALLEST_LIST_BEYOND_ONE_MOD` (timing rows only) | RARE |
| 7 | | | the Bridge v2 build items, `TILE_TEMP_CACHE_RESET_TOOL_1`, `ADVANCEUNTIL_WIRE_PER_TICK_STOP`, `CONDWATCH_BUILD_OWNED_RINGS`, `STEPCALLS_MIGRATE_WHERE_VERDICTS_HOLD` | NOT ON PATH |
| 8 | Scenes and scene library | yes: the 29 entries, their files and the offline deciders (certificate) [measured] | `RIMMANDRAKE_SAY_WHY_MOAT_WALKER_ORDER_IS_REFUSED_TWICE_ON_STEVE`: `sc_moat_walkers` first leg reads UNMEASURED, 3 of 3 on Steve1; the driver will meet it and classes it. Its bar `moat_drains_and_burns` has three other Stage 6 deciders (`sc_sluice`, `sc_hole_prison`, `sc_toss_flame`) [measured]. Its premise is wrong, see below | RARE |
| 8 | | | `RIMMANDRAKE_STOP_FLOWWORKS_ORDERS_WAITING_OUT_A_PAUSED_CLOCK` (757 s lost in visit 9), `B6_FLOOD_FIX_RAIN_FILL_LEFT_OFF` (the visit runs B0 and B4 only), `REVIEW_MAP_SELFTEST_FIX_SIZELESS_STATION` | NOT ON PATH |
| 8 | | | `RIMMANDRAKE_SHRINK_FLOWWORKS_SCENES_HUNG_BRIDGE_RAN_27_TIMES` (doing, not live): it edits scenes; do not start it during the visit | RARE |
| 8 | | | `RIMMANDRAKE_REPAIR_FLOWWORKS_HARNESS_SEVEN_RED_OR_BLIND_ROWS`, `RIMMANDRAKE_REPAIR_FLOWWORKS_WRONG_CHECKS_SIX_OLD_TICKETS`, `RIMMANDRAKE_DIAGNOSE_FLOWWORKS_PUMPS_GIVE_NO_PRESSURE_FOUR_RUNS`, `RIMMANDRAKE_FIX_X8C_LID_WALKER_DRAWN_AT_GROUND_LIVE_FAIL`, `RIMMANDRAKE_TRACE_FLOWWORKS_RAIDER_IN_OPEN_PIT_WALKED_OUT`, `RIMMANDRAKE_PROVE_FLOWWORKS_NINE_LIVE_ROWS_OWED_ONE_VISIT`: mod or check work that a visit finds and routes | RARE |
| 9 | Test table and rerun decision | yes: `ingame_facts`, `rerun_relation` and `exercises.json` read [measured] | `RIMMANDRAKE_FIX_CHANGE_RELATION_BLIND_TO_CSHARP_NINE_ROWS_MISSED` (doing): both halves landed; its run still holds the ten Pyrelands rows | RARE |
| 10 | SteveDesktop lane | yes: boundary page and `visit_rows.py` read, `cmd_start` read, 7 FlowWorks visit jobs DONE tonight and two jobs running at 5:38 AM, `selftest_stage6_checks` PASS, `selftest_steve_worker` 0 failed [measured]. The lane is a second route; the driver can run all 29 on Archmagi | `RIMMANDRAKE_FIX_STEVE_WORKER_VALIDATES_JOB_BEFORE_PULL` and `OPS_TESTQ_UNSTICK_ECPK_LZZW`: a refused job can stall the lane (47 min tonight). The visit does not wait on the lane | RARE |
| 10 | | | seven FlowWorks `HARNESS_REPAIR_CAUSE_*` items (surprises and site holds in chain jobs) and `STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO`: a chain job's row reads COULD NOT LOOK and never replaces a row that counts | RARE |
| 10 | | | `RIMMANDRAKE_SEND_STAGE_SIX_CHECKS_TO_STEVE_GAMES_NONE_CARRY_A_BLOCK` (doing, live): it made this route and still edits it | RARE |
| 10 | | | `RIMMANDRAKE_LEAVE_PASSED_GUARDS_ALONE_WHOLE_DLL_IS_VERSION`, `RIMMANDRAKE_KEY_TESTQ_SKIP_CACHE_ON_INPUTS`, `RIMMANDRAKE_WAIT_AND_WAKE_ON_ONE_LANE_JOB`, `RIMMANDRAKE_ASK_LANE_IN_ONE_LINE_AFTER_HOST_FACTS`: lane cost | NOT ON PATH |
| 11 | Exit reader and build match | yes: `read_ingame_exit` code read in part, `selftest_build_match` 0 of 76 failed, `selftest_live_kinds` PASS [measured]; `visit_*/rows.jsonl` merges by union, so the lane and the driver do not collide [measured] | none. Known, not a ticket: at the exit the ArchBig copy of FlowWorks must be the current source (a deploy, reruns no check); Explosive Knockback met this at 5:10 AM | clean |
| 12 | Routing and the road back | yes: the limit code read, 0 of 12 stewards and 1 of 12 fixers used, `selftest_maturation_autonomy` ALL PASS, and a route steward for Explosive Knockback visit 6 runs on this path now [measured]. `_route` and `_road_back` were not read line by line | `RIMMANDRAKE_PASS_OWNER_ITEMS_ON_ROAD_BACK_ULLAI_HELD` (needs an owner item), `RIMMANDRAKE_SIZE_TICK_FIXER_CAP_REBUILD_STOPPED_AT_TEN`, `RIMMANDRAKE_RESUME_CAPPED_FIXER_WITH_PROGRESS_SLACK_CAPPED_TWICE_TONIGHT`: a fixer that stops at its cap | RARE |
| 12 | | | `RIMMANDRAKE_MOVE_STAGES_BY_PROGRAM_REVERSES_A_WRITTEN_NEVER` (a build not landed), `RIMMANDRAKE_OWN_RED_SUPPORTING_TEST_SIXTEEN_HOURS_UNSEEN`, `RIMMANDRAKE_WATCH_INGAME_VISIT_OWED_NO_DRIVER_UNSEEN` (an alarm only) | NOT ON PATH |

## Could not look

No component of the path is unlooked: each row above carries a reading. Inside them, these were not read:
- the code of each bridge tool, and `_route` and `_road_back` line by line (their tests and live runs were read instead);
- the repair window of row 4 on this build, and an ArchSmall game on today's companion (UNRUN: the launch does both);
- the open items that no word of this path matched.

## One false premise, noted on its ticket

`RIMMANDRAKE_SAY_WHY_MOAT_WALKER_ORDER_IS_REFUSED_TWICE_ON_STEVE` reads `order: False` as a refusal. `jawa/order_pawn` with
`waitTicks=0` reads `success` as arrival (its own text: "success is true only when every pawn is standing on the requested
cell after ticks passed"), so False is expected before the walk [measured: code]. The fault left is that the colonist
never left (65,54) in 120 reads. The order's `canReach` and `accepted` fields are the reading to keep. Its last line also
says a visit 10 driver holds `concept_scenes.py`; no driver is live [measured].

READY. No BLOCKS ticket is open on this path. The release is the Conductor's act.
