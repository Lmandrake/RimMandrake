## answer

**YES — we can ship our own `temporary=true` terrains, with no Odyssey dependency.**
MEASURED 2026-09-20 from the decompiled 1.6 engine (RimSage, Windows Desktop).

The temp-terrain mechanism is entirely Core. Only the *defs* are DLC content:

| thing | where it lives | DLC-gated? |
|---|---|---|
| `TerrainDef.temporary` | `Verse/TerrainDef.cs:266` | no |
| `TerrainDef.tempTerrain` (`TempTerrainProps`) | `Verse/TempTerrainProps.cs` | no |
| `TerrainGrid.SetTempTerrain` | `Verse/TerrainGrid.cs:398` | no |
| `TerrainGrid.RemoveTempTerrain` / `tempGrid` | `Verse/TerrainGrid.cs` | no |
| `TempTerrainManager` | `RimWorld/TempTerrainManager.cs` | no |
| `Map.tempTerrain` construct + `Tick()` | `Verse/Map.cs:585`, `:972` | no — unconditional |
| the six shipped temp terrains | `Defs/Odyssey/TerrainDefs/Terrain_Temporary.xml` | **yes** |

🔑 **The proof that the absence of a gate is deliberate, not an oversight:** `TerrainDef`
gates when Ludeon means to — `TerrainDef.IsSubstructure` returns false outright unless
`ModsConfig.OdysseyActive`. `temporary` carries no such guard.

**The only two `ModsConfig.OdysseyActive` checks in the whole write path** are in
`TerrainGrid.DoTerrainChangedEffects` (`:553` substructure grid, `:558` fish population)
and one in `TempTerrainManager` (the `FreezeManager` that ices water). None of them is on
the set / hold / remove path; with Odyssey off, temp terrain still sets, persists, renders
and removes.

So the split the item describes is real but was never a mechanism split — FluidCanals was
Odyssey-locked purely because it *named* `ShallowFloodwater`/`MarshFlood`, which live in
Data/Odyssey and are reachable only via `MayRequire="Ludeon.RimWorld.Odyssey"`.

## trap for whoever builds the next temporary terrain

🔴 **Temp terrain has NO intrinsic duration. It is permanent until something removes it.**
`TempTerrainProps` carries only `terrainOnRemoved`, `destroysFloors`, `removedByExplosions`
and `replaceableByBridge` — no ticks field. `TempTerrainManager.Tick` drains a priority
queue that a *caller* must fill with `QueueRemoveTerrain(cell, tick)`; every vanilla user
(`SeasonalFlood`, `TorrentialRainFlood`, `GameCondition_LavaFlow`, `LavaEmergence`,
`FreezeManager`) computes its own removal tick. Set temp terrain without queueing a
removal and it never recedes.

⚠️ Also: `SetTerrain` silently ROUTES any `temporary` def to `SetTempTerrain`
(`TerrainGrid.cs:205`), so a temporary def assigned through the ordinary path lands on the
temp layer, not `topGrid` — which is the desired behaviour, but not what the call reads like.

## outcome

No work owed — the answer was already applied before this item was measured. FlowWorks
already ships its own temporary terrains (`RM_Fill_Water_Trace`/`_Half`/`_Brim`,
`ParentName="WaterShallow"` + `<temporary>true</temporary>`, no DLC gating), already pairs
every `SetTempTerrain` with a `QueueRemoveTerrain`
(`Source/Flood_FlowWorks.cs:310-311`), and its `About.xml` already states "No DLC required."
The two terrain models are unified on the D/F primitive under FLOWWORKS_BUILD_PROGRAM_1.
