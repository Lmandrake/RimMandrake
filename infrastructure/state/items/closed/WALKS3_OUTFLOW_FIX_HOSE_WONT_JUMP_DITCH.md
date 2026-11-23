## spec
found-by: SITTING_GAPS_FIX_READS_BLANK_GRAPHIC_PATHS (offline read, 2026-11-05).
`src/RimMandrake/FlowWorks/northstar/water_scenes_walk.py` `s3_geom()` sets `outflow=canal[0]` and `_pump_rig` lays hose B
onto that dug depth-1 square. A dug square is hose band 1 and `CordWorld.StepAllowed`
(`src/RimMandrake/_Shared/SlackGeometry/CordWorld.cs`) refuses a band change without a ramp/ladder link (PIPE_POLES phase 6,
`src/RimMandrake/FlowWorks/Source/Hose/RM_HoseBands.cs`), so that lay reads "no route" whenever the line-crossing rules are on
(live: sitting_gaps run 1, 2026-10-23, the same geometry shifted). S3.a/S3.b need the outflow to pour INTO the canal, so a
bank end (what sitting_gaps_proof now does, `S3["outflow_bank"]`) may not be enough: decide whether the walk stages a ramp
(RM_PitRamp) at the canal head, or ends the hose on the lip and proves the spill reaches the canal.
Done when: the walk's S3 stage lays hose B (no "outflow hose not laid" staging note) and S3.a/S3.b read on a fresh run.
