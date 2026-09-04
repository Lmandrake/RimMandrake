# RimWorld 1.6 layer mechanics — source truth

Every symbol here was read out of the RimWorld C# source. Nothing is recalled
from memory. Where something was not read, it says UNMEASURED.

## Power

### How a net forms
`PowerNetMaker.NewPowerNetStartingFrom(Building root)` flood-fills
(`ContiguousPowerBuildings`) over `GenAdj.CellsAdjacentCardinal`, collecting
buildings whose `TransmitsPowerNow == true`. Those become the `transmitters` of
one `PowerNet`. Driven by `PowerNetManager.TryCreateNetAt`, processed from a
`DelayedAction` queue in `PowerNetManager.UpdatePowerNetsAndConnections_First()`
— **on tick**, so a paused game has not yet resolved a net you just built.

### Two different joining rules — this asymmetry is the trap
- **Transmitters** (`CompProperties_Power.transmitsPower == true`: conduits,
  walls with embedded conduits, `CompPowerTransmitter`) chain by **cardinal
  cell adjacency only**. Diagonal does not connect.
- **Connectors** (`ThingDef.ConnectToPower == true` — `CompPowerTrader` or
  `CompPowerBattery` that do *not* transmit) do **not** need a conduit in their
  own cell. `PowerConnectionMaker.BestTransmitterForConnector` builds a
  `CellRect.ExpandedBy(6)` and picks the nearest live transmitter by squared
  horizontal distance, requiring `transmitter.PowerComp.TransmitsPowerNow` and
  `transmitter.def.building.allowWireConnection`. Then
  `CompPower.ConnectToTransmitter` sets `connectParent`/`connectChildren` and
  calls `PowerNet.RegisterConnector`.

**`PowerConnectionMaker.ConnectMaxDist = 6`** (`private const int`).

⚠️ A generator is a *connector*, not a transmitter. Two conduit runs that never
touch cardinally are two nets, and a generator adjacent to one of them joins
only that one. Measured live: a `SolarGenerator` reading `Grid excess: 690 W`
four cells from a conduit run reading `0 W`.

### Conduit under a wall
`PowerConduit` sets `<building><isEdifice>false</isEdifice>
<isPowerConduit>true</isPowerConduit></building>` and
`<altitudeLayer>Conduits</altitudeLayer>`. Only one **edifice**
(`BuildingProperties.isEdifice`, default `true`) may occupy a cell —
`GenConstruct` enforces via `ThingDef.IsEdifice()`. A non-edifice conduit
therefore stacks under a wall legitimately.

`BuildingProperties.ConfigErrors` enforces the corollary: `holdsRoof && !isEdifice`
is a config error.

### Brownout
`PowerNet.CurrentEnergyGainRate()` sums `EnergyOutputPerTick` over `PowerOn`
`CompPowerTrader`s; consumers report negative. In `PowerNet.PowerNetTick()`, if
`CurrentStoredEnergy() + CurrentEnergyGainRate() < -1E-07f`, every
`ShutdownInterval = 20` ticks it shuts off `RoundToInt(count * ShutdownMinFraction)`
(`0.05f`) of the running consumers until supply matches demand.

### Solar at night
`CompPowerPlantSolar.DesiredPowerOutput` =
`Mathf.Lerp(0f, -Props.PowerConsumption, parent.Map.skyManager.CurSkyGlow) * RoofedPowerOutputFactor`.
`CurSkyGlow` is 0 at night ⇒ **exactly 0 W**, regardless of roofing.

🔑 In-game hour = `ticksAbs % 60000 / 2500`. A power test at hour 21 measures
nothing at all.

## Roof

**`RoofCollapseUtility.RoofMaxSupportDistance = 6.9f`** (`public const float`).
`RoofSupportRadialCellsCount = GenRadial.NumCellsInRadius(6.9f)`.

**Support is any edifice with `ThingDef.holdsRoof == true`** — not "a wall" by
name. Walls merely happen to ship it.

`RoofCollapseUtility.WithinRangeOfRoofHolder(IntVec3 c, Map map, bool assumeNonNoRoofCellsAreRoofed = false)`
flood-fills from `c` **through already-roofed cells only**, within 6.9f
horizontal distance, inspecting `c2.GetEdifice(map)` for `def.holdsRoof`.
`RoofCollapseCellsFinder.ProcessRoofHolderDespawned` runs it for every cell in
the radial set around a despawned support; failures go to
`map.roofCollapseBuffer.MarkToCollapse(...)`.

⚠️ Because it flood-fills *through roofed cells*, straight-line distance is a
lower bound, not the rule. An approximation should err toward over-warning.

### Roof kinds
`RoofConstructed`, `RoofRockThin`, `RoofRockThick` are all `RoofDef` data, not
separate classes; they differ in `isThickRoof`, `VanishOnCollapse`, `canCollapse`.
`RoofRockThick` is special-cased in `RoofGrid` and blocks light differently
(`SectionLayer_LightingOverlay` checks `isThickRoof`). Constructed and thin
behave alike for light.

## Terrain — three grids plus a scratch layer

`Verse.TerrainGrid` holds parallel `TerrainDef[]`:
- **`topGrid`** — the visible surface: a constructed floor, or bare natural terrain.
- **`underGrid`** (private; `UnderTerrainAt`) — natural terrain hidden beneath a
  floor, set automatically in `SetTerrain` when the new terrain is `layerable`.
- **`foundationGrid`** — the **Odyssey** addition, populated only by terrains
  with `TerrainDef.isFoundation == true`, via `TerrainGrid.SetFoundation`.
  `TerrainAt` falls back to it when `underGrid` is empty.
- **`tempGrid`** — transient terrain (ice, mud) overlaying everything in lookup.

**`BuildableDef.terrainAffordanceNeeded`** (`TerrainAffordanceDef`) gates
placement: `terrainDef.affordances.Contains(thingDef.terrainAffordanceNeeded)`,
checked in `GenConstruct`.

**`TerrainDef.IsSubstructure`** is `HasTag("Substructure")`.
`CompPowerPlantGravcore` checks
`parent.Map.terrainGrid.FoundationAt(parent.Position)?.IsSubstructure` and
disables with `"MessageMustBePlacedOnSubstructure"`. Also gated on it:
`Building_GravEngine.ValidSubstructureAt`, `CompGravshipThruster.IsBlocked`,
`PlaceWorker_BuildingsValidOverSubstructure`, `PlaceWorker_InvalidOverSubstructure`.

🪤 **`CompFacility` links form ONCE, at the facility's spawn, and never retry.**
A gravship thruster whose exclusion zone touches substructure at spawn time
stays permanently unlinked even after the zone later clears — the link is not
re-evaluated, so waiting fixes nothing. Destroy and rebuild the thing. (2026-08-28)

**Bare vs covered, testably:** `TerrainDef.layerable` decides whether a new top
terrain preserves the old into `underGrid`; `TerrainDef.isFoundation` marks the
foundation layer; `IsFloor` / `IsCarpet` separate constructed floors from bare
ground.

## Rooms, enclosure and access

### Formation
`RegionMaker.TryGenerateRegionFrom` classifies each cell via
`IntVec3.GetExpectedRegionType`: `Normal` (walkable), `Portal` (has a door),
`Fence`, `ImpassableFreeAirExchange`, `None`. Contiguous same-type regions form
a `District`. `RegionAndRoomUpdater.ShouldBeInTheSameRoom(District a, District b)`
merges districts into a `Room` only if both are `Normal`/`ImpassableFreeAirExchange`
(or a `Fence` bridges two). **`Portal` never merges with anything.**

### Doors
A `Building_Door`'s *cell* becomes `RegionType.Portal`, a permanent 1-cell
Region → District → Room. `Room.IsDoorway` / `Room.Door` read
`districts[0].Regions[0].door`. `Room.UpdateRoomStatsAndRole` sets
`role = RoomRoleDefOf.None` whenever `!ProperRoom`.

🔑 So 1-cell rooms with `properRoom: false` and role `None` in a read-back are
**doors**, and are correct.

### Enclosure properties (`Verse/Room.cs`)
- **`ProperRoom`** — `false` if `TouchesMapEdge`; else true iff some district has
  `RegionType.Normal`.
- **`PsychologicallyOutdoors`** — `OpenRoofCountStopAt(300) >= 300`, **or**
  `TouchesMapEdge && (OpenRoofCount / (float)CellCount) >= 0.5`.
- **`UsesOutdoorTemperature`** — `true` if `TouchesMapEdge`; else true iff
  `OpenRoofCount >= Mathf.CeilToInt(CellCount * 0.25f)`.
  🔴 **This is the property that decides whether a shell can hold temperature at
  all.** Check it before blaming a cooler.
- **`TouchesMapEdge`** — any district with `numRegionsTouchingMapEdge > 0`.
- **`OpenRoofCount`** — cells where `!roofGrid.Roofed(cell)`.

### Reachability
`Reachability.CanReach(IntVec3 start, LocalTargetInfo dest, PathEndMode peMode, TraverseParms traverseParams)`
on `Map.reachability`: same-district fast path, else region-graph BFS
(`CheckRegionBasedReachability`). `TraverseParms.For(TraverseMode, Danger)`;
`TraverseMode` = `ByPawn, PassDoors, NoPassClosedDoors, PassAllDestroyableThings,
PassAllDestroyablePlayerOwnedThings, NoPassClosedDoorsOrWater,
PassAllDestroyableThingsNotWater`.

For "reachable from outside" there is a dedicated
`Reachability.CanReachMapEdge(IntVec3 c, TraverseParms traverseParms)`, and
`ReachabilityUtility.CanReachMapEdge(this Pawn)`.

### The offline equivalent
Enclosure reduces to pure geometry: build the region graph the way
`GetExpectedRegionType` does (walkable = Normal, door = passable Portal,
full-fillage = impassable), then a room is sealed iff its flood-fill never
reaches a map-boundary cell **and** open-roof fraction < 0.25. That is literally
the negation of `UsesOutdoorTemperature`, and it needs no running game.

## Vanilla resource pipes

CONFIRMED negative: a source search for `CompPipe|PipeNet` across the vanilla
`*.cs` returns nothing. The only vanilla network is `PowerNet`. Odyssey's
substructure connectivity (`Building_GravEngine.ValidSubstructure`) is a
flood-connectivity set, not a resource-carrying net. `GlowGrid` and `RoofGrid`
are single-purpose grids.

## Source files
`Source/RimWorld/`: `CompPower.cs`, `PowerNet.cs`, `PowerNetManager.cs`,
`PowerNetMaker.cs`, `PowerConnectionMaker.cs`, `CompPowerPlantSolar.cs`,
`RoofDefOf.cs`, `BuildingProperties.cs`.
`Source/Verse/`: `RoofCollapseUtility.cs`, `RoofCollapseCellsFinder.cs`,
`TerrainGrid.cs`, `TerrainDef.cs`, `BuildableDef.cs`, `Room.cs`, `District.cs`,
`RegionAndRoomUpdater.cs`, `RegionMaker.cs`, `RegionType.cs`,
`RegionTypeUtility.cs`, `Reachability.cs`, `Building_Door.cs`, `TraverseMode.cs`.
`Defs/Core/ThingDefs_Buildings/Buildings_Power.xml`.
