# SCALD_CROWNCARPET_NO_HABITAT_1 — shallow water band fix

Status: DONE — pushed to main at ca774b8b9

## Problem
MEASURED live: regenerated RM_TheScald map (250x250) has RUT_ScaldWaterOceanDeep
49,940 cells and ZERO RUT_ScaldWaterOceanShallow. Crowncarpet bed (on
RUT_ScaldWaterOceanShallow) has nowhere to spawn; plants = 1 anima tree.

## Investigation

This is a full water-biome floor map (RM_TheScald IS the map's own tile biome — the
GravTide sea-floor dive map, DivingInteraction/RM_SeaDiveGenerators.xml), not a
land-tile-adjacent-to-sea coast. `RM_TileMutatorWorker_SeaCoast` (SeaShores mod) only
runs for LAND tiles bordering a sea and is irrelevant to this map's own terrain.

Every cell of this map's terrain is laid by vanilla `GenStep_Terrain.Generate` ->
`MapGenUtility.GetNaturalTerrainAt` -> `TerrainFrom(cell, elevation, fertility)`
(RimSage-read `Source/RimWorld/MapGenUtility.cs`, `GenStep_Terrain.cs`). Order: (1)
`terrainPatchMakers` (none on this biome), (2) elevation bands 0.55-0.61 -> Gravel,
>=0.61 -> rock (explains the MEASURED Gravel/Marble_Rough/Granite_Rough cells — real
elevation-driven rock outcrops), (3) fallback:
`TerrainThreshold.TerrainAtValue(biomeDef.terrainsByFertility, fertility)`, first
`[min,max]` band containing the per-cell fertility value wins
(`Source/RimWorld/TerrainThreshold.cs`).

`RM_TheScald.xml`'s `terrainsByFertility` had exactly ONE band,
`RUT_ScaldWaterOceanDeep` spanning -999..999 — so every non-rock cell got Deep,
unconditionally. `RUT_ScaldWaterOceanShallow` already carries the `RM_CrowncarpetBed`
tag (`RUT_ScaldWater.xml`, added by the earlier fix `333afaf82`) but could never be
selected because nothing ever asked for a fertility value in any other range.

Fertility itself comes from `GenStep_ElevationFertility.Generate` as an INDEPENDENT
Perlin field (freq 0.021, 6 octaves, `ScaleBias(0.5,0.5)`) — a totally separate noise
module from the elevation field that produces the rock outcrops (RimSage-read,
confirmed no shared input). So a fertility-band split cannot hug the rock the way a
literal "ring around the land" would; it produces an irregular but real NOISE PATCH of
shallow across the floor. A literal adjacency-based shoreline (shallow cells only where
a deep cell orthogonally touches rock/gravel) would need a new post-terrain GenStep in
C# — flagged below, not built (out of this item's offline XML-only scope).

Checked GravTide's own donor patterns for comparison (workshop id 3779600989,
`Patches/Biomes_Ocean.xml` for vanilla Ocean/Lake, `Defs/BiomeDefs/Biomes_Seabed.xml`
for its own seabed biomes): BOTH use the exact same single-band
`terrainsByFertility` (one terrain, -999..999) per zone/biome. GravTide's real floor
variety comes from a separate custom `GenStep_Seabed` ("paints the real mix over the
top" — the seabed doc's own words), not from fertility bands at all. So the whole
`RM_`/`RUT_` terminal-seas family (GreySea, TwilightSea, PropaneLake, Scald) inherited
a single-band placeholder that was never meant to be the final depth mechanism —
informational, not fixed here (out of this item's scope; the other three seas carry
the identical defect and would need the identical two-line fix if the owner wants it).

## Fix

`src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_TheScald.xml` — split the single
`terrainsByFertility` band into two, deep-first (order matters, first match wins):

```xml
<li><terrain>RUT_ScaldWaterOceanDeep</terrain><min>-999</min><max>0.6</max></li>
<li><terrain>RUT_ScaldWaterOceanShallow</terrain><min>0.6</min><max>999</max></li>
```

`RUT_ScaldWaterOceanShallow` already carries `RM_CrowncarpetBed` in
`RUT_ScaldWater.xml` — no terrain-def edit needed, this is the whole fix.
`RUT_TheScald.xml` (the frozen save-compat twin) is untouched per its own header
("every CONTENT fix... lands in mandrake.rm.terminalbiomes only, never here").

## Snow finding (VEE_DenseSnow_Rough) — NOT fixed, donor-side

`VEE_` is the "Vanilla Expanded" family prefix (Vanilla Events/Landmarks/Weather
Expanded etc, confirmed against this repo's own `design/Jawa/art/SALVAGE_PALETTE.md`
and `forbidden_mods.md` VEE_ examples). Grepped both the GravTide workshop folder and
the deployed `.../RimWorld/Mods` tree for the literal defName `VEE_DenseSnow_Rough` —
absent from both (UNMEASURED which exact mod owns it; a full workshop-wide grep is too
slow to run in this pass, per this repo's own "C: is slow" note). Vanilla itself has
no such TerrainDef — vanilla snow is a `SnowGrid` DEPTH overlay on existing terrain
(`GenStep_Snow`, `Plant.cs`/`GridsUtility.GetSnowDepth`), never a distinct "X_Rough"
terrain swap. That shape (a distinct terrain variant, not a depth overlay) matches a
world-tile LANDMARK's own `TileMutatorWorker` laying ground cover independent of the
host biome — the same mechanism family as our own `RM_SeaCoast`/
`RM_TileMutatorWorker_SeaCoast`.

Most likely explanation, stated as a hypothesis (not MEASURED): the 250x250 map the
coordinator regenerated was generated on a DEBUG/dev-mode tile rather than the Scald's
real, hand-authored, hot-latitude world tile, and a donor Landmark/TileMutator
assigned to that tile lays `VEE_DenseSnow_Rough` onto the rock/gravel cells regardless
of the biome's own heat. `RM_SunHeatExtension`'s `heatOffsetC 15 / ambient` on
`RM_TheScald` is a RUNTIME pawn-heat-exposure mechanic (affects hediffs/comfort), not
a worldgen input — it does nothing to the map's seeded outdoor temperature or to
whatever gate the donor snow terrain reads, so it cannot be why the snow appeared and
would not prevent it either. This is donor content (a landmark/mutator on the test
tile, or possibly a temperature-gated GenStep in a VEE mod) — not touched here per the
brief.

## Verify

- `python3 -c "import xml.etree.ElementTree as ET; ET.parse('src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_TheScald.xml')"` — OK.
- `python3 src/RimMandrake/Utils/run_selftests.py` — **77/79 passed**, 2 skipped
  (human-driven art check; a lupa-dependent package test), 1 UNMEASURED
  (`selftest_tool_metadata.py` — needs the Windows-side .NET SDK for a local
  bridgetools build; irrelevant here, this fix is XML-only, no C#), 1 FAILED
  (`selftest_deployed_biome_refs.py`, 19 dangling deployed refs — all
  `RUT_TheRot`/`RUT_WeepingStones` `wildPlants` rows needing
  `mandrake.rut.rotsporekit`; ZERO mention of Scald or Crowncarpet anywhere in
  its output — pre-existing and unrelated to this change, not caused by it).
- No C# touched, no DLL/`.srchash` to rebuild — this fix is a single BiomeDef
  field edit.

## Expected outcome for coordinator's live check

Regenerating the RM_TheScald map and running `terrain_census.py` should now show:
- `RUT_ScaldWaterOceanShallow` > 0 (previously 0) — expect roughly **20-35% of
  non-rock water cells**, `RUT_ScaldWaterOceanDeep` the remaining ~65-80% majority.
  This is an ESTIMATE from the fertility noise's typical range around its 0.5 center,
  not a live measurement (no bridge in this offline worktree) — the live regen is the
  real instrument.
- Plant count should rise well above 1 (crowncarpet, `plantDensity 0.3`, now has real
  `RUT_ScaldWaterOceanShallow` cells carrying its `RM_CrowncarpetBed` wildTerrainTag to
  spawn on).
- Gravel/Marble_Rough/Granite_Rough/VEE_DenseSnow_Rough counts should be materially
  unchanged (elevation-driven, untouched by this fix).
