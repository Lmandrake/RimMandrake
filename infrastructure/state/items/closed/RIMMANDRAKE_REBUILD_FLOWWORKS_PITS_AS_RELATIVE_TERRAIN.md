# RIMMANDRAKE_REBUILD_FLOWWORKS_PITS_AS_RELATIVE_TERRAIN

## What the card said

<!-- answered 2026-11-20T15:08:05Z; recorded by `file` (OWNER); written by rimflow, never by hand -->

**Question:** Second question. You dug a pit with a step in its floor: two rows 3.5 m deep beside one row 5 m deep. Movement obeys the step, but the floor draws as one flat dark area. Your words: "Clearly you have not implemented the pit visuals as relative terrain representation... That won't do. Need more generalization." 'Relative terrain' means the wall and shading art is drawn wherever two neighbouring squares differ in height, not only where a pit meets the surface. I guess, at about 50%, that the same change would also fix the pit walls showing through the cover at station 47. Effort is unread; the helper is reading the draw code now. Where does drawing pits as relative terrain belong?
**Picked:** In 0.1.0, full rebuild (Recommended)
**Its description:** Why: you said "That won't do", and stepped digs are ordinary play. Buys: inner walls and shading at every height change. Costs: a rewrite of pit drawing; my guess is 2 to 4 runs, geometry solved offline first, then one look from you. 0.1.0 waits on it. Recommended: by your rule a defect a player would reject stays in the current version.
**Other options:** Cheap cue now, rebuild later · Next version entirely · Wait for the code read

## spec

FlowWorks Design Version 0.1.0, Convergent, a Problem (his card 2026-11-20, above). Source: `design/RimMandrake/validation_holding/flowworks_walk_20261120.md` part 2, picture 7.

**What he dug** [measured, his save `FLOWWORKS_OWNER_WALK_END_20261120`, depth grid read from a copy]: cells x198-200; rows z124 and z123
at 7 notches (3.5 m), row z122 at 11 notches (5.5 m; he said 5 m). It drew as one flat floor. The "-5" on every square is the vanilla
beauty overlay (playSettings `showBeauty` True; `RM_Channel_Superdeep` has Beauty -5), not a depth reading.

**What the draw keys on today** [measured]:
- Walls: `SectionLayer_RMExcavationWalls` (`src/RimMandrake/FlowWorks/Source/Superdeep/RM_ExcavationWalls.cs:28`) draws every dug square; for the north,
  west and east neighbours it reads the neighbour's depth (`NeighbourLevel`, `:595-602`) and takes the exposed drop
  `myDepth - neighbourDepth` (`RM_UnderLiquid.Exposed`, `Source/Superdeep/RM_UnderLiquid.cs:278-284`); the outline (`:216-239`) draws
  every side whose neighbour is shallower. So the planner is already relative: his 5.5 m row should carry a 0.50-cell north face.
- Redraw: the layer re-prints only on a Terrain or LookFlag change (`:37`). `DeepenWithin` (`Source/RM_MapComponent_Excavation.cs:1700-1745`)
  writes the depth and calls `ApplyFillTerrain`, which returns at `cur == want` (`:3681-3684`); every depth past 2 m is the same
  terrain (`Source/RM_ExcavationDepth.cs:80-92`). So a square cut deeper than 2 m never redraws, nor do its neighbours: the step he
  dug is in the grid but not in the picture [measured code path; that his pit's last re-print came at equal depths: guess ~80%].
- Floor: the floor is the square's terrain, one of four colours by depth (`Defs/Canals/TerrainDefs/FlowWorks_Terrain.xml:32-124`:
  plain Gravel at 0.5 m, then 0.78, 0.58, 0.38); every depth past 2 m is the same 0.38 floor. Faces stop growing at a 2.5 m drop
  (`Source/RM_WallFaceMath.cs:26`, `NorthMax`); deeper only darkens the face foot by 12 alpha a notch (`RM_ExcavationWalls.cs:158`).

**What the rebuild needs**: a redraw on every depth change (the square and its four neighbours); a face and a line on every edge
where two neighbours differ (the planner has this; keep it); a floor shade by depth past 2 m, so a step between two deep rows reads;
face height and foot shade that keep telling drops apart past 2.5 m; the depth readout unchanged (it is right).

**Geometry first, offline, in Python** (his standing preference): a planner `src/RimMandrake/FlowWorks/model/pitdraw.py` with `plan(heights)` over the whole
space of neighbour height pairs (0..cap notches, dry and wet), checked against the acceptance test, before any C#.

**Today's faults this rebuild should absorb** (fix them in the same run, not twice):
- the walls and outline showing through a concealed cover, RIMMANDRAKE_HIDE_FLOWWORKS_PIT_WALLS_UNDER_CONCEALED_COVER: same layer;
  the walls draw at queues 2440-2449 over the cover and never ask about a cover [measured]; the rebuild skips covered squares [guess ~80% it fixes it];
- the pale frame in water, RIMMANDRAKE_DIM_FLOWWORKS_DROWNED_WALLS_PALE_FRAME_IN_WATER: same file, `SideUnder` [measured same code]; fixed by the rebuild [guess ~70%];
- the dark halo round the deepest pit, RIMMANDRAKE_FADE_DEEP_PIT_HALO_DARKENS_THE_BANK: the bank collar and halo are drawn in the same layer
  (`Collar`, `ScorchHalo`, `RM_ExcavationWalls.cs:66-74`) [measured]; that the halo comes from there [guess ~50%];
- the canal floor reading lighter than a pit floor: the colour ramp above [measured]; his ask "a darker floor would likely help".

## verify

Offline: the acceptance test below, then the planner's own selftest over all neighbour height pairs. Live: his pit on save `FLOWWORKS_OWNER_WALK_END_20261120` (x198-200, z122-124) and the review map's dry holes (stations 34-39), zoomed captures, then his look.

## criteria

Acceptance test: `python3 src/RimMandrake/FlowWorks/acceptance_pit_relative_terrain.py` (exit 0). On base 4f5b97b652 it reads 1 of 3 PASS (planner_faces_every_step PASS; deepening_redraws_walls FAIL; floor_shade_follows_depth_past_two_metres FAIL), watched red 2026-11-20; on a planted fix (a MapMeshDirty in DeepenWithin, a deeper terrain past 2 m) it reads 3 of 3, and a planner broken to 'pit or no pit' turns case 1 red. Live look: UNRUN (`FLOWWORKS_OWNER_WALK_END_20261120`, his pit). Rename the test selftest_flowworks_pit_relative_terrain.py once green.
