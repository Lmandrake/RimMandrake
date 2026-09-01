<!-- status: live -->
# Populating Ash'karr — what exists, what fits, and what cannot fire

**Census run 2026-08-20, the day the map was accepted for v1.** The shape of the planet is
settled; this is the inventory for the layer that has never been authored.

🔴 **The world bundle carries no mutator column and no landmark column at all.** Its
per-tile CSV is `tile,lat,lon,arc,bearing,elev_m,temp_c,rain_mm,biome,water,river_flow,region,hilliness,swampiness`.
Mutators and landmarks are not *missing from the map* — nobody has authored them.

Full rows, committed rather than left in a scratchpad:
`world/census/mutators.tsv` (335) · `world/census/landmarks.tsv` (112).

## The counts

**336 TileMutatorDefs** across nine active mods — Core 5 · Odyssey 82 · Vanilla Landmarks
Expanded 144 · Alpha Biomes 48 · Geological Landforms 44 · SW Animal Collection 9 ·
Dark Ages 2 · Map Designer 1 · Biome Transitions 1. **113 LandmarkDefs.**

| | mutators | landmarks |
|---|---|---|
| ✅ fits a hot, dry, tidally-locked desert | **218** | **69** |
| ⚠️ depends — needs a whitelist entry or a relabel | 23 | 10 |
| 🌙 nightside only | 14 (**only 4 placeable today**) | 0 |
| ⛔ wrong planet | 81 | 34 |

🔴 **44 mutators and 22 landmarks are not merely wrong — they are MECHANICALLY UNPLACEABLE.**
Their `biomeWhitelist` names no biome in Ash'karr's 24-biome palette, or their
`averageTemperatureRange` excludes all 21,872 tiles. ⚠️ **A def that cannot fire logs
nothing** — naming one in a placement plan produces silence, not an error.

## ⭐ The oasis answer

You have **227 tiles of oasis already** (`ZBiome_DesertOasis`, 1.04%). The other three
mechanisms do genuinely different work — and one of them cannot currently reach those tiles.

| mechanism | what it does in play | verdict |
|---|---|---|
| **`ZBiome_DesertOasis`** biome — **painted, 227 tiles** | changes the WORLD TILE: animalDensity 1.5, plantDensity 0.70, regrow 17 days (vs Desert 0.4 / 0.45 / 35), allows Elephant pack animals. Every map rolled there is green, and it shows on the globe | **in use, load-bearing** |
| **`Oasis` TileMutatorDef** (Odyssey) | a LOCAL-MAP generator — `TileMutatorWorker_Oasis` carves a spring of fresh water and injects `Plant_TreePalm`, `Plant_RatPalm`, `Plant_Grass`, `Plant_GrayGrass`, `Plant_Reeds` | **complementary, and BLOCKED — see below** |
| **`Oasis` LandmarkDef** + `NamerLandmark_Oasis` | the named-place wrapper: forces the mutator, rolls `AnimalLife_Increased` 75% / `AnimalHabitat` 25% / `AncientUplink` 2%, draws the globe icon, names it | **the player-facing half.** Use on a handful, not 227 — a named place stops being a place when there are 227 |
| **`GL_Oasis`** (Geological Landforms) | a different, larger terrain layout — sand rings, water body, natural rock. Inland only, no river, commonness 2.5% | **redundant with the Odyssey mutator, not with the biome.** Both are `Groundwater` map generators and will fight. Pick one |

🔴 **THE BLOCKER, verified in the shipped XML** —
`Data/Odyssey/Defs/TileMutators/TileMutators_Natural.xml`:

```
<defName>Oasis</defName>
<biomeWhitelist>['Desert', 'ExtremeDesert']</biomeWhitelist>
<averageTemperatureRange>20~60</averageTemperatureRange>
<canSpawnOnRiver>false</canSpawnOnRiver>
```

⇒ **`ZBiome_DesertOasis` is not in the whitelist, so the oasis mutator cannot roll on our
227 oasis tiles as shipped.** A one-line `PatchOperationAdd` fixes it. ⚠️ The 227 span
16–62 °C, so a few also fall outside the 20–60 gate.

⚠️ **And the 227 have zero rivers, zero water tiles and zero landmarks.** They are lush
biome paint with no water feature underneath.

⛔ `BiomeArcticOasis` and `GL_IceOasis` are wrong for this planet. `BMT_ChromaticOasis`
(Biomes! Oasis) is **not installed**.

## 🔴 49 leftover landmarks must be cleared before anything is authored

**Verified: exactly 49 landmark tiles in `WORLDMAP_gen.rws` AND 49 in
`WORLDMAP_sub7b_source.rws`.** They are vanilla worldgen leftovers that nobody authored,
and they no longer match the repainted biomes:

`Bay` ×3 · `AB_PropaneLakes` ×3 · `VEE_JaggedRocks` ×2 · `Chasm` ×2 · `Cavern` ×2 ·
`VEE_DriftwoodShore` ×2 · `Lake` ×2 · `Wetland` ×2 · `Cove` · `ToxicLake` · `VEE_CoralReef` ·
`VEE_AlluvialFan` · `VEE_CraterLake` · …

⚠️ **A coral reef and a driftwood shore on a world that is 8.14% water and has no forest
upstream.** These are the first thing to clear, not the last.

## Duplication risks — the map already names these places

| proposed | already is | tiles |
|---|---|---|
| `Lake` / `Lakeshore` / `Pond` landmark | **The Scald** — painted `Lake`, and it is a named sea | 312 |
| `Dunes` mutator or landmark | **The Dune Sea** | 1,725 |
| `VEE_SaltPlains` / `VEE_DustBowl` | **The Salt**, **The Ammonia Flats** | — |
| `VEE_Volcano` / `LavaFlow` | **The Ashteeth**, **The Ashfall Range** | — |

## Why the ⛔ calls — the planet has no seasons and does not rotate

| reason | examples |
|---|---|
| needs seasons | `VEE_FloodPlains`, `VEE_AuburnTree_*`, `VEE_FertileRains` |
| needs a tidal cycle | `VEE_RisingWaters`, `VEE_StrongerTides` — a locked world has a static bulge |
| needs forests | `VEE_LaurelForest`, `VEE_BurnedForest`, `VEE_DriftwoodShore`, `ArcheanTrees` |
| needs rain | `WetClimate`, `Wetland`, `Marshy`, `VEE_Mangrove`, `Pond` |
| needs ice caps | `Iceberg`, `Crevasse`, `VEE_IceSpires`, `VEE_PermafrostBasin` |

🌙 **Nightside: only 4 of 14 are placeable** — `IceCaves`, `AB_BlizzariskNest`,
`AB_AncientFreezingVent`, `VEE_FrequentAuroras`. The other ten are blocked because **the
deep night has no cold biome painted**: arc 120°+ is `AB_RockyCrags` (3,254),
`AB_MycoticJungle` (698) and `AB_PropaneLakes` (554) at −22 to −80 °C.

🔑 **`AB_PropaneLakes` is painted as a BIOME on 554 tiles, but its own MUTATOR whitelists
only IceSheet / SeaIce / GlacialPlain — it cannot roll on its own biome.** That is the
shape of the whole nightside problem in one def.

## Temperature levers we are not using

| lever | note |
|---|---|
| **`BiomeDef.constantOutdoorTemperature`** | pins a biome to one temperature, ignoring tile and season. ⭐ **On a world with no seasons this is the most powerful lever available.** Used today only by `Space`/`Orbit` (−75) and three Biomes! Caverns biomes |
| `BiomeDef.biomeMapConditions` | permanent GameConditions per biome — `Glowforest`→`DarkenedSkies`, `AB_PyroclasticConflagration`→`AB_VolcanicHeatWave`. A nightside biome could carry permanent darkness this way |
| `TileMutatorDef.additionalGameConditions` | attaches a condition to every map on that tile |
| worker-class mutators | `AncientHeatVent` raises map temperature, `AB_AncientFreezingVent` lowers it — C#, values not in the dump |
| per-tile `temperature` in the save | already authored per tile; directly writable |

⚠️ **`GameConditionDef.temperatureOffset` reads −10 for all 89 defs in the dump. That is a
dump default, not a real per-def value — do not use those numbers.** Another entry for the
def-dump blind-spot list.

## What this census deliberately does NOT do

⛔ **No placement plan.** The owner scoped populating the map, not a specific layout, and
choosing which of 218 fitting mutators go where is design, not inventory.
