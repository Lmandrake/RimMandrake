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
`lane2/rerun_offline.py` reran all 16 offline tests of `version/test_table.json` (`lane2/reruns.jsonl`): **16 of 16 PASS, 15 same result, 13 exact match** [measured].
- Every decider of the two offline bars passes: T_KERNEL (180/180), T_FUZZ, T_SCRIPT, T_PROOFGATE, T_RESTORE.
- The 3 non-matches are improvements since the table was made (2026-11-15 08:55): T_KERNEL and T_HEAVY_KNOCK_RULE now count 180 checks, not 174 (cycle 3 added K-23); T_RESTORE, recorded KNOWN RED RIMMANDRAKE_RESTORE_ON_THROW_IN_KNOCKBACK_PROOF_TWO_LEAKS, now passes (`selftest_proof_restore_check: PASS (0 failure(s))`). That item is closed (`587529cee1`), so the table's `known_red` is stale.
- T_SETTINGS_SCREEN (red/unrun-as-recorded list) reran PASS, 856/856.

## Planted
`lane2/plant_faults.py` (restores on SIGTERM/SIGINT/SIGHUP, `WINBUILD_ROOT=/mnt/d/ClaudeWork/rimmandrake/scratch/explosiveknockback_blind_c4_mut/`), 6 batches, each ending `tree_clean_after: true`, `git diff --quiet` on the mod. **50 planted, 41 caught by a builder suite, 9 missed** [measured]. Caught means a suite green at baseline that goes red, or a new lane-1 FAIL row.
- Kernel `RM_KnockbackMath.cs` (inv_kernel): 17 of 17 caught (T_KERNEL, T_FUZZ, S_BLIND_CYCLE1, lane 1), including the changed fire switch's three faults.
- inv_proof_scenes' kernels: `RM_KnockbackMod.cs` 4 of 4; `proof_build_gate.py` 2 of 3; `RM_KnockbackProof.cs` 6 of 6 (Verdict/Stage restore dropped, pokes before restores, a scene name dropped).
- Changed test files (oracle flips, two each in `SelfTest/Program.cs`, the goods-obstacles, proofgate and restore selftests): 8 of 8 went red.
- Missed (9), and why none is a Problem against an offline decider:
  - `PF_GATE_WRONG_TYPE_NAME`: changes only the refusal message's type name; `is_release_answer` matches the literal, so this is an equivalent mutant.
  - `PF_GO_DOOR_BOUNCE_ANY_CELLS`, `PF_GO_SANDBAG_LANE_SHORT`: weaken a live scene's own verdict. No offline test can see that, the same class as cycle 3's open Polish RIMMANDRAKE_GUARD_PROOF_VERDICTS_FIVE_WEAKENED_STAYED_GREEN (evidence for it, not a new item).
  - `PF_HOOK_FIRE_SWITCH_DROPPED`, `PF_HOOK_FIRE_HEDIFF_NOT_PASSED`, `PF_HOOK_POWER_NOT_APPLIED`, `PF_HOOK_REF_DAMAGE_EXT_IGNORED`, `PF_MC_OTHER_PAWN_UNHURT`, `PF_MC_DOOR_SETTING_IGNORED`: game-side callers whose bars prove at Stage 6 (every_harmful_blast_throws by sc_blast_kinds, settings_scale_and_switch by sc_settings_sweep, which `selftest_explosiveknockback_settings_sweep.py` names for fireAtHalf and doorsTakeDamage, heavier_flies_less by sc_mass_and_power, doors_and_deep_water_stop by sc_door_water, pawn_hits_pawn_stops by sc_pawn_hits_pawn). Their offline decider T_KERNEL covers only the kernel half. Owed to Stage 6: those scenes must catch these.
- Record files `journal.md`, `run_spend.jsonl` and `stage_record.json`, and the binary DLL with its `.srchash`, carry no behaviour any test reads, so no fault was planted in them.

## Faults
`lane2/faults.json`: **0 Problems, 1 Polish** [measured]. The Polish is `miss_of: 3`.
- Polish `RIMMANDRAKE_STOP_KNOCKBACK_HIT_ACROSS_SANDBAG_NO_CONTACT` (filed, proposed; acceptance test in its note). Lane-1 row `L1_PATH_RANDOM_CONSERVATION`: a pawn thrown over a sandbag straight into a pawn, wall or door backs off the sandbag, often to its own start. It still reports the hit, and `ThrowPawn` hurts it, a pawn two cells away and a door two cells away, though it never moves. No bar's words break (it stops before the pawn and takes a hit; nothing rests on a sandbag). `Resolve` is unchanged since cycle 3, hence `miss_of: 3`.
- Lane-1 INFO rows checked against the callers, no fault in any:
  - `L1_WILD_RIM_ZERO_KERNEL`: `RM_MapComponent_Knockback.cs` skips a rim good too_weak by the kernel's cells, as inv_too_weak_skip says.
  - `L1_FIRE_SWITCH_UNPATCHED_TYPE`: an untuned modded burn type throws at the other-mods percent, as every_harmful_blast_throws words it.
  - `L1_HEAVY_KNOCK_CORPSE`: the leaf speaks of stacks.

## Fixes
- **Mod:** none. No Problem was found, so no mod code was changed and `lane2/fixes.jsonl` is empty.
- **Pipeline** (the pipeline fixes its own defects): RIMMANDRAKE_CLEAR_POLISH_LANE1_FAIL_WITHOUT_ANY_FIX, fixed and closed at `52c3efecf8`.
  - The defect: `maturation.py next` refused a lane-1 FAIL owned by a Polish fault whenever the cycle made no fixes, because it demanded `lane2/lane1_rows_after_fix.jsonl`. That contradicts its own docstring and the brief.
  - Tests first: a new met case in `selftest_maturation.py --blind` went red on the base (rc 1, `lane2/pipeline_fix/red_selftest_maturation_blind.txt`) and green after the fix (rc 0, 68/68, `lane2/pipeline_fix/green_selftest_maturation_blind.txt`).
  - Scope: a FAIL that no Polish fault names still reads not met.

## Steward's decisions enacted
None written for this cycle. The standing default held: every bar was judged as locked, no bar or criterion was edited, nothing was NOTED_FOR_CONDUCTOR.

## Tests edited
None (`tests_edited.json` is `[]`).

## Unsettled
- 31 lane-1 `not_kernel` rows, each naming one Stage-6 game-side bar (flight carrier, hose, gas chain and census, pit cover and fetching, Harmony scope, storage classification, the walk; listed in `lane1/blind_lane1_proof.py` GAME_SIDE). None names an offline bar.
- The six game-side caller faults planted and missed above: owed to Stage 6's scenes.

## Exit
offline_bars: {inv_kernel: green, inv_proof_scenes: green}
problems_open: 0
exit_met: true

## Owed
- Stage 6: the live scenes named under Planted must catch the six missed caller faults (fire switch and hediff, blast power and reference damage, the other pawn's impact, the door-damage setting).
- The steward: `version/test_table.json` still lists T_RESTORE as known red although its item is closed, and records T_KERNEL at 174 checks, not 180. Regenerate it at the next advance.
- Polish RIMMANDRAKE_STOP_KNOCKBACK_HIT_ACROSS_SANDBAG_NO_CONTACT, for the Polish list (not part of passing).
