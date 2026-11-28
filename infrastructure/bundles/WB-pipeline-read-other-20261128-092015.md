# WB-pipeline-read-other-20261128-092015: state (FINISHED 2026-11-28)

Ten fresh-reader tickets over 17 FlowWorks files; page = FlowWorks locked bars + test_table rows (no design/specs page).
Five readers (rm-builder, Opus), one per group; brief /mnt/d/ClaudeWork/scratch/WB-pipeline-read-other-20261128-092015/reader_brief.md.

| ticket | outcome | commit |
|---|---|---|
| 70390D63 proof_hose.py | Problem fixed (scene 2 ignored the hose's fill; live FAIL on a working mod); FLAGGED | 810dc99e77, polish 3af94c5f2a |
| F0A9D24739 review_map_coverage.py | READ-CLEAN | 3af94c5f2a |
| D097EA3260 Excavation, NotLiquidExtension, DeepSand.xml, GptFixesAChecks | READ-CLEAN (T_DIG 36 cases, GptA/deep sand 25/25) | 01f2760e53 |
| B64B4353EF FlowWorks_LadderClimbers.xml | Problem fixed (HAR races missed); FLAGGED | 0028ce88bf |
| 8D559E4074 RM_LadderParity(.cs, Math.cs) | Problem fixed in RM_LadderParity.cs (wall ladder skipped ClimbEligible); FLAGGED; Math READ-CLEAN | 44a6a5cc72 |
| 669FE2FC9C PitReliefMath, ExcavationWalls, FaceMaterial | Problem fixed (corner-foot floor wedge); 2 FLAGGED, FaceMaterial READ-CLEAN | 44a6a5cc72, polish 633c3077a1 |
| 8491944D06 RM_LiquidBottleUtility.cs (+ WorkGiver_WashBottle.cs) | Problem fixed (barrel wash loop); both FLAGGED | 44a6a5cc72 |
| 989284C054 LakeFloorChecks.cs | READ-CLEAN | a6be6fda58 |
| A62C932133 RM_PitAccess.cs | READ-CLEAN | 042422f1c3 |
| 3B23DC14E9 suspension bridge | READ-CLEAN | a6be6fda58 |

Live: WATER_ONE_SURFACE_LIVE PASS on ArchSmall (flowworks_list, walk save), clean load, RM_LadderClimber live; row 7dcaa9b7b9.
Polish: 13 lines on design/concepts/FlowWorks/version/polish.md (042422f1c3). Lesson: winbuild.stage_build copies the DLL back.
