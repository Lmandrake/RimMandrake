# Remark pass 2026-10-09 (FOUNDRY helper)
Private clone: /home/mandrake/.seat-tmp/remark_clone (origin/main). Second full-file review of the files the first reviewer edited.
Files: RM_ShadeHop.cs, RM_MapComponent_TentacleWatch.cs, RM_HorizonWarning.cs, RM_MapComponent_Aerial.cs, BrineEncasementUtility.cs, RM_ExcavationWalls.cs (the sixth: ScorchHalo low alloc fix).

## Reviews (read from origin/main 76711eeb6)
- BrineEncasementUtility.cs: no findings (edifice destroyed only after TryEncase succeeded).
- RM_ShadeHop.cs: no findings.
- RM_MapComponent_TentacleWatch.cs: no findings (one Grant roll = one Thing, so unplaced = rolls - placed.Count is exact).
- RM_HorizonWarning.cs: fix (landed) — plume defNames/bearings could load as null strings; normalised to "" in PostLoadInit.
- RM_MapComponent_Aerial.cs: low alloc fix — DrawLocalDrops reuses scratch lists, hoists ExpandedBy; Deregister drops lastTerminals entry.
- RM_ExcavationWalls.cs: low alloc fix — ScorchHalo arrays and grid are per-layer scratch (ScorchFloor/SootFace allocs left: scorched dug cells only).

## Status
Landed: 693927dea (source + DLLs for FlowWorks, GimmeSomeSlack, Stillsand), d003947b1 (six clean records). All six files CLEAN at the landed content.
Selftests in the clone: 341/347 pass; the 4 non-passes are rimflow/bridgetools (items_glob_live, lease, built_old_reader, tool_metadata), none touch this C#.
Not landed: the clone's Transient/modcheck/fixtures.json drift from the selftest run.
