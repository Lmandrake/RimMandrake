# Huge Things combined walk: grid key (plan only, not built)

For BENCH to build live and save as a keeper. Mod: **Huge Things** (`mandrake.rm.hugethings`) after the merge at
`c954ccdca`. The walk it serves is `design/validation_walks/RimMandrake/HugeThings.md`, step 8.

## Mod list
- Harmony
- Huge Things
- `mandrake.rm.biomes`, which carries every titan below (RustCathedral, LongShade, TheRot, Scarlands, WeepingStones and
  Stillsand are all in `Biomes.compose.json`)
- `sarg.alphabiomes`: six of the nine Rot giants are Alpha Biomes defs (`AB_*`) that the Rot patch opts in
- `neku.largepawns`, so the titans occupy 2x2 to 4x4 cells
- all five DLCs
- Do **not** load `mandrake.rm.titaniccreatures`. It is retired, and its About.xml is now `incompatibleWith` Huge Things.

## Map
- A quicktest map of at least 250 x 250, flat soil, daylight.
- Sweep hostiles (`kill_hostiles`) when you build it and on every visit.
- Tame every titan to the colony so none goes manhunter. The borehulk is a mechanoid (`BaseMechanoidWalker`), so spawn
  it as colony-owned instead.
- Give each titan an allowed area of 9 x 9 around its cell so it stays on its grid spot.
- All coordinates below are absolute map cells. A plant's coordinate is its **root** cell. Its picture rises north of
  the root, and is as tall as the drawn width given.
- Mod Settings stay at the defaults: both masters on, smash tier T3, wake on, custom tiers off.

## Titans (defNames checked in src, sizes read from the ThingDef and PawnKindDef)

Tiers use the shipped ladder: T1 from 4, T2 from 8, T3 from 20. "LP" is the Large Pawns footprint for that tier.

| cell | defName | body size | drawn size (adult) | tier | LP | defined in |
|---|---|---|---|---|---|---|
| C1 (20,90) | `RM_Borehulk` | 6 | 5 | T1 | 2x2 | `src/RimMandrake/RustCathedral/Defs/ThingDefs_Races/RM_Borehulk.xml` (mechanoid) |
| C2 (50,90) | `RM_Ulgga` | 6 | 8.2 | T1 | 2x2 | `src/RimMandrake/LongShade/Defs/ThingDefs_Races/RM_LongShade_Fauna.xml` |
| C3 (80,90) | `RM_Hwelgrue` | 8 | 6 | T2 | 3x3 | `src/RimMandrake/TheRot/Defs/Fauna/RM_Hwelgrue.xml` |
| C4 (110,90) | `RM_Totchak` | 14 | 7 | T2 | 3x3 | `src/RimMandrake/Scarlands/Defs/ThingDefs_Races/RM_Totchak.xml` |
| C5 (140,90) | `RM_Gorrask` | 15 | 5 | T2 | 3x3 | `src/RimMandrake/WeepingStones/Defs/ThingDefs_Races/RM_Gorrask.xml` |
| D1 (20,120) | `RM_Gloomcast` | 24 | 13.2 | T3 | 4x4 | `src/RimMandrake/LongShade/Defs/ThingDefs_Races/RM_LongShade_Gloomcast.xml` |
| D2 (50,120) | `RM_Oommok` | 36 | 15 | T3 | 4x4 | `src/RimMandrake/Stillsand/Defs/ThingDefs_Races/RM_Oommok.xml` |
| D3 (80,120) | `RM_Gloomcast` **corpse** | 24 | 13.2 | T3 | n/a | Spawn it, then kill it. It should stand as `RM_TitanicCorpseSite`. |

No patch in `src/` changes any of these body sizes (checked: the only patches naming them are acoustic, map-gen, track
and tolerance patches).

The design table had the hwelgrue drawn at 5. Its PawnKindDef draws it at **6**.

## Giant plants (the nine Rot giants), pitch 30

The drawn widths come from `measure_huge_plant_masks.py`. "Contact" is the number of ground-contact cells per variant.

| cell | defName | drawn width | contact |
|---|---|---|---|
| A1 (20,30) | `AB_AgariluxPrime` | 20 | 118 |
| A2 (50,30) | `AB_DribblingCap` | 12 | 28 |
| A3 (80,30) | `RM_Nogtyl` | 12 | 17 / 13 / 10 |
| A4 (110,30) | `RM_Arpeau` | 10 | 4 / 3 |
| A5 (140,30) | `AB_ArbuscularMycorrhiza` | 9 | 16 |
| B1 (20,60) | `AB_AgaricusDomeCap` | 7 | 10 |
| B2 (50,60) | `AB_GiantAgarilux` | 6 | 0 (its own cell is solid) |
| B3 (80,60) | `AB_WitchesOyster` | 6 | 9 |
| B4 (110,60) | `RM_PaleTree` | 6 | 3 |
| B5 (140,60) | `RM_Nogtyl` at growth 0.3 (a young giant: should block less than A3, or nothing below `minGrowthToBlock` 0.25) | 12 at full growth | |

## Test strip: three lanes running east, each with the same obstacles

| lane | z | titan | expected |
|---|---|---|---|
| L1 | 150 | `RM_Ulgga` (T1), a second one, spawned at (20,150) | It tramples the grass and takes the rubble trail. Walls, shelves and roofs are untouched. **It goes around the giant.** |
| L2 | 175 | `RM_Totchak` (T2), spawned at (20,175) | Grass, shelves and the wall line take crush damage (60 per pass). It holes the thin roof. It is slowed under the mountain roof. **It goes around the giant.** |
| L3 | 200 | `RM_Oommok` (T3), spawned at (20,200) | It destroys shelves and the wall outright and holes the thin roof. **It smashes the giant**: one heavy blow (60) per step while the trunk is in or beside its 4x4 footprint, until the plant falls. |

Obstacles in every lane. Here x is absolute and z is relative to the lane's z.

| x | what | defName / how | crush table says |
|---|---|---|---|
| 26 to 36, z-2 to z+2 | grass strip | `Plant_Grass` | T1+ crush (Plants row) |
| 40 | crates | two `Shelf` (WoodLog), each holding an item stack | the shelf crushes at T2+ (BuildingsFurniture is under the Buildings row). **The items are never crushed**: no row matches an Item. |
| 46, z-2 to z+2 | sandbag line | `Sandbags` (Cloth) | **never crushed**: Sandbags has no thingCategories, so no row matches. It is a control. |
| 50, z-2 to z+2 | wall line | `Wall` (WoodLog) | T2+ (the `RM_Crush_Walls` exact row); T3 destroys it outright |
| 58 to 64, z-3 to z+3 | thin-roofed room | Four corner `Wall` pillars only. `RoofConstructed` on the 5 x 5 interior x 59 to 63, z-2 to z+2. | T2+ holes it (the `wakeRoofHolingEnabled` setting) |
| 72 to 76, z-2 to z+2 | overhead mountain | `RoofRockThick` on the 5 x 5, with four corner `Wall` pillars at x 71 and 77 | Never removed. A titan stepping under it is slowed (step cost 2000). Route choice does not see it. |
| root at (92, z-1) | **giant fungus in the path** | `AB_DribblingCap`, growth 1 (28 contact cells, drawn 12 wide) | It is never on the crush table (the `RM_Crush_HugeTrunk` row). T3 smashes it, T1/T2 go around. |
| (110, z) | destination | `ordered_job Goto` to here, the same verb the validation chain uses | |

**Before ordering the titans,** check that the trunk actually crosses each lane. Run `jawa/list_things RM_HugeTrunkBlocker`
with rect `86,z-2,13,5`; it should find at least 3 cells. The picture is bottom-anchored on the root, and which variant is
drawn depends on the cell. If fewer than 3 come back, move the root one cell south and check again.

## What he looks at
- **Plants:** click the edges of each picture (cap tips, roots); each click should select the plant. Pawns path around
  the stems and walk under the caps. A wall ordered inside a stem is refused. B2's own cell is solid. B5 blocks less
  than A3.
- **Titans:** click anywhere on each drawn body (the ulgga's tail, the oommok's edge). With Large Pawns loaded, the
  square under each body is 2x2, 3x3 or 4x4 as listed. D3 stands as a corpse site, and a hauler works one harvest
  session on it.
- **The seam (his ruling):** in lanes L1 and L2 the titan walks around the dribbling cap. In L3 the oommok brushes it
  and smashes it, the cap's hit points fall step by step, and once it is gone its trunk cells vanish with it. A second
  check: set `giantPlantSmashMinTier` to T2 in Mod Settings, restage L2, and the totchak now smashes too.
- **Settings:** switch off the "Giant animals" master, unpause, and rerun L3. The oommok should leave nothing broken.
  Switch off the "Giant plants" master: every trunk clears within about 300 ticks, and the giants become ordinary
  plants, which a T1 tramples under the crush table.

## Build notes for BENCH (from the merge)
- Deploy before you build the save, with the game closed. The DLL is locked while the game runs.
  1. `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod HugeThings` to see the plan, then the same with `--apply`.
  2. Delete the old game folder `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\TitanicCreatures`.
  3. Swap `mandrake.rm.titaniccreatures` for `mandrake.rm.hugethings` in the list you load (`modset_builder.py` tiers
     already say hugethings).
- Old saves that list `mandrake.rm.titaniccreatures` show the "mod list changed" dialog and then load. Type names did
  not change, so trunk blockers, map components and corpse sites still resolve.
- Smashing happens at the trunk's edge, not by walking through it. The 1.6 pathfinder treats an impassable edifice as a
  hard wall, so a T3 titan routes around the giant like everyone else, hugging it. It smashes the giant on every step
  that brushes the trunk, and walks straight through once the giant falls.
