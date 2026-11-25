# ExplosiveKnockback 0.2.0 — blind challenge, cycle 1

## Start time
2026-11-25T12:54:57Z (2026-11-25 4:54 AM PST)

## Lane 1
Written blind from the bars (tree.json, sheet.md, plan.md, record.json bar rows, VERSION.json, bars.md), the shipped
settings (RM_KnockbackMod.cs, read by regex) and the patches. `lane1/BlindLane1.cs` compiles against the shipped kernel
`RM_KnockbackMath.cs`; `lane1/run_lane1.py [--kernel <file>]` also runs Python rows on the inv_proof_scenes kernels
(proof_build_gate.py by behaviour, the settings' initializer/Scribe/Reset defaults, the scene dispatch, the release DLL,
and the proof build compiled under a private WINBUILD_ROOT).

- 100 rows [measured]: 28 PASS, 0 FAIL, 1 INFO, 71 UNSETTLED. Every UNSETTLED row is one `not_kernel` row per
  game-side bar (all 71 bars other than the two offline ones prove in game); none names an offline bar.
- inv_kernel: 23 rows (fixed, random with seeds 20261125, 7, 11, 3, 5, 9, 13, 17, and sweeps through every shipped
  slider range, every kernel switch off) PASS. inv_proof_scenes: 5 rows PASS.
- Two of my own oracles were wrong on the first run and were corrected before this record (a throw backed off a
  sandbag ends `Distance` short of its cells; the all-off lane never reached its pit). No kernel change.
- Committed before anything closed to lane 1 was opened.

## Lane 2 reruns
`lane2/rerun_offline.py` (generic over test_table.json; a private WINBUILD_ROOT, created first) reran all 36 offline tests
with their recorded commands into `lane2/reruns.jsonl` [measured]: 36 PASS, 36 of 36 match the recorded verdict. Every
decider of the two offline bars PASS: T_KERNEL (277/277), T_FUZZ (42001 cases), T_SCRIPT, T_PROOFGATE, T_RESTORE.
T_SITUATION_MAP_OFFLINE (315 s) ran alone under waitalive. One apparatus fault of mine, repaired before the record:
the first T_KERNEL run read UNMEASURED because my private build root did not exist yet; the tool now creates it.
After the fix, `rerun_relation.py --old 39be8e7f43` named only T_PROOFGATE: `lane2/reruns_after_fix.jsonl` PASS
(`PASS proofgate (R1 P1 D1 G1)`); every other decider keeps its `reruns.jsonl` row.

## Planted
`lane2/planted_faults.json`: 35 faults [measured] — 16 in the kernel RM_KnockbackMath.cs, 10 in the inv_proof_scenes
kernels (proof_build_gate.py 2, RM_KnockbackMod.cs 5, RM_KnockbackProof.cs 3), 9 in game-side callers and the patch
(RM_KnockbackPlan.cs 4, RM_MapComponent_Knockback.cs, RM_PawnFlyerPatches.cs, RM_ThingFlyer_Knockback.cs,
RM_Patch_DamageWorker_ExplosionKnockback.cs, Patches/RM_Knockback_DamageDefs.xml). `lane2/plant_faults.py` ran the five
offline-bar deciders, 12 offline supports (the situation map too for planner and flyer faults) and lane 1 on each, restored
on signal, and ended `tree_clean_after: true`. Baseline all green.
- Caught 31 of 35 [measured]: all 16 kernel faults (by T_KERNEL or T_FUZZ, and by lane 1); 9 of 10 proof-scene faults;
  6 of 9 caller faults (T_KERNEL, the situation map, T_CARRY_STATIC, T_SETTINGS_SWEEP_OFFLINE, T_LINT).
- `P_SCENE_CASE_RENAMED` was caught only by lane 1: no inv_proof_scenes decider saw it (the Problem below, fixed).
- Missed: `P_RULES_REBOUND_KEEP_FIXED` and `C_FLYER_REBOUND_FROM_WHOLE_THROW` (Polish below; live Stage 6 deciders
  own them); `C_LANDING_BRUISE_SWAPPED` (Verse landing code; the live sc_pawn_arc_bruise_sizes reads the damage
  taken, so it is that scene's to catch); `C_CONTAINER_INTO_PITS` is an equivalent mutant (ContainerCellFree already
  refuses a superdeep cell, so the rest cell is the same).

## Faults
`lane2/faults.json`: 1 Problem, 3 Polish [measured].
- Problem, against check: RIMMANDRAKE_CHECK_KNOCKBACK_SCENE_DISPATCH_NO_DECIDER_LOOKED (inv_proof_scenes). A named
  proof scene with no Build case stages "unknown scene", and no decider read the dispatch. FIXED 08b632f259.
- Polish (one line each on version/polish.md, no ticket): RIMMANDRAKE_CHECK_KNOCKBACK_RULES_MAPPING_OFFLINE_LIKE_KERNEL,
  RIMMANDRAKE_CROSSCHECK_KNOCKBACK_REBOUND_LEFT_FLYER_GRADES_ITSELF, RIMMANDRAKE_SAVE_KNOCKBACK_LANDING_IMPACT_FACTOR_ACROSS_RELOAD.
- No mod Problem: every caller of the kernel I read (KbPlanner, Execute, ThrowPawn, ThrowCarried, the landing bruise,
  the goods flyer, the explosion hook) holds its bar on the real build.

## Fixes
`lane2/fixes.jsonl`: one check repair, test file only. Plant P_SCENE_CASE_RENAMED (`lane2/plants/P_SCENE_CASE_RENAMED.patch`):
red rc 1 (`FAIL D1 no Build case for wall_stop`), green rc 0 on the real build, both at 08b632f259. `maturation.py
red-seen ExplosiveKnockback T_PROOFGATE` recorded (version/evidence/red_seen.json). A check repair owes no reader.
`lane2/lane1_rows_after_fix.jsonl`: 28 PASS, 0 FAIL.

## Steward's decisions enacted
Three, recorded with --per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM (OWNER.jsonl, 5bb0c50825): the 1.6 goods factor
is a constant (no fault raised for a missing slider); closed containers are "thrown a short way" (at least one cell,
never past the cap); sc_settings_sweep names every saved setting (so the Rules() gap offline is Polish, the live sweep
owns it). The others are history of 0.1.0 and changed nothing here.

## Tests edited
`tests_edited.json`: `src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_proofgate.py` (T_PROOFGATE), check D1
added; nothing removed or weakened.

## Unsettled
71 not_kernel rows, one per game-side bar, all proving at Stage 6 or the walk; none names an offline bar. Their kernel
halves are in the lane-1 rows they cite.

## Exit
offline_bars: {inv_kernel: green, inv_proof_scenes: green}
problems_open: 0
exit_met: true

## Owed
Nothing for this cycle. The 71 game-side bars are Stage 6's. Three Polish lines are on version/polish.md.
