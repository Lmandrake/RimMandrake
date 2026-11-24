# Is the pipeline ready for Pyrelands 0.1.0's return to in-game acceptance (visit 9)?

Written 2026-11-24, 7:10 AM PST, by the detached helper of
`RIMMANDRAKE_DECLARE_PYRE_CHECKS_CSHARP_SO_TEN_RERUN_NOT_FORTY`. The rule is `design/RimMandrake/standing_rulings.md` §No mod
runs forward on a broken pipeline. The form follows `design/concepts/FlowWorks/version/in_game/readiness_visit_10_20261124.md`
(5:41 AM), and the component rows it read two hours ago are cited as "FlowWorks list" where nothing landed on them since. The
clone was at f6690c93e2. Ticket states come from the ledger replay (1,528 open items [measured]). I searched those items by
name and title for this path and opened the ones that can touch it. I did not open all 1,528 [guess ~10% that a ticket on
the path is not listed].

Tags: [measured] = a command, a test or a code read in this run. [guess ~N%] = not proved. Classes: BLOCKS, RARE and
NOT ON PATH, as the rule defines them.

## The path, in order

1. The Conductor runs `./pipe on Pyrelands`. The tick's act `autovisit` moves the record from `his_walk` to `in_game`, landed,
   and opens visit 9.
2. The tick launches the driver on the first free game. `launch_mod` deploys the composed biomes (both games hold the DLL of
   visit 8) in one game-down window.
3. The driver runs 18 checks (below). The lane may take the minimal-list ones.
4. `read_ingame_exit` and the build match read the visit. The exit waits for one fresh reader of a6f05380df.

## What visit 9 runs

`ingame_to_run` at f6690c93e2 [measured]: 18 of 40, `sc_full_list_smoke` the only one that needs the full list. 17 are touched
by a6f05380df. The eighteenth, `sc_ullai`, has a row from visit 7, made before 510d96f7b8 changed `MapComponent_BurnLine.cs`.
The other 22 rows stand: 15 of visit 7 and 7 of visit 8 [measured]. So visit 8's "40 of 40 PASS" held 24 rows of visit 7.

`sc_burn_line_walks`, `sc_ash_watered`, `sc_burn_compounds`, `sc_grass_regreens`, `sc_scorchfruit`, `sc_ashwallow`, `sc_ullai`,
`sc_no_rain`, `sc_reload_keeps_the_burn`, `sc_full_list_smoke`, `sc_heat_dome`, `sc_fire_dusts_ash`, `P_mapgen_log`,
`P_grass_cover`, `P_ambient_ash_drift`, `P_blackrain`, `P_gate`, `sc_fire_walks_with_wind`.

## Holds and waits above the tickets

| What | State | Whose act |
|---|---|---|
| His holds | Pyrelands is not in `mod_owner_hold.json` [measured] | none |
| Switch | OFF (act ct_000167, 4:54 AM) [measured]. Its own lift condition (ten rows pass) cannot be met while it is off | the Conductor: `./pipe on Pyrelands --why "..."` |
| Ceiling | 7.5M weighted tokens (Opus) counted at in-game since this arrival, plus a 7.5M cap, is under the 25.0M ceiling: no release [measured: `stage_spent`, `ceiling_gate` at 6:58 AM] | none |
| Certificate | it read REFUSED on 5 of 16 bars at 6:40 AM (7 stale stamps, and T_SETTINGS_SWEEP_OFFLINE, edited by a6f05380df and never seen red). `certificate --run` and `red-seen` done; OK on 16 bars at 6:50 AM [measured], landed with this list | done |
| Fresh reader | a6f05380df owes one, by `fix_readers_owed` at the exit. No `fix_reviews.jsonl` names that commit [measured] | a fresh run, in the visit |
| This helper | reads as live on Pyrelands until it ends, plus 180 s [measured: `live_units`] | a wait |
| Games | ArchBig FREE at 6:55 AM (its Gimme Some Slack driver ended). ArchSmall HELD by FlowWorks visit 10 since 5:50 AM [measured] | none, or a wait if ArchBig is taken first |
| Account | lukas 48% left (32 h), steven 97% left (31 h), system 3% left (29 h), Codex 17% left (6.7 h) [measured 6:57 AM]; jpl-genai: not on this machine | none |

## Components and open tickets

| # | Component | Looked? | Open ticket and what it can do | Class |
|---|---|---|---|---|
| 1 | Walk gate and act `autovisit` | yes: `walk_owed` reads 18 owed, no cause, on `/home/mandrake/rm/dispatch` at f6690c93e2 [measured]; `selftest_walk_owes_checks` 0 of 15 failed, `selftest_maturation_autonomy` ALL PASS [measured by hand: the publish check ran past 180 s] | `RIMMANDRAKE_FIX_CHANGE_RELATION_BLIND_TO_CSHARP_NINE_ROWS_MISSED` (doing): the live act was never seen; its wait is this lift | RARE |
| 1 | | one of five readings said "Pyrelands is not deployed" though it is: the walk folder's hash could not be read once, during a deploy or a game write [guess ~60%]. `could-not-look-is-not-clean`: the tick takes no act and reads again | none | RARE |
| 2 | Dispatch tick | yes: peaks 418 to 953 MB of 1 GB at 6:52 to 6:57 AM, no kill in 24 h [measured: journal] | `RIMMANDRAKE_SHRINK_TICK_DEPLOY_PLAN_PEAK_HIT_ONE_GIG`: Pyrelands is composed, so this visit's launch runs that plan. It peaked at 1 GB at visit 2 and no tick was killed then or in visits 3 to 8 (six launches) [guess ~90% it holds again]. A kill voids the tick; the launch is read again | RARE |
| 2 | | | `RIMMANDRAKE_SLIM_TICK_MEMORY_PAGE_BUILD_HITS_ONE_GIG_TICK_TOOK_FIVE_MIN` (doing), `RIMMANDRAKE_CUT_TICK_DRVFS_WALK_OF_DEPLOYED_BIOMES_STATS_TEN_THOUSAND` (66 to 125 s per tick on this mod): slow only | RARE |
| 2 | | | the `OPS_MATURATION_*` alarms (idle, paused, stalled, hand act) and `OPS_DISPATCH_CLONE_BEHIND_UNSTICK_YUYW` (dispatch was level at f6690c93e2 [measured]) | NOT ON PATH |
| 2 | | | `RIMMANDRAKE_NAME_STAGE_CEILING_DANGER_OR_REMOVE_THE_LIMIT`, `RIMMANDRAKE_KEEP_STAGE_CEILING_IN_TOKENS_NOT_LIST_DOLLARS` | NOT ON PATH |
| 3 | Offline certificate | yes: OK on 16 bars; DID NOT RUN: 6 in-game scenes have no empty-game adapter [measured] | none | clean |
| 4 | Launch, clone, run end | FlowWorks list | `RIMMANDRAKE_FIND_SIX_RUNS_SHARED_ONE_PYRELANDS_CLONE` (overlapping launches of one item, seen once), `RIMMANDRAKE_KILL_LIVE_HOLDER_RESUME_AFTER_FIRST_SESSION` (a killed visit) | RARE |
| 5 | Deploy to the game | yes: both games hold `FireEcologyHook.dll` 5cf9f9a168 and the source is 728425fd7b [measured], so the launch deploys; `selftest_launch_wait_and_deploy` 0 failed [measured]. The repair is UNRUN on this build | `RIMMANDRAKE_REMOVE_GRANT_EXPIRY_CHECKS_ONCE_FOUR_COMPANIONS_REDEPLOYED`, `RIMMANDRAKE_PROVE_CANONICAL_GUARD_LIVE_AFTER_NEXT_DEPLOY` | RARE |
| 6 | Driver's brief | yes: rendered for visit 9 from the live record with the move added in memory, 223 lines, read in its check list and its owed sections [measured]: it names 18 of 40 checks and the one full-list check. Its wall-time bound says 3 hours; visit 8 took nine. The bound is the driver's own stopping point, and the 18 include two long chains | none | RARE |
| 7 | Game lock and bridge client | yes: `game_lock query`, `selftest_game_instance` 0 failed [measured] | `RIMMANDRAKE_BIND_BRIDGE_CLIENT_TO_ITS_GAME_TWICE_HIT_WRONG_ONE` (a shell with no game named) | RARE |
| 7 | | | `RIMMANDRAKE_LET_LOCK_CLAIM_PASS_HIS_HOLD_STAGING_RAN_UNLOCKED` (2e9cff556b landed), `RIMMANDRAKE_FIX_BRIDGE_RELEASE_WRAPUP_RESTORE_TRACEBACK_EXIT_ONE` | NOT ON PATH |
| 8 | Bridge tools of the 18 scenes | in part: visit 8 called them on ArchBig last night; the tool code was not read | `RIMMANDRAKE_FIX_BRIDGE_STEPPED_PAWNS_DRAWN_ON_OLD_SQUARE` (captures of walked pawns), `BRIDGE_CALL_EVIDENCE_WIRE_LOST_REPLY_UNKNOWN`, `RIMMANDRAKE_PROVE_COMPANION_REFUSALS_THE_MINIMAL_LIST_CANNOT` | RARE |
| 9 | Scenes and site builder | yes: the 18 chains read for this declaration; `T_SITE`, `T_WALK_SMALL` and the other offline deciders green (certificate) [measured] | `RIMMANDRAKE_SHARE_PYRELANDS_SITE_LOAD_BETWEEN_SHORT_CHAINS` (cost), `FIXTURES_FIX_REST_STILL_COMPRESSED` (a registry save; visits build fresh sites) | NOT ON PATH |
| 9 | | | `RIMMANDRAKE_CLASS_PYRE_CONTROL_PAD_BURN_NOBODY_LIT`: an UNRESOLVED run of `sc_burn_compounds`, visit 7, not classed on its ticket. Visit 8 passed the scene and its exit was met; the scene runs again here | RARE |
| 9 | | | `RIMMANDRAKE_SHOW_PYRE_GRASS_UNDER_ASH_COVER_COUNTED_UNSEEN`, `RIMMANDRAKE_READ_PYRE_LONG_RUN_FOUR_OWED_ZHAKKA_FIRST`, `RIMMANDRAKE_STAGE_PYRE_POND_SO_SHORE_RING_CLAUSE_GETS_A_READING`: mod or check work that a visit finds and routes | RARE |
| 10 | Rerun decision | yes: f6690c93e2; `selftest_rerun_relation` 0 of 97 failed, 21 of 22 planted code faults caught [measured]; the other is equivalent by reading [guess ~85%]. A wrong declaration is caught by nothing in the relation (boundary.md, a-wrong-declaration): 4 of 4 planted were missed. Three of those four checks also have an UNRUN row, so the exit holds them; `sc_fire_dusts_ash` has none | none | RARE |
| 11 | SteveDesktop lane | FlowWorks list | `HARNESS_REPAIR_CAUSE_F6CADE57_2` (a Pyrelands lane job read UNMEASURED, a downed colonist), `RIMMANDRAKE_FIX_STEVE_WORKER_VALIDATES_JOB_BEFORE_PULL`, `OPS_TESTQ_UNSTICK_ECPK_LZZW`, `RIMMANDRAKE_SEND_STAGE_SIX_CHECKS_TO_STEVE_GAMES_NONE_CARRY_A_BLOCK` (its run ended, it waits) | RARE |
| 12 | Exit reader and build match | yes: `selftest_build_match` 0 of 76, `selftest_stage6_checks` PASS, `selftest_live_kinds` PASS, `selftest_maturation_dispatch` ALL PASS, `selftest_pipeline_pause` ALL PASS [measured] | none | clean |
| 13 | Routing and road back | FlowWorks list; not read line by line | `RIMMANDRAKE_PASS_OWNER_ITEMS_ON_ROAD_BACK_ULLAI_HELD`: a `needs=owner` item can hold the mod after its one fixer; it happened at Pyrelands visit 6. It needs an owner item on a visit finding | RARE |
| 13 | | | `RIMMANDRAKE_RESUME_CAPPED_FIXER_WITH_PROGRESS_SLACK_CAPPED_TWICE_TONIGHT`, `RIMMANDRAKE_UNSTICK_PYRELANDS_FIXER_COUNT_TWELVE_FOUR_REFUSED` (limit raised to 20, 2026-11-21) | RARE |
| 14 | His walk after the visit | not read | `RIMMANDRAKE_FREE_PYRE_WALK_SAVE_SKY_TUTOR_PINS_CLEAR`, `RIMMANDRAKE_SHOW_PYRE_HIS_WALK_FOUR_PICKS_ULLAI_FIRST`, `RIMMANDRAKE_SPREAD_SHADE_DASH_SEVEN_ANIMALS_ON_ONE_CELL`: the walk save is restaged before Stage 8. The visit does not need it | NOT ON PATH |

## Could not look

- each bridge tool's code, and `_route` and `_road_back` line by line;
- the live act `autovisit` and the repair deploy on this build: both UNRUN;
- the open items that no word of this path matched.

No component of the path is unlooked: each row above carries a reading, or cites the FlowWorks list of 5:41 AM.

READY. No BLOCKS ticket is open on this path. The lift is the Conductor's act.
