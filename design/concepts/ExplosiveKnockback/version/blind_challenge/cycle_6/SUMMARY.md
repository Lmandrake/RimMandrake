# ExplosiveKnockback 0.1.0, blind challenge cycle 6 (run judge-1795437145)

## Start time
2026-11-23T12:33:44Z (UTC), before any input was opened.

## Changed files to bars
`git diff --name-only 040f55f95e origin/main` (paths of the brief, less `/blind_challenge/`): 78 files [measured].
| changed file(s) | bars whose inputs they touch |
|---|---|
| `Source/RM_KnockbackMath.cs` (covered pit is a pit for the path, `PitCell`, a pawn landing breaks a cover) | inv_kernel, thrown_into_pit_falls, blast_breaks_pit_cover, pawn_hits_pawn_stops, inv_pits_receive |
| `Source/RM_KnockbackPlan.cs` (new: the whole throw decision, Verse-free) | the_spared, every_good_moves, goods_arc_spin_rebound, closed_container_holds, open_shelf_scatters, gas_goes_clump_by_clump, shield_belt_holds, recovery_immunity, heavier_flies_less, thrown_into_pit_falls, no_teleport, inv_who_is_spared, inv_too_weak_skip, inv_mass_limit_skip, inv_container_shove, inv_closed_guard, inv_shelf_skip, inv_goods_fly, inv_items_teleport, inv_kernel |
| `Source/RM_MapComponent_Knockback.cs`, `RM_ThingFlyer_Knockback.cs`, `RM_PawnFlyerPatches.cs`, `RM_KnockbackCompat.cs` (callers) | inv_hook, inv_pawn_flyer, inv_goods_fly, inv_closed_guard, pawn_flight_arc, no_teleport, heavy_stack_knocks, thrown_into_pit_falls, blast_breaks_pit_cover, pit_goods_fetched, closed_container_holds |
| `Source/RM_KnockbackMod.cs` | settings_scale_and_switch, inv_settings |
| `Source/RM_KnockbackProof*.cs`, `RM_KnockbackScenes.cs`, `RM_KnockbackVerdicts.cs`, `validation.py`, `proof/*.py`, `selftest_explosiveknockback_{script,proofgate,map,stage3_scenes,storeroom_bomb_pit,goods_obstacles,gas_clumps,journal_jolt,barrage_p99,settings_sweep}.py`, `Utils/selftest_proof_restore_check.py`, `Utils/selftest_settings_screens.py` | inv_proof_scenes (and the scene bars each proves) |
| `selftest_explosiveknockback_kernel.py`, `Utils/selftest_explosiveknockback_fuzz.py`, `Source/SelfTest/*` | inv_kernel (deciders T_KERNEL, T_FUZZ) |
| `Assemblies/*.dll`, `.srchash`, `.csproj` | every game-side bar (the build) |
| `version/test_table.*`, `stage_record.json`, `journal.md`, ledger, `rescue_2026-11-17/`, `polish.md`, `run_spend.jsonl`, `in_game/unrun.jsonl`, `next_version/`, `ticket_sweep` | records, no bar input. No locked file changed (`tree.json`, `sheet.md`, `scenes.json` absent from the diff) [measured]. |

Lane-1 scope: inv_kernel and inv_proof_scenes (the offline bars), then every bar the two Verse-free kernels decide (Math.cs and the new Plan.cs, which holds the whole throw decision).

## Lane 1
`lane1/BlindLane1.cs` + `lane1/run_lane1.py` (C# against the shipped `RM_KnockbackMath.cs` and `RM_KnockbackPlan.cs`; Python against the shipped settings and `proof_build_gate.py`). Written from the bars, settings and def patch only, before anything sealed was opened.
Result: 34 rows: 28 PASS, 2 FAIL, 4 UNSETTLED [measured] (`lane1/lane1_rows.jsonl`).
- FAIL `L1_EVERY_REACHED_GOOD_MOVES` (every_good_moves): seed 7741, 400 walled rooms: 593 of 12474 reached goods (kernel >= 1 cell) sit still; 435 are a one-cell throw with a wall or door right behind it (the wall-first bounce keeps floor(0.7 x 1) = 0 cells), 148 a bounce whose reflected line is blocked, 10 sandbags with no hop.
- FAIL `L1_SHELF_STOREROOM_EVERY_GOOD_MOVES` (every_good_moves, open_shelf_scatters): seed 2611, 300 storerooms with open shelf rows: 764 of 10699 reached goods sit still (312 one-cell against a wall/door, 255 bounce blocked, 197 shelf/sandbag no hop).
- UNSETTLED `L1_GAS_SHOVE_PAWN_ON_INTACT_COVER`: a person on an intact cover is skipped `in_pit` by a gas clump; settled by the caller's `onSuperdeep` and whether standing on a cover is "in a pit".
- UNSETTLED `L1_SHIELD_DOES_NOT_STOP_GAS_SHOVE`: the plan absorbs a gas shove when `shieldAbsorbed`; settled by the caller (lane 2).
- UNSETTLED `L1_FIRE_SWITCH_ON_UNPATCHED_FIRE_TYPE`: another mod's fire type with no extension throws full and ignores the fire switch; settled by the caller and the bar's two clauses.
- UNSETTLED `L1_NOT_KERNEL_GAME_SIDE` (not_kernel): flyers, hooks, pit hauling, pathing, gas census, the raid walk: Stage 6.

## Lane 2 reruns
`lane2/rerun_offline.py`, every kind=offline test of `version/test_table.json` (28) with its recorded command [measured]:
- Deciders of the offline bars: T_KERNEL, T_FUZZ, T_SCRIPT, T_PROOFGATE PASS = recorded. T_RESTORE **FAIL** (recorded PASS): `selftest_proof_restore_check` reads the whole repo and four FlowWorks proof-restore leaks of 2026-11-22 were outside its filed baseline. Class: check wrong (no ExplosiveKnockback hit). Repaired at `44bf0e6b6f` (BASELINE keys under the filed item RIMMANDRAKE_RESTORE_FLOWWORKS_PIT_PROOF_SETTINGS_FOUR_NEW_LEAKS, its acceptance test in the title); shown red on a planted EK leak (`lane2/plant_ek_restore_leak.patch`, rc 1, names RM_KnockbackProof.cs) and green on the tree (rc 0): `lane2/reruns_after_fix.jsonl`.
- The other 23 offline tests: 23 of 23 PASS = recorded.
- 27 of 28 match on first rerun; 28 of 28 PASS after the check repair [measured].
- Verified the two claimed fixes of cycle 5 (`judge-verify`): RIMMANDRAKE_STOP_KNOCKBACK_THROW_AT_PAWN_ON_PIT_COVER (`cycle_5/lane2/check_pit_pawn.py` rc 0, 6 of 6) and RIMMANDRAKE_STOP_THROWS_OVER_COVERED_PITS_K08_SAYS_GROUND (`accept_covered_pit.py --rev 9a0e1710fb` rc 0, 6 of 6); both `finding.verified` in the mod ledger.

## Planted
The judge (judge-1795437145) was killed before it wrote this section. The steward run (run-1795441975) read `lane2/planted_results.jsonl` [measured]: 33 planted faults, 21 caught, 12 not caught, tree clean after.
- 8 not caught are game-side Verse callers on Stage-6 bars (PF_CALLER_SHIELD_NEVER, PF_CALLER_PIT_NEVER_READ, PF_CALLER_PAWN_ON_COVER_IGNORED, PF_CALLER_FIRE_SWITCH_IGNORED, PF_CALLER_PAWN_LANDING_KEEPS_COVER, PF_CALLER_PAWN_LANDING_NOT_STANDABLE, PF_CALLER_GOODS_LANDING_KEEPS_COVER, PF_CALLER_HEAVY_KNOCK_OFF). This is the class of the open finding RIMMANDRAKE_NOTE_KNOCKBACK_CALLER_MUTANTS_OWED_TO_STAGE_SIX. No offline test runs Verse code.
- 4 not caught are in proof code and proof scripts (PF_PROOF_RESET_NOOP, PF_PROOF_WALL_SCENE_DROPPED, PF_MAPAGREE_ALWAYS_OK, PF_SAVELOAD_ALWAYS_OK). This is the class of the open finding RIMMANDRAKE_PIN_KNOCKBACK_PROOF_VERDICTS_NINE_MUTANTS_UNSEEN (open since cycle 3; cycles 4 and 5 judged inv_proof_scenes green with the same class surviving). No new item: one source event, one item.

## Faults
`lane2/faults.json` [measured counts]: 2 Problems, 2 Polish; 0 `miss_of: 5`.
- Problem, against mod: RIMMANDRAKE_MOVE_KNOCKBACK_GOODS_PINNED_AGAINST_WALLS_SHELVES (every_good_moves). A reached good with a throw of a cell or more sat still when its line was blocked and no bounce or hop freed it: a one-cell throw into a wall (the bounce keeps floor(0.7 x 1) = 0 cells), a bounce whose reflected line is blocked at a corner, a throw along a shelf row deeper than 2 cells. Lane 1: 593 of 12,474 goods in walled rooms, 764 of 10,699 in open-shelf storerooms. The shipped situation map hid it: its M04 exempted such goods as "pinned", which the bar does not spare (on the parent with M04 narrowed: 7,334 of 243,452 readings break). The material (RM_KnockbackPlan.cs) is new since cycle 5, so not a miss.
- Problem, against check: RIMMANDRAKE_SCOPE_KNOCKBACK_RESTORE_DECIDER_RED_ON_FLOWWORKS (inv_proof_scenes, decider T_RESTORE), above.
- Polish (in `version/polish.md`): RIMMANDRAKE_NOTE_KNOCKBACK_FIRE_SWITCH_MISSES_UNPATCHED_FIRE, RIMMANDRAKE_NOTE_KNOCKBACK_GAS_SKIPS_PAWN_ON_INTACT_COVER. Neither failed; no concrete case; test 1 fails.

## Fixes
`lane2/fixes.jsonl`:
- `fa2de6ee4b` (mod, unit judge-1795437145): `RM_KnockbackPlan.cs` GoodsWithNoFirstCell ends with `Tumble()`: when throw, hop and bounce leave a good in place (deep water excepted), it walks its throw (up to +HopExtraCells) along the eight directions, most in line with the throw first, and takes the first that moves; `RM_MapComponent_Knockback.cs` journals `tumbled`; DLL rebuilt with its `.srchash`. Red: lane 1 against the parent's plan (`44bf0e6b6f`) rc 1 (2 FAIL); the map under `plant_tumble_removed.patch` rc 1. Green at the fix: lane 1 rc 0 (30 PASS, 4 UNSETTLED; `lane2/lane1_rows_after_fix.jsonl`), map `--map-only` rc 0, full map selftest PASS with 31 of 31 planted faults seen. Owes one fresh reader (the steward run).
- `44bf0e6b6f` (check repair, no reader owed): T_RESTORE baseline, plant and both readings above.
- `maturation.py red-seen` recorded for T_SITUATION_MAP_OFFLINE and T_RESTORE.

## Steward's decisions enacted
None were written for this cycle; the standing default held (every bar judged as locked; no bar, wording, version or stage touched).

## Tests edited
`tests_edited.json`: `Source/SelfTest/KnockbackMap.cs` (M04's pinned exemption narrowed to the bar: stronger), `selftest_explosiveknockback_map.py` (one planted fault added), `Utils/proof_restore_check.py` (BASELINE keys for the filed FlowWorks item; still red on an EK leak). No assertion was weakened or removed.

## Unsettled
- `L1_SHIELD_DOES_NOT_STOP_GAS_SHOVE`: settled in lane 2: the caller passes `shield = null` for every gas burst (`RM_MapComponent_Knockback.cs` gas request), so `shieldAbsorbed` is never true for a shove; the map's M18 reads it too.
- `L1_GAS_SHOVE_PAWN_ON_INTACT_COVER`, `L1_FIRE_SWITCH_ON_UNPATCHED_FIRE_TYPE`: Polish, above; no bar decided on them.
- `L1_NOT_KERNEL_GAME_SIDE`: flyers, hooks, pit hauling, pathing, gas census, the raid walk: Stage 6, every bar it names proves at 6.
- Code review status of the changed files reads UNREADABLE (mod bars mostly UNRUN live, Stage 6 state) and NO PAGE for `proof_restore_check.py` [measured].

## Exit
The judge wrote this block at `dbdd5f88d6`, with lane 1 only, before lane 2 and before its fixes. It was then killed. The steward run (run-1795441975) set offline_bars from its own reruns at `e0e997836e`, after the mod fix `fa2de6ee4b` (`lane2/reruns_after_fix.jsonl`, rows `by` run-1795441975): T_KERNEL, T_FUZZ, T_SCRIPT, T_PROOFGATE and T_RESTORE are rc 0. exit_met stays the judge's false. The reader reads that false as the owed fresh reader of the mod fix, and `lane2/fix_reviews.jsonl` holds that reader's review.
offline_bars: {inv_kernel: green, inv_proof_scenes: green}
problems_open: 0
exit_met: false

## Owed
- Steward run run-1795441975 is the one fresh reader of `fa2de6ee4b`. Its verdict is sound (`lane2/fix_reviews.jsonl`).
- `L1_SHIELD_DOES_NOT_STOP_GAS_SHOVE` is settled by a planted run of T_GAS_CLUMP_ORDER. The planted run uses `lane2/plant_gas_burst_reads_belt.patch`, a gas request that reads the belt. It gives rc 1, and the check gives rc 0 at `e0e997836e` (`lane2/lane1_rows_after_fix.jsonl`, `settled_by`).
- Stage 6 owes the game-side bars named by `L1_NOT_KERNEL_GAME_SIDE` and the 8 caller faults that no offline test caught.
