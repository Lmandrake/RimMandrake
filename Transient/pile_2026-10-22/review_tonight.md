# Review tonight — code changed since 2026-10-22 18:30 (BENCH helper)

Scope: .cs/.py in git log since 18:30, DIRTY per code_review_status, no uncommitted edits. Transient/ scripts skipped (one-shot, untracked shelf). Uncommitted at start (skipped): RM_MapComponent_Hoses.cs, HoseSelfTest.cs, modern_port_fittings.py, selftest_tank_art_edges.py.

| file | lines | reachable | verdict | note |
|---|---|---|---|---|
| src/RimMandrake/FlowWorks/art_source/LadderPortable/gen_a3.py | 18 | ? | PENDING | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/gen_a5.py | 20 | ? | PENDING | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/gen_a4.py | 21 | ? | PENDING | |
| src/RimMandrake/DeepDrill/Source/Kernel/RM_DeepDrillKernel.cs | 24 | ? | PENDING | |
| src/RimMandrake/Aftermath/Source/AftermathMod.cs | 25 | ? | PENDING | |
| src/RimMandrake/DeepDrill/Source/Patch_DeepHome.cs | 27 | ? | PENDING | |
| src/RimMandrake/DeepDrill/Source/RM_DeepHomeDef.cs | 32 | ? | PENDING | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/gen_a6.py | 34 | ? | PENDING | |
| src/RimMandrake/Utils/selftest_deepdrill.py | 36 | ? | PENDING | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/gen_a7.py | 37 | ? | PENDING | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/gen_a8.py | 43 | ? | PENDING | |
| src/RimMandrake/DeepDrill/Source/RM_DeepDrillMod.cs | 47 | ? | PENDING | |
| src/RimMandrake/Utils/art/selftest_art_guard_latest_retire.py | 47 | ? | PENDING | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/gpt_reference.py | 52 | ? | PENDING | |
| src/RimMandrake/DeepDrill/validation.py | 64 | ? | PENDING | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/gen_a2.py | 72 | ? | PENDING | |
| src/RimMandrake/Utils/mutate_graffiti_fuzz.py | 73 | ? | PENDING | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/compose_a2.py | 80 | ? | PENDING | |
| src/RimMandrake/FlowWorks/northstar/selftest_pipe_levelling_perf_proof.py | 81 | ? | PENDING | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/mock.py | 86 | ? | PENDING | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/compose_a3.py | 90 | ? | PENDING | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/compose_a4.py | 90 | ? | PENDING | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/compose_a8.py | 90 | ? | PENDING | |
| src/RimMandrake/DeepDrill/Source/SelfTest/Program.cs | 91 | ? | PENDING | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/compose_a5.py | 94 | ? | PENDING | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/compose_a6.py | 94 | ? | PENDING | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/compose_a7.py | 94 | ? | PENDING | |
| src/RimMandrake/FlowWorks/northstar/selftest_joint_check.py | 94 | ? | PENDING | |
| src/RimMandrake/FlowWorks/art_source/LadderPortable/gen.py | 104 | ? | PENDING | |
| src/RimMandrake/FlowWorks/Source/SelfTest/PitCoverBeneathChecks.cs | 106 | ? | PENDING | |
| src/RimMandrake/FlowWorks/Source/Hose/ReelIntakeGeometry.cs | 122 | ? | PENDING | |
| src/RimMandrake/Utils/art/selftest_art_provenance.py | 145 | ? | PENDING | |
| src/RimMandrake/DivingInteraction/Source/RM_SeabedFloorLife.cs | 165 | ? | PENDING | |
| src/RimMandrake/Aftermath/Source/MapComponent_BattleRecorder.cs | 172 | ? | PENDING | |
| src/RimMandrake/FlowWorks/Source/SelfTest/HoseWallSeamChecks.cs | 192 | ? | PENDING | |
| src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitDepthDraw.cs | 192 | ? | PENDING | |
| src/RimMandrake/FlowWorks/northstar/selftest_scenarios_map.py | 223 | ? | PENDING | |
| src/RimMandrake/Utils/mockups/messy_conduit/reel_intake_geometry.py | 223 | ? | PENDING | |
| src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitLipOcclusion.cs | 262 | ? | PENDING | |
| src/RimMandrake/FlowWorks/northstar/joint_check.py | 266 | ? | PENDING | |
| src/RimMandrake/FlowWorks/selftest_review_map.py | 275 | ? | PENDING | |
| src/RimMandrake/ExplosiveGrowth/Source/RM_ExplosiveGrowthPatches.cs | 314 | ? | PENDING | |
| src/RimMandrake/FlowWorks/review_map_rivers.py | 333 | ? | PENDING | |
| src/RimMandrake/Utils/pulse/selftest_pulse.py | 350 | ? | PENDING | |
| src/RimMandrake/FlowWorks/Source/Pits/Building_PitCover.cs | 354 | ? | PENDING | |
| src/RimMandrake/FlowWorks/northstar/pipe_levelling_perf_proof.py | 361 | ? | PENDING | |
| src/RimMandrake/FlowWorks/Source/RM_PromotionProofs.cs | 362 | ? | PENDING | |
| src/RimMandrake/Utils/art/selftest_art.py | 399 | ? | PENDING | |
| src/RimMandrake/FlowWorks/Source/Hose/HoseProbe.cs | 438 | ? | PENDING | |
| src/RimMandrake/Utils/art/art_guard.py | 439 | ? | PENDING | |
| src/RimMandrake/Utils/art/chat_review.py | 446 | ? | PENDING | |
| src/RimMandrake/Utils/art/art.py | 454 | ? | PENDING | |
| src/RimMandrake/FlowWorks/northstar/selftest_proof_hose.py | 476 | ? | PENDING | |
| src/RimMandrake/Utils/art/review_queue.py | 488 | ? | PENDING | |
| src/RimMandrake/ExplosiveGrowth/Source/RM_ExplosiveGrowthProof.cs | 492 | ? | PENDING | |
| src/RimMandrake/DivingInteraction/validation.py | 533 | ? | PENDING | |
| src/RimMandrake/Utils/pulse/pulse.py | 585 | ? | PENDING | |
| src/RimMandrake/DivingInteraction/Source/RM_DivingSettings.cs | 658 | ? | PENDING | |
| src/RimUtinni/Rites/validation.py | 700 | ? | PENDING | |
| src/RimMandrake/Utils/validation_core.py | 774 | ? | PENDING | |
| src/RimMandrake/FlowWorks/Source/Hose/CompHoseReel.cs | 944 | ? | PENDING | |
| src/RimMandrake/Utils/pulse/pulse_core.py | 965 | ? | PENDING | |
| src/RimMandrake/FlowWorks/Source/Pits/Suspension/RM_SuspensionPatches.cs | 993 | ? | PENDING | |
| src/RimMandrake/FlowWorks/northstar/proof_hose.py | 1144 | ? | PENDING | |
| src/RimMandrake/FlowWorks/northstar/lines_proof.py | 1166 | ? | PENDING | |
| src/RimMandrake/FlowWorks/northstar/walk_gaps_proof.py | 1208 | ? | PENDING | |
| src/RimMandrake/FlowWorks/northstar/scenarios_map.py | 1372 | ? | PENDING | |
| src/RimMandrake/Utils/art/artledger.py | 1376 | ? | PENDING | |
| src/RimMandrake/ExplosiveGrowth/validation.py | 1565 | ? | PENDING | |
| src/RimMandrake/FlowWorks/Source/Hose/HoseMath.cs | 1791 | ? | PENDING | |
| src/RimMandrake/LuminousPigment/validation.py | 1794 | ? | PENDING | |
| src/RimMandrake/FlowWorks/Source/SelfTest/Program.cs | 2121 | ? | PENDING | |
| src/RimMandrake/FlowWorks/northstar/validation_v2.py | 4888 | ? | PENDING | |

## Items filed

## Commits
