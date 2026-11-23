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
(pending)

## Planted
(pending)

## Faults
(pending)

## Fixes
(pending)

## Steward's decisions enacted
(pending)

## Tests edited
(pending)

## Unsettled
(pending)

## Exit
offline_bars: {inv_kernel: red, inv_proof_scenes: red}
problems_open: 0
exit_met: false

## Owed
(pending: run in progress)
