# TERRITORY_ROAD_WEIGHTED_SCALE_1 — faction territories: bigger, road-weighted

Filed 2026-08-30, FOUNDRY, live chat request after the owner saw Ash'karr territory
screenshots: **"Can we make the territories bigger? ... Even cooler if they could bleed
more along roads than out into open desert."**

## The mod, and the finding that changed the plan
"Faction Territories and Vassalage" (jaeger972.factionterritories, Steam Workshop
`3626725895`) is a world-map VIEW MODE registered with `NozoMe.MapModeFramework`
(`3296654393`, ships its own `Source/` — read directly, no decompile needed for the
framework). FactionTerritories itself ships no `Source/`, so its
`Assemblies/FactionTerritories.dll` was decompiled with `ilspycmd` (Windows-side tool at
`C:\Users\Mandrake\.dotnet\tools\ilspycmd.exe`, 9.0.0.7889 — the same install the
`SWCP_CHARACTERS_DECOMPILE_1` item used) into
`D:\Luke\dev\Rimworld\vendor\mod_sources\FactionTerritories_decompiled\` (gitignored,
derived, regenerable).

**The expected work — a Harmony patch substituting a road-weighted cost-distance
calculation into the region-growing algorithm — was already unnecessary.** Reading
`TerritoryOwnershipCache.cs` and `FactionTerritoriesUtility.cs` confirms the mod already
computes territory as a genuine multi-source Dijkstra cost-distance flood fill from every
settlement (a min-heap over `WorldGrid` tiles), where the per-edge step cost
(`EdgeMovementDifficultyNoWinter`) is real vanilla `BiomeDef.movementDifficulty` for the
base cost, times `WorldGrid.GetRoadMovementDifficultyMultiplier(fromTile, toTile, null)` —
RimWorld's own vanilla world-pathfinding API, exactly the one this item expected to have
to reinvent — for the road discount. Both terms, and the base radius, are already exposed
as `ModSettings` (`FactionTerritoriesSettings.cs`):
- `radiusSteps` (mod default 5, live file had 4) — "bigger"
- `variationSteps` — ± noise so edges aren't a perfect circle
- `roadMovementDifficultyPercent` (default 100 = exact vanilla multiplier; clamp 0-200) —
  above 100 the mod EXTRAPOLATES past the vanilla multiplier (`Lerp(1, mult, pct/100)`),
  so at 200 a road tile's cost approaches zero relative to full-price desert — exactly
  "bleed along roads, not open desert"
- `impassableHillinessOffset` (default 10) — extra cost on impassable hills
- `settlementUncontestedRange` — guaranteed ring around each base

One field, `terrainDifficultyImpactPercent`, is drawn in the mod's own settings UI, saved,
and hashed into the cache-invalidation key, but is **never read** by
`TileBaseMovementDifficulty`/`EdgeMovementDifficultyNoWinter`/`ComputeStepCostScaled` — a
dead setting in the shipped mod itself, unrelated to anything built here.

## What was built
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchFactionTerritoryTools.cs` —
one new tool, `jawa/faction_territory_settings`, reflection-only (the mod is a Workshop
dependency, not a build-time reference, same discipline as `JawaBenchMapModeTools.cs` for
MapModeFramework). Reads or writes `FactionTerritoriesMod.Instance.Settings`' fields,
persists via the mod's own `Settings.Write()` — the SAME
`Config\Mod_3626725895_FactionTerritoriesMod.xml` the in-game Mod Settings window writes,
so a change made through the bridge is exactly as durable as one the owner makes by hand —
and live-refreshes via the mod's own `FactionTerritoriesUtility.RequestRegenerate(clearCache:
true)`, the same path its settings window and its own `WriteSettings()` override call. No
Harmony patch, no new algorithm: this only reaches the knobs the mod's author already
built and wired to real vanilla data.

## spec
1. Confirm the settings ARE live-settable without a restart (WriteSettings ->
   RequestRegenerate is the mod's own hot-reload path) — read-back the object, not just
   the XML.
2. Raise `radiusSteps` (owner: "bigger") and `roadMovementDifficultyPercent` toward its
   200 ceiling (owner: "bleed more along roads than into open desert").
3. Switch to the `FactionTerritories` map mode (`jawa/world_map_mode`) and screenshot
   before/after to `Transient/`.

## verify
- [ ] `jawa/faction_territory_settings` builds clean (0 warnings/errors,
      `dotnet build -c Release`), no duplicate `jawa/` alias, passes `build.py --gm`
      plan-only tool-surface check.
- [ ] Deployed live; tool appears in `--list-tools`; a settings write is proven to persist
      to `Config\Mod_3626725895_FactionTerritoriesMod.xml` AND take visible effect without
      a second restart (read-back after `RequestRegenerate`, then a screenshot).
- [ ] Before/after screenshots at `Transient/` showing territories larger and visibly
      elongated along roads rather than uniformly circular into open desert.

## criteria
- [x] Existing settings checked first, before any patch was written — this closed the
      item's original Harmony-patch plan entirely.
- [x] Algorithm read from the mod's own decompiled source, not guessed; confirmed it
      reuses vanilla's own road-movement-difficulty API rather than reinventing "what
      counts as a road."
- [ ] Live-proven: values changed, persisted, regenerated, and photographed against the
      currently-loading game session (mods still constructing as of this write —
      `jaeger972.factionterritories` had not yet resolved on the bridge; owed once the
      load finishes).

--- history ---
