## spec
Child of `WATER_DEPTH_RESKIN_HE_LOOKS_FIRST` (plan P9). In the 2026-10-17 water-scene review the water in a dug canal
and the lake it joins were drawn in different colours (relayed by the FOUNDRY seat; shots in
`Transient/fw_scenes/live/`). Bar `canal_reads_as_same_liquid_as_reservoir` says they must read as one substance.
Find which material, tint or depth band differs; any change is cosmetic and goes in the one P9 review for his look.

## verify
- L1: the cause is named (material, tint or band) with file:line.
- L3: in a frame, a filled canal and the lake it joins at the same water depth read as one colour.
- L4: in the P9 review he keeps it.

## finding (FOUNDRY, 2026-10-23, offline; L1)
The 2026-10-17 shots (`Transient/fw_scenes/live/S1_p14.png`) predate P14 and compare two DIFFERENT depth looks, not one
liquid in two tints:
- Lake: `water_scenes_walk.py:432` paints the whole lake rect vanilla `WaterDeep` (WaterDeepRamp + depth shader).
- Canal (1 level, under 0.75 m) was then the temporary fill layer `RM_Fill_Water_Trace`
  (`Defs/Canals/TerrainDefs/FlowWorks_Terrain.xml:277`, ParentName WaterShallow -> WaterShallowRamp): the shallow ramp,
  a paler, flatter picture than the deep lake.
- Since P14 (`ce36444ba`, 2026-10-18) water uses `freshwaterLadder` (`FlowWorks_Fluids.xml:25`) and a wet dug square
  draws the SAME def a natural pond does at that depth band (`Source/RM_WaterLadder.cs:71-79`: VeryShallow,
  RM_WaterThin, WaterShallow, RM_WaterChestDeepStill, WaterDeep). At equal water depth canal and lake are one def, so one
  colour; a 2 m+ canal beside the lake is vanilla WaterDeep on both sides.
- What can still differ: (a) depth itself, by design (depth spec §4.1: the water picture says how deep the WATER is);
  (b) `RM_WaterThin` / `RM_WaterVeryShallow` (`FlowWorks_PondStageTerrain.xml:33-62`) are plain tiled PROVISIONAL
  pictures with no water-depth shader, so the under-0.5 m rungs read differently from vanilla water; that art is owned by
  `WATER_DEPTH_RESKIN_HE_LOOKS_FIRST` / the very-shallow reskin and goes in the P9 review.
No colour change made here (cosmetic). Owed: L3 frame at equal depth on a current DLL; L4 his P9 look.
