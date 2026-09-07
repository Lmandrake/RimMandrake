## the ask

Owner, 2026-09-07: *"make those biomes look like ocean yet allow you to land
'underwater' with that ruleset... It can be a later modification to add
underwater biome support."*

Applies to `RUT_TheScald`, `RUT_GreySea`, `RUT_TwilightSea` (and
`RUT_PropaneLake`, painted nowhere yet).

## what is known, measured 2026-09-07

All four currently mirror vanilla `Ocean` exactly:

```
workerClass       BiomeWorker_Ocean
isWaterBiome      true
impassable        true      <- blocks landing/travel
canBuildBase      false     <- blocks settling
isBackgroundBiome true
allowRivers/Roads false
texture           World/Biomes/Ocean
```

## what is NOT known — do not start by flipping flags

⛔ `impassable: false` + `canBuildBase: true` are the obvious gates, **but that
is the easy half and probably not the answer.** With `isWaterBiome: true` the map
generator lays `waterDeepTerrain` / `waterShallowTerrain` across the map, so
landing would drop the player onto open water with no seafloor.

**Verify before designing:** how RimWorld chooses map terrain for a water biome
(`terrainsByFertility` is absent on all four — the land control has it), whether
`isBackgroundBiome` alone suppresses map generation, and what `BiomeWorker_Ocean`
does beyond world-gen placement.

🔑 **The likely shape of the answer is an INJECTED LAYER, not a biome flag.** The
closest working precedent in this repo is `LANTERN_DEEPS_INJECTION_1` — the
crystal caverns as an injected underground layer beneath qualifying maps. Read
that before proposing a biome-flag route.

## why it matters to the design

`the_grey_deep.md` and `the_twilight_deep.md` both describe sea BOTTOMS — the
statuary, the pillar forest, the ossuary shrimp, the mat-as-roof — as places.
Until this exists, that ground is unreachable by any route, and the standing
ruling defers the bottoms to "the diving mods".

## not blocking

The three seas' surfaces work as ocean today. This is additive.
