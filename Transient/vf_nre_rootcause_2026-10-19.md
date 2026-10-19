# Vehicle Framework NRE on the donor-free 535 list: root cause (2026-10-19)

Read-only investigation, FOUNDRY. Source: the live `Player.log` (one session, 535 mods; one save load at
line 8496: `Loading game from file RM_TestSite_contagion_v1`). The literal-string log searches ran with
`MEASURE_ALLOW_SCAN=1`. Decompiled with `ilspycmd.exe`: Vehicles.dll (workshop 3014915404, VF 1.6.2144) and
vanilla Assembly-CSharp.

## Root cause: a removed donor's C# class is still in the save's areaManager

The save still names a class from `oskarpotocki.vfe.insectoid2` (removed). The chain, first exception first:

| line | event |
|---|---|
| 10467-10475 | `Could not find class VFEInsectoids.Area_Hive` in `<areaManager><areas>` → falls back to abstract `Verse.Area` → `Can't load abstract class` → a **null** entry in the areas list |
| 10476-10479 | `NullReferenceException at Verse.AreaManager.UpdateAllAreasLinks ← AreaManager.ExposeData ← SaveableFromNode` → **the whole areaManager is discarded: `map.areaManager == null`** |
| 10548-10554 | `VehiclePathFinder..ctor` NRE. Decompiled ctor: `map = mapping.map; roadGrid = map.areaManager.Get<Area_Road>();` → the NRE is the null areaManager. **No VehicleDef is at fault**: the first VehicleDef iterated throws, whichever it is. |
| 10571, 10868 | the same, at FillComponents again (PostLoadInit, then FinalizeLoading) |
| 12302 onward | `Exception spawning loaded thing RM_Toothmoss…`: 6461 such lines, all one stack (`Ref D4C1B192`, VF `PathingHelper.RecalculatePerceivedPathCostAt`, which needs the missing VehiclePathingSystem) |
| 25252 | `Reached max messages limit`: the log went blind, so the step where map init aborted is not visible |
| 25278 | `MapDrawer.WholeMapChanged` NRE: `sections` is null (decompiled), so `mapDrawer.RegenerateEverythingNow` never ran and **the map never finished initialising**. This is the blank screen. |
| 26027-26474 | more `areaManager` consumers fail: `JobGiver_DropUnusedInventory`, `WanderUtility.GetColonyWanderRoot`, PrisonLabor `CanWorkHere` |
| 87685 / 87724 | `PawnTweener.TweenedPosRoot` NRE for Lumpy: thrown **inside the vanilla method body** (`pawn.ageTracker.CurLifeStage…`/`pawn.pather.MovingNow` at IL 0x53), before any postfix runs. GiddyUp, VEF, LargePawns, GravTide and our `RM_Patch_PitDepthDrawOffset` only appear on the stack; none of them is the source. Pawn state on a map that never finished init. |

Other missing-class lines (10368 VFEInsectoids GameComponent, 10455/10524 AlphaBiomes components, 10529-10543
our FloodedCanyon map components because `mandrake.rm.floodedcanyon` is not active) are **non-fatal**: an
abstract component is simply skipped. Only the **Area** is fatal, because one null area kills the whole AreaManager.

## Caused by what?

- **Caused by the donor removal** (VFE Insectoids 2), meeting a save authored with it. The save names VFEI2
  defs (10497-10520) and its GameComponent (10368). With VFEI2 loaded, `Area_Hive` resolves, so this chain
  cannot happen on the 542 list.
- **Not caused by the 2026-10-19 deploy.** None of our frames is on the first chain.
- **Not a VehicleDef problem and not VF's fault.** No VehicleDef config error is involved, and no vehicle def
  or VF patch depends on a removed donor.
- `Player-prev.log` (04:28, 542 list) loaded no game, so the two sessions cannot be compared directly. The
  mechanism above is enough to show the cause.
- **"Every map fails" is not shown by this log.** It holds ONE save load and no fresh map generation. A fresh
  map builds a new AreaManager and should not break. Every **save** carrying the class would break the same way.

## Saves carrying `VFEInsectoids.Area_Hive` (literal grep, 1 hit each)

`RM_TestSite_contagion_v1`, `RM_TestSite_calm_v1`, `RM_TestSite_cauldron_v1`, `RM_TestSite_leaningscrub_v1`,
`RM_TestSite_river_v1`, `CANONICAL_ASHKARR_START_2026-09-12.rws` and
**`CANONICAL_ASHKARR_START_2026-09-12.DONORFREE_CANDIDATE_2026-10-18.rws`**. `RM_TestSite_calm_v2`: 0.

**The candidate itself is affected.** `save_donor_census.py` matches defNames in element text only. C# type
names in `Class="…"` attributes are a blind spot of the donor-free save check (`save_adoption_check.py`
has no Class= pass either).

## Smallest fix

In each listed save (back up first; `rimworld-savegame` skill), delete the one element
`<li Class="VFEInsectoids.Area_Hive">…</li>` from `<areaManager><areas>`. It is an empty 250×250 grid
(ID 13 in contagion_v1). Nothing references an area by ID except zones and policies naming *that* area, and
the hive area is VFEI2-only. Then reload. Expect: no `UpdateAllAreasLinks` NRE, no VehiclePathingSystem NRE.

Follow-up worth filing: give the donor-census tooling a pass that lists every `Class="X.Y"` whose
namespace belongs to a removed donor assembly, and flag `Area`/`Designation`-type ones as fatal.
