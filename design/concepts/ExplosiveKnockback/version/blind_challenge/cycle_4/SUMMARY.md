# ExplosiveKnockback 0.1.0 — blind challenge cycle 4

## Start time
2026-11-15 22:14 UTC (written before any input was opened)

## Changed files to bars
`git diff --name-only 05aded8b89 origin/main -- <the brief's paths> | grep -v /blind_challenge/` gives the brief's 14 files (no locked file changed: tree, sheet, scenes untouched).

| changed file | bars whose inputs it touches |
|---|---|
| `Source/RM_KnockbackMath.cs` (+15: FireSwitchedOff, IsFireDamage) | inv_kernel; every_harmful_blast_throws, settings_scale_and_switch (fire at half off) |
| `Source/RM_Patch_DamageWorker_ExplosionKnockback.cs` (caller now uses the two kernel functions) | inv_hook, inv_which_blasts, every_harmful_blast_throws, settings_scale_and_switch |
| `Source/RM_KnockbackProof.cs`, `Source/RM_KnockbackProof_GoodsObstacles.cs` | inv_proof_scenes; goods_arc_spin_rebound, doors_and_deep_water_stop (sc_goods_obstacles) |
| `Assemblies/*.dll` + `.srchash` | the build of the above: every stage-6 bar; no offline bar decides on it |
| `Source/SelfTest/Program.cs` (T_KERNEL) | inv_kernel |
| `selftest_explosiveknockback_proofgate.py` (T_PROOFGATE), `Utils/selftest_proof_restore_check.py` (T_RESTORE) | inv_proof_scenes |
| `selftest_explosiveknockback_goods_obstacles.py`, `validation.py` | inv_proof_scenes (scene runner); goods_arc_spin_rebound, doors_and_deep_water_stop |
| `journal.md`, `version/run_spend.jsonl`, `version/stage_record.json` | records only, no bar input |

Lane-1 scope: inv_kernel and inv_proof_scenes in full ("all once"), with the changed fire switch, plus the stage-6 bars whose logic plainly lives in `RM_KnockbackMath.cs`.

## Lane 1
Committed blind, before any test, journal, test table or earlier finding was opened. Runner: `python3 design/concepts/ExplosiveKnockback/version/blind_challenge/cycle_4/lane1/run_lane1.py` (C# `BlindLane1.cs` against the shipped `RM_KnockbackMath.cs`, settings read from `RM_KnockbackMod.cs`; `blind_lane1_proof.py` for the gate, scene list and settings defaults).

60 rows [measured]: 22 PASS, 1 FAIL, 6 INFO, 31 UNSETTLED (all `not_kernel`, each naming one stage-6 game-side bar; none names an offline bar).

- **FAIL `L1_PATH_RANDOM_CONSERVATION`** (42 of 30000 random grids, seed 20261115, one kind): a pawn whose throw crosses a sandbag cell straight into another pawn backs off the sandbag to the cell it started on (travelled 0) yet the result reports `stop Pawn, hitOther` with both impacts on a pawn two cells away. Shrunk: lane `start 4 | sandbag 5 | pawn 6`, 5 cells east. Same shape with a wall behind the sandbag: impact without contact.
- INFO rows to weigh in lane 2: an unpatched modded burn type ignores the fire switch (`L1_FIRE_SWITCH_UNPATCHED_TYPE`); 14 of 290 rim distances give kernel 0 but wild 1 (`L1_WILD_RIM_ZERO_KERNEL`, versus inv_too_weak_skip); a flying corpse never knocks (`L1_HEAVY_KNOCK_CORPSE`).

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
(pending)

## Owed
(pending)
