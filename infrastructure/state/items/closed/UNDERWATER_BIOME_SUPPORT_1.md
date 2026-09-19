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

## ⭐ THE MECHANISM ALREADY EXISTS AS A SUBSCRIBED MOD — found 2026-09-07

The owner recalled one; measured by scanning all **1341** installed `About.xml`:

**`gravtide.mod` — "GravTide"**, subscribed, currently **INACTIVE**.
Dependencies `Ludeon.RimWorld.Odyssey` + `brrainz.harmony`, both already active.
Folder: `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3779600989`

> *"Land your gravship on an ocean tile and dive for what is on the sea floor.
> Down and back, mostly, though **a base down there does work**. The surface half
> is its own: a shipyard on the beach, boats that sail the world map, and a
> platform on piles driven into the sea floor."*

It ships a full pressure model: 1 atm per 10 m; gear rated piece by piece with
the **shallowest piece deciding**; vacuum gear 20 m, drysuit+helmet 800,
hardsuit 1000, mechanoid casing 5000; past rating a piece stops sealing and its
wearer drowns in ~80 s; high-pressure nervous syndrome at ~150 m that no seal
answers — the hardsuit is a rigid shell at 1 atm, and past 1000 m it is mechs or
a rebuilt body.

🔑 **This is gravship-shaped, which is this campaign's spine.** Evaluate it before
building anything.

**Also found:** `oceanmodder.oceanbiome` — "Ocean Biome", subscribed, inactive:
a deep-sea biome with **underwater terrain generation steps** and marine flora.
The terrain-generation half is the piece our defs lack.

### 🔴 the crux question to answer FIRST
**Does GravTide dive on ANY water biome, or only vanilla `Ocean`?** If it keys off
`isWaterBiome` / `BiomeWorker_Ocean`, the three seas may already qualify — all
four of ours set both. If it hard-codes `BiomeDefOf.Ocean`, we need a patch, not
a new system. ⚠️ Read its assembly for the check (`strings -el` plus a decompile —
a clean ASCII sweep of a managed DLL proves nothing), and do not conclude from
its description.

## why it matters to the design

`the_grey_deep.md` and `the_twilight_deep.md` both describe sea BOTTOMS — the
statuary, the pillar forest, the ossuary shrimp, the mat-as-roof — as places.
Until this exists, that ground is unreachable by any route, and the standing
ruling defers the bottoms to "the diving mods".

## not blocking

The three seas' surfaces work as ocean today. This is additive.
