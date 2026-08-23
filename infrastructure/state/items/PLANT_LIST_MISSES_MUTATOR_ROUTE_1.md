## ✅ FIXED 2026-08-23 — and the builder did not exist at all

**`design/Jawa/mods/gen_plant_candidates.py`** now builds the list from both routes.

🔴 **The item says *"the BUILDER is still wrong; only its output was patched"*. It was
worse than that: there was no builder.** The CSV was produced ad hoc when
`PLANT_CHERRYPICK_PASS_1` was filed (`43e2913f`) and no script writing it existed anywhere
in the repo — `gen_plant_sheet.py`, `plant_harvest_coverage.py` and `plant_walk_list.py`
all only READ it. The candidate list was an orphan artifact, hand-patched twice.

## ⭐ The verification is exact

```
MEASURED 192 reachable plants over 28 biomes and 74 mutators
  by biome only: 185 · both: 5 · 🔴 MUTATOR ONLY: 2
     VEE_Plant_ChollaCactus   8 tiles via VEE_RedDesertPlants
     VEE_Plant_HoodiaCactus   8 tiles via VEE_RedDesertPlants
  vs the hand-patched CSV: +0 / -0
```

**The builder reproduces the hand-patched list exactly** — same 192 rows, and it finds the
two cacti on its own instead of needing them appended. That is this item's stated verify
(*"a strict superset of today's 192, every added row attributable to a named mutator"*)
met at equality, which is the strongest form of it.

🔑 **The 5 both-route plants are the warning the item named.** `Oasis` adds five plants that
were already in the list *by coincidence* — they also grow in `ZBiome_DesertOasis`. A
biome-only scan would keep looking correct until a mutator changed.

## 🔴 It also repaired a gap NOT in this item, and the numbers moved

The old CSV predated `HorrorWastes` having any tiles, so the plant pass had never seen it.
DECIDE told the owner on 2026-08-22 that HorrorWastes *"has no plant at all"* — that came
from the stale CSV. **The biome has exactly one: `Plant_Agave`.**

| | before | after |
|---|---|---|
| biomes carrying flora | 23 | **24** |
| biomes with NO wood | 2 | **3** — `HorrorWastes` joins `AB_PropaneLakes`, `BMT_CrystalCaverns` |
| sole-source biome-resource pairs | 57 | **58** |
| rows whose reach changed | — | **46 of 192** |

⚠️ `Plant_Agave` gained **913 tiles** (10,089 → 11,002). The other 45 moved because of the
2026-08-23 coast pass and the warm-crags transfer, not because of this fix.

🔑 **`HorrorWastes`: 807 tiles, one plant, no wood.** The coverage report now says so on its
own. That is the shell defect already filed under `HORROR_WASTES_ON_NIGHTSIDE_1`; the
instrument can see it now instead of reporting the biome as absent.

✅ **Downstream regenerated and consistent:** `plant_review.html` (192 rows, JS lints, the
owner's 4 cuts merge untouched), `plant_harvest_coverage.md`, `plant_walk_list.md`.
`--against-decisions` still reports the two accepted losses and nothing new.

---

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
