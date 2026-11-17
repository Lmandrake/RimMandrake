# RIMMANDRAKE_LIFT_PROOF_VERDICTS_INTO_TESTED_CODE_NINE_SLIPPED

ExplosiveKnockback 0.1.0, bar `inv_proof_scenes` (proves at Stages 4-5), blind cycle 5 Problem NOTED_FOR_CONDUCTOR
(judge-1794890427). Replaces RIMMANDRAKE_PIN_KNOCKBACK_PROOF_VERDICTS_NINE_MUTANTS_UNSEEN (filed under the judge's own
item, so the Dispatch road back could not see it); the mod-ledger finding keeps that old id as its subject: claim it fixed
under that subject.

## spec

Nine planted faults in the proof scenes' verdict and planning code survived every offline suite and blind lane 1
(design/concepts/ExplosiveKnockback/version/blind_challenge/cycle_5/lane2/planted_results.jsonl, caught false each,
~35-40 s per fault): PF_P_CALIBRATION_ANY_CELLS, PF_SB_PLAN_IGNORES_MASS_LIMIT, PF_SB_PLAN_PLAIN_KERNEL,
PF_GO_CONTROL_NEVER_FAILS, PF_GO_DOOR_LANE_NO_REBOUND, PF_S3_HOSE_CONTROL_ALWAYS_PASSES, PF_S3_HOSE_THREE_DROPPED,
PF_PP_INVALID_NEVER, PF_PP_INVALID_TEXT (mutation texts: `lane2/planted_faults.json`). The verdicts are Verse code in
`RM_KnockbackProof*.cs`, which no offline test executes, so a verdict loosened to always pass reads green offline.

Route chosen by the steward (delegated, evidence-for-ask): the judge's code-side would_pass, not its re-pin. The re-pin
would change what decides `inv_proof_scenes` (verdict honesty moved to Stage 6), which the re-pin rule reserves to the
owner's card; the code route keeps every bar as written.

Fix: lift each of these scenes' verdict and plan arithmetic (calibration three cells, storeroom plan with the mass limit
and the kernel's real throw, goods-obstacle control and door lane, hose control and three-cells row, pit probe INVALID
and its text) into Verse-free static functions (beside `RM_KnockbackMath` or a new `RM_KnockbackVerdicts.cs` compiled
by `Source/SelfTest`), have the Verse scenes call them with the values they read, and add offline cases that pin each
verdict's pass, fail and INVALID edges. Verdict behaviour in game must not change. Rebuild release and proof DLLs with
their `.srchash`.

## refs
file: src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs
file: src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof_StoreroomBombPit.cs
file: src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof_GoodsObstacles.cs
file: src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof_StageThree.cs
file: src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof_PitProbe.cs
file: src/RimMandrake/ExplosiveKnockback/Source/SelfTest/Program.cs

## criteria

Acceptance test: re-point the nine entries of a copy of `lane2/planted_faults.json` at the same semantic mutation in the
moved code (same meaning, new `old`/`new` text; a fault whose meaning cannot be re-planted is named with why), then
`WINBUILD_ROOT=/mnt/d/ClaudeWork/rimmandrake/scratch/<own dir>/ python3
design/concepts/ExplosiveKnockback/version/blind_challenge/cycle_5/lane2/plant_faults.py --baseline` and `--ids <the
nine>` record caught true for each, and `--finish` shows the tree clean. Red side already watched: caught false for all
nine at a898e049d4 (planted_results.jsonl). Every offline decider of inv_proof_scenes (T_SCRIPT, T_PROOFGATE, T_RESTORE)
and T_KERNEL stay green. No `## launch-checks`: the planted run takes ~6 minutes (over the 120 s launch budget) and its
mutation texts must move with the code, so no fast must-fail exists.

## verify

Rerun the nine planted faults (each caught) and the offline suites above; record the reruns for the next blind judge.
