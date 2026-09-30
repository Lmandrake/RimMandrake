# BLUEDESERT_ZERO_PLANTS_1 report (2026-09-30)

Evidence: `Transient/quicktest_biomes_2026-09-30{,b,c}.json` (main tree), the live
`Player.log` (run c, tile 57231), decompiled 1.6 engine via RimSage, ReGrowthCore.dll
decompiled with ilspycmd, donor Biomes! Polluted Lands source (workshop 3390196656).

## 1. Blue Desert 0 plants / Scald 1 plant: the test tile, not a defect

**Blue Desert.** None of tonight's commits touched the Blue Desert flora.
`RM_BlueDesertFlora.xml` last changed at `6a843cdd6` (09-29 08:00). `044381748`
touched only the fauna file (one tool group). 47f6c74a0/136d7c228/546d14da6 touch no
Blue Desert file. All four plants still derive from `PlantBase`.

The gate that rejects them is `PlantUtility.CanEverPlantAt(..., checkMapTemperature: true)`,
which `WildPlantSpawner.CalculatePlantsWhichCanGrowAt` calls for every wild plant during
`GenStep_Plants`:

    if (checkMapTemperature && (map.TileInfo.MinTemperature > plant.maxGrowthTemperature || ...)) return false;

All four natives are authored with `maxGrowthTemperature -1` (cold-stable fuel charges).
So on any tile whose **annual minimum** stays above -1 °C, every native plant is
rejected. That empties the candidate list, and `CheckSpawnWildPlantAt` returns false on
every cell, with no log line. Fertility is not the cause: Ice has fertility 0, but all
four set `completelyIgnoreFertility`, so `HaveAnyPlantsWhichIgnoreFertility` bypasses the
fertility check. `plantDensity` is 0.33 and no mutator or condition zeroes the density
factor.

The harness keeps the debug tile's climate (`prove_biome_quicktest.py` sets only the biome;
`temp` in the JSON is `outdoorTempNow`, not the tile's annual range). Run a (200 plants) and
runs b and c (0 plants) are consistent with different tiles or seasons on either side of
that -1 °C annual minimum. Run b's `outdoorTempNow` was 21 °C, so that tile's minimum is
very likely above -1. The run-a tile is UNMEASURED: its log was overwritten.

Second trap, even when plants do spawn: `CompPlantCharge` kills each plant after two
consecutive long ticks above `warmDetonationThresholdC` (default **5 °C**). Run a (6.05 °C)
and run c (5.48 °C) are both above it, so any plants would have detonated within about 66 s
of game time.

**A fair Blue Desert tile:** annual minimum ≤ -1 °C (required for mapgen), and outdoor
temperature ≤ 5 °C when counting (so the plants survive). Ideally use the biome's real
climate: sheet §0 gives a median of -42.6 °C, a range of -58 to -19.4 °C, and a summer
maximum below 0 on every tile. Set the test tile's temperature to about -30 °C.

**Scald.** `RM_TheScald` is an ocean biome (`BiomeWorker_Ocean`, impassable, background).
Its only wild plant, `RM_Crowncarpet`, has `wildTerrainTags` of `RM_CrowncarpetBed` and
`RUT_ScaldMarginMat`. Those tags exist only on vanilla `WaterOceanShallow` (patched) and
`RUT_ScaldMargin`. Mapgen lays neither on a Scald map (its terrain is
`RUT_ScaldWaterOceanDeep`), and the margin ring is an authored placement. So 0 crowncarpet
on a regenerated Scald map is expected. The 1 plant counted was `Plant_TreeAnima`, placed by
something else. A fair Scald test is a coastal land tile beside the Scald, or a map with the
margin ring authored.

## 2. RSW_ToxinDependence: fixed

The BMT_FAUNA_ABSORPTION_1 port dropped the donor classes
`BMT_PollutedLands.Need_ToxinDependence` and `Hediff_ToxinDependence`, which left
`needClass` null. Every norphea then threw in `Pawn_NeedsTracker.AddNeed`, and the need
never existed, so the hediff sat inert.

I rebuilt both from the donor's shipped source as `RSW_Need_ToxinDependence` and
`RSW_Hediff_ToxinDependence` in
`src/RimStarWars/SWBestiary/Source/BeastMechanics/ToxinDependence.cs`:
- **Need:** rises by 0.0001 per tick while the pawn has ToxicBuildup or stands on a
  polluted cell, and falls at `fallPerDay` otherwise.
- **Hediff:** stage 1 ("unmet", lethal MTB) only while the need is in Withdrawal.

I did not use vanilla `Need_Chemical`: it only ever falls, so every wild norphea would
starve into the lethal stage with nothing on the map able to refill it. A new Mod Setting,
"Toxin-dependent creatures" (default on), holds the need full when switched off. The
NeedDef and HediffDef now name the two classes.

## 3. ReGrowth `RecolorMineables` NRE: not pinned to our defs (donor-side until probed)

Decompiled (`ReGrowthCore.Map_FinalizeInit_Patch.ProcessMap`). It collects every
`Mineable` whose `def.building.isResourceRock` is set and whose graphic is Linked into
"lumps", then in `RecolorMineables` runs:

    GraphicData data = building.Graphic.data;
    GraphicDatabase.Get(data.graphicClass, data.texPath, ...)

The NRE is therefore a resource-rock lump whose runtime `Graphic.data` is null.

I checked all 26 of our `isResourceRock` ThingDefs:
- Every one has vanilla graphic classes and a texture that exists (in its own mod or
  vanilla `RockFlecked_Atlas`), or inherits RockBase's graphic.
- None appears in tonight's "Could not load Texture2D" list.
- No Harmony patch of ours touches `Thing.Graphic` or `Mineable` graphics.

Nothing in our XML explains a null `Graphic.data`. The next step is one live probe: for each
spawned `Mineable` with `isResourceRock` and a Linked graphic, print defName, packageId and
whether `Graphic.data == null`. The offender is most likely on every map through
`mineableScatterCommonality > 0`. Ours with that are `DV_MineablePyrinth` (0.1) and
`RUT_Webwork_SilkKnot` (0.6); otherwise it is a donor mod's rock. The exception fires after
mapgen, in a queued long event, and only skips recolouring, so it does not affect plants or
gameplay.
