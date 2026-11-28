# WB-pipeline-read-other-20261128-092015: state

Ten fresh-reader tickets over 17 FlowWorks files (all NO PAGE on design/specs; page = FlowWorks locked bars + test_table rows).

## Done
- 2026-11-28: claimed RIMMANDRAKE_READ_FIX_70390D63_WITH_FRESH_EYES (a376a16d5f).
- Five fresh readers (rm-builder, Opus) launched, one per group; brief:
  /mnt/d/ClaudeWork/scratch/WB-pipeline-read-other-20261128-092015/reader_brief.md
  A proof_hose.py, review_map_coverage.py | B RM_MapComponent_Excavation.cs, RM_NotLiquidExtension.cs, RM_DeepSand.xml,
  GptFixesAChecks.cs | C RM_LadderParity(.cs, Math.cs), FlowWorks_LadderClimbers.xml, RM_PitAccess.cs |
  D RM_PitReliefMath.cs, RM_ExcavationWalls.cs, RM_FaceMaterial.cs | E Designator_SuspensionBridge.cs,
  RM_SuspensionMath.cs, RM_LiquidBottleUtility.cs, LakeFloorChecks.cs

## Next
- On each reader's return: CLEAN file -> code_review_status.py mark-clean; fixed file -> commit fix, flag; polish lines
  -> design/concepts/FlowWorks/version/polish.md; then close each ticket whose `fresh_reader.py holds` passes.
- A restart re-launches only the groups whose files still read DIRTY.
