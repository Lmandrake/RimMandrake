# Review tonight — code changed since 2026-10-22 18:30 (BENCH helper)

Scope: .cs/.py in git log since 18:30, DIRTY per code_review_status, no uncommitted edits. Transient/ scripts skipped (one-shot, untracked shelf). Uncommitted at start (skipped): RM_MapComponent_Hoses.cs, HoseSelfTest.cs, modern_port_fittings.py, selftest_tank_art_edges.py.

| file | lines | reachable | verdict | note |
|---|---|---|---|---|
| src/RimMandrake/FlowWorks/art_source/LadderPortable/gen_a3.py | 18 | ? | PENDING | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/gen_a5.py | 20 | ? | PENDING | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/gen_a4.py | 21 | ? | PENDING | |
| src/RimMandrake/DeepDrill/Source/Kernel/RM_DeepDrillKernel.cs | 24 | yes | CLEAN | |
| src/RimMandrake/Aftermath/Source/AftermathMod.cs | 25 | yes | CLEAN | |
| src/RimMandrake/DeepDrill/Source/Patch_DeepHome.cs | 27 | yes | CLEAN | |
| src/RimMandrake/DeepDrill/Source/RM_DeepHomeDef.cs | 32 | yes | CLEAN | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/gen_a6.py | 34 | ? | PENDING | |
| src/RimMandrake/Utils/selftest_deepdrill.py | 36 | yes | CLEAN | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/gen_a7.py | 37 | ? | PENDING | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/gen_a8.py | 43 | ? | PENDING | |
| src/RimMandrake/DeepDrill/Source/RM_DeepDrillMod.cs | 47 | yes | CLEAN | |
| src/RimMandrake/Utils/art/selftest_art_guard_latest_retire.py | 47 | ? | PENDING | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/gpt_reference.py | 52 | ? | PENDING | |
| src/RimMandrake/DeepDrill/validation.py | 64 | yes | CLEAN | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/gen_a2.py | 72 | ? | PENDING | |
| src/RimMandrake/Utils/mutate_graffiti_fuzz.py | 73 | yes | CLEAN | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/compose_a2.py | 80 | ? | PENDING | |
| src/RimMandrake/FlowWorks/northstar/selftest_pipe_levelling_perf_proof.py | 81 | ? | PENDING | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/mock.py | 86 | ? | PENDING | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/compose_a3.py | 90 | ? | PENDING | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/compose_a4.py | 90 | ? | PENDING | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/compose_a8.py | 90 | ? | PENDING | |
| src/RimMandrake/DeepDrill/Source/SelfTest/Program.cs | 91 | yes | CLEAN | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/compose_a5.py | 94 | ? | PENDING | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/compose_a6.py | 94 | ? | PENDING | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/compose_a7.py | 94 | ? | PENDING | |
| src/RimMandrake/FlowWorks/northstar/selftest_joint_check.py | 94 | yes | CLEAN | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/gen.py | 104 | ? | PENDING | |
| src/RimMandrake/FlowWorks/Source/SelfTest/PitCoverBeneathChecks.cs | 106 | yes | CLEAN | |
| src/RimMandrake/FlowWorks/Source/Hose/ReelIntakeGeometry.cs | 122 | yes | CLEAN | |
| src/RimMandrake/Utils/art/selftest_art_provenance.py | 145 | ? | PENDING | |
| src/RimMandrake/DivingInteraction/Source/RM_SeabedFloorLife.cs | 165 | yes | CLEAN | |
| src/RimMandrake/Aftermath/Source/MapComponent_BattleRecorder.cs | 172 | yes | CLEAN | |
| src/RimMandrake/FlowWorks/Source/SelfTest/HoseWallSeamChecks.cs | 192 | ? | PENDING | |
| src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitDepthDraw.cs | 192 | yes | CLEAN | |
| src/RimMandrake/FlowWorks/northstar/selftest_scenarios_map.py | 223 | yes | CLEAN | |
| src/RimMandrake/Utils/mockups/messy_conduit/reel_intake_geometry.py | 223 | ? | PENDING | |
| src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitLipOcclusion.cs | 262 | yes | CLEAN | |
| src/RimMandrake/FlowWorks/northstar/joint_check.py | 266 | yes | CLEAN | |
| src/RimMandrake/FlowWorks/selftest_review_map.py | 275 | yes | CLEAN | |
| src/RimMandrake/ExplosiveGrowth/Source/RM_ExplosiveGrowthPatches.cs | 314 | yes | CLEAN | |
| src/RimMandrake/FlowWorks/review_map_rivers.py | 333 | yes | CLEAN | |
| src/RimMandrake/Utils/pulse/selftest_pulse.py | 350 | ? | PENDING | |
| src/RimMandrake/FlowWorks/Source/Pits/Building_PitCover.cs | 354 | yes | CLEAN | |
| src/RimMandrake/FlowWorks/northstar/pipe_levelling_perf_proof.py | 361 | ? | PENDING | |
| src/RimMandrake/FlowWorks/Source/RM_PromotionProofs.cs | 362 | yes | CLEAN | |
| src/RimMandrake/Utils/art/selftest_art.py | 399 | yes | CLEAN | |
| src/RimMandrake/FlowWorks/Source/Hose/HoseProbe.cs | 438 | yes | OPEN | OPEN: WallCrossJson was inserted between RelayEnd's Round-7 <summary> and RelayEnd, so WallCrossJson carries two summaries and RelayEnd none; not fixed (FlowWorks DLL/srchash have a helper's uncommitted edits, no rebuild possible now) |
| src/RimMandrake/Utils/art/art_guard.py | 439 | ? | PENDING | |
| src/RimMandrake/Utils/art/chat_review.py | 446 | ? | PENDING | |
| src/RimMandrake/Utils/art/art.py | 454 | yes | CLEAN | |
| src/RimMandrake/FlowWorks/northstar/selftest_proof_hose.py | 476 | yes | SKIPPED | SKIPPED: another helper has uncommitted edits (zoo_start_checks); my one HW1 check committed f531265895 |
| src/RimMandrake/Utils/art/review_queue.py | 488 | ? | PENDING | |
| src/RimMandrake/ExplosiveGrowth/Source/RM_ExplosiveGrowthProof.cs | 492 | yes | CLEAN | |
| src/RimMandrake/DivingInteraction/validation.py | 533 | yes | CLEAN | |
| src/RimMandrake/Utils/pulse/pulse.py | 585 | ? | PENDING | |
| src/RimMandrake/DivingInteraction/Source/RM_DivingSettings.cs | 658 | yes | CLEAN | |
| src/RimUtinni/Rites/validation.py | 700 | yes | CLEAN | |
| src/RimMandrake/Utils/validation_core.py | 774 | yes | SKIPPED | SKIPPED: another helper has uncommitted edits (sweep_at_start) |
| src/RimMandrake/FlowWorks/Source/Hose/CompHoseReel.cs | 944 | yes | CLEAN | |
| src/RimMandrake/Utils/pulse/pulse_core.py | 965 | ? | PENDING | |
| src/RimMandrake/FlowWorks/Source/Pits/Suspension/RM_SuspensionPatches.cs | 993 | yes | CLEAN | |
| src/RimMandrake/FlowWorks/northstar/proof_hose.py | 1144 | yes | CLEAN | |
| src/RimMandrake/FlowWorks/northstar/lines_proof.py | 1166 | yes | CLEAN | |
| src/RimMandrake/FlowWorks/northstar/walk_gaps_proof.py | 1208 | yes | CLEAN | |
| src/RimMandrake/FlowWorks/northstar/scenarios_map.py | 1372 | yes | CLEAN | |
| src/RimMandrake/Utils/art/artledger.py | 1376 | yes | CLEAN | |
| src/RimMandrake/ExplosiveGrowth/validation.py | 1565 | yes | CLEAN | |
| src/RimMandrake/FlowWorks/Source/Hose/HoseMath.cs | 1791 | yes | CLEAN | |
| src/RimMandrake/LuminousPigment/validation.py | 1794 | yes | CLEAN | |
| src/RimMandrake/FlowWorks/Source/SelfTest/Program.cs | 2121 | yes | CLEAN | |
| src/RimMandrake/FlowWorks/northstar/validation_v2.py | 4888 | yes | SKIPPED | SKIPPED: another helper has uncommitted edits |

## Items filed

## Commits

- 425091e33d DeepDrill validation unused REPO; DivingInteraction validation stale docstring/toggle count, TypeError on a missing hatch temperature row
- f531265895 proof_hose HW1 census failure is HARNESS not SITE (+selftest check); Rites validation false claim about set_setting and static fields

Files with a prior clean mark were reviewed diff-scoped from the commit whose blob matches the recorded sha256 (standing_rulings: incremental review is valid once CLEAN).
