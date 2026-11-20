# Is the pipeline ready for FlowWorks 0.1.0's move to Stage 6 (in-game visit 2) by the game-only road?

**Verdict: READY** (refreshed 2026-11-19, 8:31 PM PST, detached helper on
`RIMMANDRAKE_UNBLOCK_GAME_ONLY_ADVANCE_AT_BLIND_EXIT`). No BLOCKS row is open. Row 1 cleared by the reader change
07ba8608f8 (the Conductor's route b): a dry `evaluate` of the game-only move reads `ok True`, 8 clauses passed, 0 refused,
hand step `steward_confirms` only [measured 8:31 PM]. The certificate still passes in that evaluate (`judge_certificate`
clause) [measured 8:31 PM]; tonight's run read 55 of 55 bars certified [measured 8:04 PM]. Two launch gates are not
clean, and neither is a ticket: the game's FlowWorks copy differs from the repo, and the bridge companion now reads
STALE (both in the next table). `launch_mod` refuses the visit until each is fixed, which is the correct refusal.

The rule is `design/RimMandrake/standing_rulings.md` §No mod runs forward on a broken pipeline. The format follows
`D:\ClaudeWork\rimmandrake\conductor\pipeline_lanes_20261119.md` and the 4:06 PM refresh
`D:\ClaudeWork\rimmandrake\conductor\readiness_refresh_20261119.md`. That refresh read the shared Stage-6 path for
GimmeSomeSlack (driver, runner, bridge, spend cap), and the Conductor switched GimmeSomeSlack on from it at 4:20 PM (act
ct_000074). Ticket states were read live from the ledger at about 7:50 PM PST, after `./sync` to 2f2e08f0b. A state
read is not a code read. Each row says which kind of read it is.

Tags: [measured] = a command or a code read tonight. [guess ~N%] = not proved. [from <list>] = read by an earlier list
today, not again by me.

## The path, in order

1. The Conductor runs the advance (blind_challenge -> in_game, game-only road).
2. `./pipe` already reads FlowWorks ON (act ct_000073). The tick launches the in-game driver once a slot is free
   (`max_live` 1) and `launch_mod`'s gates pass (mod copy, companion, certificate).
3. The driver holds the bridge, restarts the game on the `flowworks` tier and runs the 32 Stage-6 tests of
   `version/test_table.json` [measured]. The five game-side tickets below are among them.
4. `read_ingame_exit` reads visit 2. A FAIL goes back along the road from Stage 6 (fixer, Test Pilot).

## Holds and waits above the tickets

| What | State | Whose act |
|---|---|---|
| His holds | FlowWorks is not in `mod_owner_hold.json` (the held mods: Contagion, Cauldron, FeverWood, GelatinousSlime, LeaningScrub, Stillsand, Graffiti) [measured] | none |
| One mod at a time (`max_live` 1) | GimmeSomeSlack in-game visit 2 is live (`rm-detached-bench-rimmandrake-drive-gimmesomeslack-in-game-1795143532`, 50 min at 7:49 PM) [measured: `maturation_dispatch.py status`]. FlowWorks launches only after it ends. | a wait |
| This helper counts as live on FlowWorks | `maturation_dispatch.py status`: "FlowWorks wait live waiting on rm-detached-bench-rimmandrake-clear-flowworks-paperwork-to-…" [measured]. Its title names the mod (finding 1 of the 4:06 PM refresh, not filed). It ends when this run ends. | a wait, not a ticket |
| The game's FlowWorks copy | `maturation.mod_deployed(FlowWorks)`: "differs from the repo (~ Assemblies/RimMandrakeFlowWorks.dll, ~ .srchash)" [measured]. `launch_mod` refuses the visit until it is deployed. The refusal is correct. | Conductor act, with the game down (GSS holds the game now): `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod FlowWorks --apply` |
| Bridge companion | `maturation.companion_current()`: STALE at 8:26 PM, embedded source hash f38860ed43de, the companion sources now hash 209877e3ebed [measured]. It read FRESH at 8:00 PM, so a commit to the companion sources came in between. `launch_mod` checks the companion. | Conductor act or the tick's own rebuild, with the game down [guess ~60% that the tick rebuilds it by itself] |
| Driver spend cap | `ingame_cap_usd` 30, `ingame_model` opus, `ingame_auto_runs_per_visit` 1 [measured: `maturation_dispatch.json`]. 32 Stage-6 tests; visit 1 ran its 31 [measured: visit_1/SUMMARY.md]. A stop at the cap reads `visit_unfinished`, and the Conductor relaunches it with `--resume` [from the 4:06 PM list]. | Conductor decision, no ticket |

## Components and open tickets

| # | Component | Looked? | Open ticket and what it can do | Class | Item |
|---|---|---|---|---|---|
| 1 | The advance (`maturation.evaluate`, blind_challenge -> in_game with `--game-only`) | yes [measured 8:31 PM: a dry `evaluate`, writes nothing] | none. `RIMMANDRAKE_UNBLOCK_GAME_ONLY_ADVANCE_AT_BLIND_EXIT` landed at 07ba8608f8: on a game-only move whose `game_only` clause passes, `exit_met` does not count the new judge owed for cycle 4's four FIXED Problems, nor the SHEET, THIRST and DRILL rows (each bar is carried by a named game-only item). `read_exit` reads cycle 4 `met` that way. An unfixed Problem, an uncarried offline row, and every other move still refuse (selftest_maturation_game_only_exit.py; each guard's planted fault seen red) | clean | none |
| 2 | Certificate before the visit (`judge_certificate`, `--to in_game`) | yes [measured] | none: `certificate FlowWorks --to in_game` rc 0, 55 of 55 bars certified [measured 8:04 PM]. A later commit to a decider's inputs makes its stamp stale again; the tick reruns a stale stamp at zero tokens [from the 4:06 PM list]. | clean | none |
| 3 | Certificate: empty-game check on in-game scenes | yes [measured] | `scene_hole_prison` was not examined ("not in STAGE3_SCENES"). FIXED tonight: 65926ef481 adds it, and its selftest was red first and green after. `scene_empty_game.py --json` reads `vacuous: []` over all 18 scenes [measured]. 4 harnesses (live_session, river_scenes_walk, suspension_bridge_proof, validation_v2) have no empty-game adapter. The certificate reads them as DID NOT RUN and does not refuse. I did not read those 4 files. | RARE (a vacuous PASS needs a scene that stages nothing and reads PASS; visit 1's rows from them were real readings) | none |
| 4 | Tick, control store, switch | yes [measured: `./pipe show` rev 74: ALL ON, FlowWorks ON] | `RIMMANDRAKE_FIX_SLICE_REVIEW_TWENTY_FINDINGS_QUEUE_FIRST` (state done, not closed): page and grant findings | NOT ON PATH [from the GSS lists] | as named |
| 5 | Detached launch and run end | state read only | `RIMMANDRAKE_KILL_LIVE_HOLDER_RESUME_AFTER_FIRST_SESSION`: live proof of a killed holder's resume, not run. The lane `RIMMANDRAKE_CLOSE_DETACHED_RUN_ENDS_AND_CLONE_LEFTOVERS` is closed. | RARE (only a killed visit reaches it) | as named |
| 6 | Live driver, in-game runner (`decide_ingame`, `launch_mod` in-game branch, `concept_scenes.py`) | partly: code read for GSS [from the 4:06 PM list]; the FlowWorks scenes table was loaded and run on an empty game tonight [measured] | none open on the runner. `RIMMANDRAKE_READ_FOREIGN_DEF_NOT_FOUND_AS_LIST_FACT`, `RIMMANDRAKE_WAIT_LOAD_READY_UNTIL_CURRENTMAP_SET` and `RIMMANDRAKE_FIX_VALIDATION_CORE_FOREIGN_DEFS_AND_GATES` are closed [measured]. | clean | none |
| 7 | Bridge, game start, companion tools | state read only | `RIMMANDRAKE_TELL_TRUE_BRIDGE_TOOL_OUTCOME` (live proof UNRUN); `RIMMANDRAKE_FIX_JAWABENCH_AWARENESS_INSTALL_CRASHES_START` (game start crashes on 2 of 4 launches); `RIMMANDRAKE_ISOLATE_GAME_FREEZES_SMALLEST_LIST_BEYOND_ONE_MOD`; lane `RIMMANDRAKE_HARDEN_BRIDGE_COMPANION_TOOLS_WITHOUT_THE_GAME` (doing). | RARE. A launch crash is a run that never started, which the tick voids [guess ~80%]. A false bridge FAIL is possible [guess ~20%, from the 4:06 PM list]. | as named |
| 8 | Stage-6 exit reader (`read_ingame_exit`) | not by me [from the GSS lists: the earlier-FAIL row and the split-run hold were fixed, aea6ee2885] | none open. Every check must PASS on its last row; an UNMEASURED row fails the visit. That is the bar, not a ticket. | clean [from the GSS lists] | none |
| 9 | Books: void, run spend, ceiling | state read only | `RIMMANDRAKE_CLOSE_VOID_GAPS_REVIEW_FOUND_SIX_MORE` and `RIMMANDRAKE_FIX_MATURATION_REVIEW_FINDINGS_SIX_PREDATE_SCOPE` are closed [measured]. `RIMMANDRAKE_KEEP_STAGE_CEILING_IN_TOKENS_NOT_LIST_DOLLARS` is open (units only). | NOT ON PATH | as named |
| 10 | Road back from Stage 6, owed actions | state read only | `RIMMANDRAKE_RETRY_OWED_ACTIONS_JUDGE_UNLAUNCHED_QUESTION_STUCK`: an owed launch can stay stuck | RARE (a FAIL that goes back and then stalls; the Conductor sees it on `maturation.py next`) | as named |
| 11 | Mod ledger, stage record | state read only | `RIMMANDRAKE_CUTOVER_PILOT_MODS_TO_LEDGER_SAME_DAY` (doing): FlowWorks' stage.json is still hand-written | RARE [from the census] | as named |
| 12 | Blind-challenge machinery (not on this move) | state read only | `RIMMANDRAKE_OPEN_NEXT_BLIND_CYCLE_WHEN_PROBLEMS_CLOSED_INSIDE`, `RIMMANDRAKE_REDECIDE_REPEAT_FINDINGS_JUDGE_COUNTED_AGAIN_TWICE`; Stage-3 items `RIMMANDRAKE_AUTOBUILD_FLOWWORKS_SEVEN_BARS_LEFT` (its own note says DONE, 0 of 61 bars not runnable; still `proposed`) and `RIMMANDRAKE_GREEN_FLOWWORKS_T_FETCH_FALLEN_OFFLINE_RED_DECIDER` | NOT ON PATH | as named |
| 13 | Owner-look and judges after Stage 6 (pre_human) | no | the next step, not this one | NOT ON PATH | none |

## The game-side tickets the visit carries (mod work, not pipeline)

Each needs game-up and is filed `caused_by RIMMANDRAKE_CLEAR_FLOWWORKS_PAPERWORK_TO_GAME_ONLY_ROAD`, so the `game_only`
clause names them all and no offline sibling stays open [measured: the clause passes].

| Ticket | Source event | Scene that decides it |
|---|---|---|
| `RIMMANDRAKE_PROVE_FLOWWORKS_SHEET_DROWNS_CROPS_LIVE` | cycle 4 lane 1 `SHEET_GAME_SIDE_NOT_KERNEL` | `sheet_overflow_proof.py` row `CROPS_IRRIGATE_THEN_DROWN` with the overspill switched on, plus per-fluid soak/drying rows |
| `RIMMANDRAKE_PROVE_FLOWWORKS_BOTTLE_JOBS_MOVE_EXACT_LITRES` | cycle 4 lane 1 `THIRST_GAME_SIDE_NOT_KERNEL` | `thirst_live.py`, a fill/empty litre-delta row next to T4/T11/T23 |
| `RIMMANDRAKE_PROVE_FLOWWORKS_DRILL_SURVEY_ROLLS_PER_BIOME_LIVE` | cycle 4 lane 1 `DRILL_RIGHT_MAPS_NOT_KERNEL` | a new survey read on two quicktest maps of different biomes, no yield set (no worldgen: existing tiles) |
| `RIMMANDRAKE_RETEST_FLOWWORKS_TOSS_FLAME_SINCE_JOBDEF_BUILT` | visit 1 `sc_toss_flame` FAIL (Unknown JobDef) | `concept_scenes.py --scene scene_toss_flame` |
| `RIMMANDRAKE_PASS_FLOWWORKS_COATING_WASH_SCENE_NEVER_PASSED` | visit 1 `sc_coating_wash` FAIL | `concept_scenes.py --scene scene_coating_wash` |

Other open mod tickets the visit will meet (they are not pipeline tickets and do not decide READY):
`FLOWWORKS_BOTTLE_FIX_JOBS_VANISH_EMPTY`, `SALT_BOTTLE_DIAGNOSE_DRUNK_FOR_NOTHING`, `THIRST_ROWS_DIAGNOSE_SLIME_SITS_STILL`,
`PITCAPTURE_DIAGNOSE_PRISONER_FLAG_BACKSLIDES` (visit 1's `sc_hole_prison` read PASS), and
`RIMMANDRAKE_TRACE_SLACK_MINIFIED_LOOKUP_ERROR_WITH_FLOWWORKS` (tier `gimmesomeslack_flowworks` only).

## Could not look (never clean)

- The code of rows 5, 7, 9, 10 and 11: I read ticket states and the earlier lists, not the code.
- The 4 in-game harnesses with no empty-game adapter (row 3).
- Whether visit 1 stopped at its spend cap. The summary lists its 31 tests done, and I found no cap line [guess ~75%
  that the cap fits 32].

## What is left before the visit runs (no ticket)

1. The Conductor runs the advance (the command is in the item's close note).
2. The launch waits clear by themselves: the GimmeSomeSlack visit ends (live 86 min at 8:26 PM [measured]), and this
   helper ends.
3. With the game down, deploy FlowWorks (`python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod FlowWorks --apply`)
   and bring the companion to FRESH.
4. Rerun `certificate FlowWorks --run --resume` only if a decider's inputs change first.
