# Code review: tonight's builds (2026-10-17)

Commits: thirst 43266db9aa, 77ef5bfcc8 · sprinklers 799336e671, 05598e20ce · pond depth 0b60f7a80 ·
explosive growth 846b07e973, ff4759f445 · venomvine fe4addc7, d893ad30.
I reviewed for correctness only: crashes, wrong logic, save/load, hot-path allocation, Harmony targets, settings round-trip.
FlowWorks was NOT edited or built. The weir agent has uncommitted FlowWorks Source edits (PipeLook.cs,
PipeStyles.cs, Rivers/*), so each FlowWorks fix below is a written patch that someone still has to apply.
I found no clear bug in ExplosiveGrowth, LeaningScrub or EnvironmentalHazards, so nothing was rebuilt.

## Bugs owed (FlowWorks; apply, build, selftest once the weir agent's tree is committed)

### B1 — FIXED in e8ecd28f06 — Sprinkled cells are never restored on load (save/load) — `FlowWorks/Source/Sprinklers/RM_MapComponent_Sprinklers.cs:299-327`
`ExposeData` loads `cells/untils/owners/keys` into LOCAL lists, then rebuilds the grid only when
`Scribe.mode == PostLoadInit`. Scribe calls ExposeData again for each pass, so in PostLoadInit those locals are fresh
nulls (the data was read in LoadingVars and then dropped). The guard `cells != null` therefore never passes, and
the saved wet grid is dead weight. Effect: after every reload, every sprinkled cell reads dry until its head's next pulse
(up to 1 game hour; `nextPulseTick` is saved). Over that hour ExplosiveGrowth's charges on sprinkled crops drain at
the dry rate (about a third of a full charge at the default 6 h). The VFE valve's `WetByOther` also loses the other
heads' wet cells. Fix (local): rebuild in `LoadingVars`, where the lists are filled. `map.cellIndices` already exists
then, because Map.ConstructComponents runs before ExposeComponents.
```csharp
if (Scribe.mode == LoadSaveMode.LoadingVars && cells != null && untils != null && keys != null
    && cells.Count == untils.Count && cells.Count == keys.Count)
```

### B2 — FIXED in e8ecd28f06 — A stale "no water here" mark carries into the next loaded game — `FlowWorks/Source/Thirst/RM_ThirstUtility.cs:456,473-476,518-521`
`noTerrainUntil` is a static `Dictionary<thingIDNumber, tick>` that is never cleared. Thing IDs repeat across saves.
Suppose a pawn or animal is marked at tick 5,000,600 in game A. Load game B at tick 100,000, and B's pawn with the same
ID skips `TryFindDrinkCell` for about 80 game days. For an animal, which drinks only from terrain, that is death by
thirst with water in sight. The map also grows without bound, one entry per wild animal ever searched. Fix (local):
treat an "until" more than 600 ticks ahead as stale, and drop expired entries:
```csharp
if (noTerrainUntil.TryGetValue(pawn.thingIDNumber, out int until))
{
    if (now < until && until - now <= 600) return false;
    noTerrainUntil.Remove(pawn.thingIDNumber);
}
```
(Clearing it from a `GameComponent.FinalizeInit` would do the same job.)

### B3 — FIXED in e8ecd28f06 — Doctors carry water to downed hostiles — `FlowWorks/Source/Thirst/RM_ThirstJobs.cs:276-277`
In `WorkGiver_RM_AdministerWater.Wants`, the non-prisoner branch accepts
`patient.Faction == pawn.Faction || patient.HostFaction == pawn.Faction || patient.guest != null`. Every humanlike
has a `guest` tracker, so the faction test is a no-op. Any downed thirsty raider, in a bed or lying on the battlefield,
becomes a doctor job, and the doctor walks out under fire to hand them a bottle. Design §5 says "downed or imprisoned"
pawns, which means ours, not an enemy's. Fix (local):
```csharp
return !patient.IsPrisoner && (patient.Downed || patient.InBed()) && !patient.HostileTo(pawn)
    && (patient.Faction == pawn.Faction || patient.HostFaction == pawn.Faction);
```

## Perf notes (not bugs; no action required tonight)
- P1 (FIXED in e8ecd28f06, one-slot cache in Of()) `FlowWorks/Source/Sprinklers/RM_MapComponent_Sprinklers.cs:280-288` `WetAt` → `map.GetComponent` on every
  read. ExplosiveGrowth's sprinkled source calls it from the GrowthRate postfix, and for vanilla plants (setting A,
  `WaterNearby`) that is 25 cells per call, twice per TickLong. That is a linear walk of the component list each time.
  Measured cost is UNMEASURED. A one-slot `(Map, comp)` cache, like ExplosiveGrowth's `For()`, would remove it.
- P2 (left: needs a per-map dictionary, not a few lines) `ExplosiveGrowth/Source/RM_MapComponent_ExplosiveGrowth.cs:99-106` `For()` caches only one map. With pocket maps
  or several colonies the cache thrashes, and every miss calls GetComponent. This is correct, just slower on multi-map.
- P3 `FlowWorks/Source/Thirst/RM_ThirstUtility.cs:376` `BestBottle` allocates a candidate list per call. That is
  per think of a thirsty humanlike, not per tick, so it is acceptable.

## Per file

| file | read | verdict |
|---|---|---|
| FlowWorks/Source/Thirst/Need_RM_Thirst.cs | full | CLEAN, marked |
| FlowWorks/Source/Thirst/RM_ThirstMath.cs | full | CLEAN, marked |
| FlowWorks/Source/Thirst/RM_ThirstSettings.cs | full | CLEAN, marked (7 keys round-trip, defaults match) |
| FlowWorks/Source/Thirst/RM_ThirstProvider.cs | full | CLEAN, marked (ShouldHaveNeed target matches the cited decompile) |
| FlowWorks/Source/Thirst/RM_ThirstCaravan.cs | full | CLEAN, marked |
| FlowWorks/Source/Thirst/RM_ThirstUtility.cs | full | DIRTY: B2 fixed e8ecd28f06 (not whole-file re-read, not marked); P3 |
| FlowWorks/Source/Thirst/RM_ThirstJobs.cs | full | DIRTY: B3 fixed e8ecd28f06 (not marked) |
| FlowWorks/Source/Sprinklers/RM_MapComponent_Sprinklers.cs | full | DIRTY: B1+P1 fixed e8ecd28f06 (not marked) |
| FlowWorks/Source/Sprinklers/CompRM_SmartSprinkler.cs | full | CLEAN, marked |
| FlowWorks/Source/Sprinklers/CompRM_SprinklerHead.cs | full | CLEAN, marked |
| FlowWorks/Source/Sprinklers/RM_Sprinkle.cs | full | CLEAN, marked |
| FlowWorks/Source/Sprinklers/RM_SprinklerKernel.cs | full | CLEAN, marked |
| FlowWorks/Source/Sprinklers/RM_SprinklerSettings.cs | full | CLEAN, marked |
| FlowWorks pond depth (RM_FlowKernel, RM_LiquidStock, RM_MapComponent_Excavation, RM_LiquidBody, Mod, DefOf) | diff only | no bug found in the diff; not marked (I did not read the whole files). DefOf terrains RM_WaterChestDeepStill / RM_WaterThin exist in Defs/Canals/TerrainDefs/FlowWorks_PondStageTerrain.xml |
| FlowWorks/Source/RM_PondDepthMath.cs | not read | selftested, Verse-free; not marked |
| ExplosiveGrowth/Source/RM_ExplosiveGrowthPatches.cs | full | CLEAN, marked. GrowthRate postfix and dormancy prefix allocate nothing. Dormancy is safe because vanilla's `ageInt += 2000` is unconditional (decompiled Plant.cs:840) |
| ExplosiveGrowth/Source/RM_MapComponent_ExplosiveGrowth.cs | full | CLEAN, marked (P2 perf only) |
| ExplosiveGrowth/Source/RM_WetSources.cs | full | CLEAN, marked |
| ExplosiveGrowth/Source/RM_SoakSources.cs | full | CLEAN, marked |
| ExplosiveGrowth/Source/RM_SprinklerWetSource.cs | full | CLEAN, marked |
| ExplosiveGrowth/Source/RM_TopResolver.cs | full | CLEAN, marked |
| ExplosiveGrowth/Source/RM_ExplosiveGrowthRegistry.cs | full | CLEAN, marked. Every shipped roster XML still parses against the new roster fields; no retired field is used |
| ExplosiveGrowth/Source/Kernel/RM_ExplosiveGrowthKernel.cs | full | CLEAN, marked |
| _Shared/FlowWorksIrrigation/FlowWorksSprinklerRead.cs | full | CLEAN, marked |
| ExplosiveGrowth/Source/ExplosiveGrowthMod.cs | partial (fields, ExposeData, half the window) | all 49 Scribe keys round-trip with defaults equal to the field initialisers; not marked |
| ExplosiveGrowth/Source/RM_GrowthTop.cs, ExplosiveGrowthAPI.cs, RM_ExplosiveGrowthDefOf.cs | diff only | no bug found; not marked |
| ExplosiveGrowth/Source/RM_ExplosiveGrowthProof.cs, RM_ChargeSelfTest.cs | not read (proof/test harness) | not marked |
| LeaningScrub/Source/RM_VenomvineIslands.cs | full | CLEAN, marked |
| LeaningScrub/Source/Kernel/RM_IslandKernel.cs | partial (Grow, Reach, SizeIslands, IslandCount) | no bug found; not marked |
| LeaningScrub/Source/RM_LeaningScrubMod.cs | diff only | 11 new keys round-trip; not marked |
| EnvironmentalHazards/Source/CompContactVenom.cs, MapComponent_ContactVenom.cs | diff only | minGrowth gate is correct; not marked |

Build and selftests: none run. There was no fix in an unblocked mod, and FlowWorks is blocked by the weir agent's
uncommitted Source edits.
