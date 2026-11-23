# RIMMANDRAKE_DARKEN_PIT_FLOOR_BELOW_GROUND_SLATE_DRAWS_BRIGHTER

## spec
A dry FlowWorks pit floor draws darker than the ground the pit was dug in, on every ground a player digs in. Today the floor is
one brown gravel tone (RM_Channel_*) on any ground: `RM_PitReliefMath.StepK` is written as "a multiplier on undug ground" but is
a multiplier on gravel. On dark ground (rich soil, marsh, mud, slate) a 0.5 m floor is as bright as the ground or brighter, and
the 2 m floor in slate is only 10 % darker. The original ground of each dug square is already stored
(`RM_MapComponent_Excavation.OriginalTerrainAt`).

Two different builds; the owner's look question decides which:
- (A) keep the brown gravel floor and darken it by the ground's own brightness (a per-ground factor in `StepFloorShade`);
- (B) give the floor the material of the ground it was dug in (a slate pit has a slate floor); this also removes the brown floor
  in grey rock.

Files: `src/RimMandrake/FlowWorks/Source/RM_PitReliefMath.cs`, `src/RimMandrake/FlowWorks/Source/Superdeep/RM_ExcavationWalls.cs`,
`src/RimMandrake/FlowWorks/Defs/Canals/TerrainDefs/FlowWorks_Terrain.xml`.

## verify
Live, on any free game (red 2026-11-23 on build 81ee41df54: SoilRich, MarshyTerrain, Mud and Slate_Rough FAIL; Soil, Sand, Gravel,
Granite_Rough and Marble_Rough PASS):

    python.exe src/RimMandrake/FlowWorks/northstar/pit_floor_ground_live.py     # exit 0, 9 of 9 rows PASS
    python.exe src/RimMandrake/FlowWorks/northstar/pit_floor_ladder_live.py     # stays exit 0, 5 of 5 rows PASS

## criteria
- 9 of 9 `FLOOR_DARKER_THAN_ITS_GROUND_<ground>` rows PASS: the 0.5 m and the 2 m floor are each at least 10 % darker than their
  own ground.
- The depth ladder keeps its 5 rows (each doubling darker, the law, the 16 m floor keeps its grain).
- Failing moment: `design/specs/2026-11-23-pit-floor-depth-ladder/img/pit_floor_on_nine_grounds.png`; keeper save
  `RM_PIT_FLOOR_ON_NINE_GROUNDS` (ArchBig Saves, the 23-mod list).
