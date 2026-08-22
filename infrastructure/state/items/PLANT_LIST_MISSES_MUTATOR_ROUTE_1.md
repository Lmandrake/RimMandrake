## spec
🔴 **The plant candidate list is built from `BiomeDef.wildPlants` ONLY, and that is not the
only route a plant reaches a map.** `TileMutatorDef.additionalWildPlants[].plant` and
`TileMutatorDef.plantKinds[]` add flora irrespective of biome, and the builder never reads
them.

**Measured 2026-08-22** across the 74 mutators actually present in
`world/ASHKARR_WORLDMAP_mutators.csv`:

| mutator | tiles | plants it adds | already in the list? |
|---|---|---|---|
| `Oasis` | 209 | `Plant_TreePalm`, `Plant_RatPalm`, `Plant_Grass`, `Plant_GrayGrass`, `Plant_Reeds` | ✅ all five, **by coincidence** — they also appear in `ZBiome_DesertOasis` |
| `VEE_RedDesertPlants` | 8 | `VEE_Plant_ChollaCactus`, `VEE_Plant_HoodiaCactus` | 🔴 **neither** |

⇒ **Two plants were missing, and the coincidence on the other five is the warning.** The
route is unread; today it costs 2 rows, and it would cost more the moment a mutator changes.

✅ **Already repaired by hand:** both cacti were appended to
`design/Jawa/mods/plant_cherrypick_candidates.csv` (now **192** rows) with their measured
fields from the live dump — `treeCategory: Full`, `harvestedThingDef: WoodLog`,
`growDays: 5`, `Vanilla Landmarks Expanded` — and the 8 tiles they reach are
**ExtremeDesert ×6, Desert ×2**, so they land in the core-desert group. **The BUILDER is
still wrong; only its output was patched.**

## what to change
Union, over the mutator set in `world/ASHKARR_WORLDMAP_mutators.csv`, each
`TileMutatorDef`'s `additionalWildPlants[].plant` and `plantKinds[]`, attributing tiles by
**mutator count** rather than biome count. Dedup against the biome-derived rows.

## routes CHECKED AND CLEAR — do not re-investigate these
- No `BiomeVariantDef` on this planet touches plants (all 6 are Biomes! Caverns, layers only).
- No `extraGenSteps` on any planet mutator places flora (Sarlacc pits, cenotes, flesh pits,
  sulfur vents, ancient structures).
- Landmarks resolve to the same mutator set.
- `src/Jawa/` patches touch `terrainPatchMakers` and `baseWeatherCommonalities`, never `wildPlants`.
- **There is no terrain-keyed spawn route.** `wildTerrainTags`, `terrainBlacklist` and
  `wildPlantUseDistanceToShore` only *restrict* placement of plants already in the biome
  list — they never add one.
- Mutator `plantDensityFactor` shifts amount, not roster (`Dunes` 0, `VEE_PlantLife_Overgrown` ×4).

## verify
Re-derive the list and confirm it is a strict superset of today's 192, with every added row
attributable to a named mutator on Ash'karr.

## criteria
The builder reads both routes; the two VEE cacti appear without hand-patching.

## watch out
⚠️ **The dump nests plant fields under `fields`, not at the top level.** Reading
`thingDef['plant']['growDays']` returns `null` for **every** plant including vanilla
Saguaro, which looks like missing data and is a parse error. It is
`thingDef['fields']['plant']['growDays']`.
⚠️ Sprites do not exist for the two new rows; they render "no art" in the sheet.
