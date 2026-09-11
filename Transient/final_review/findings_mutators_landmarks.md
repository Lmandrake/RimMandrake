# WORLDMAP_FINAL_REVIEW_1 Phase 1 — mutators + landmarks audit (MEASURED)

Read-only. Sources: `world_mutators.json` (14,400 tiles-with-mutators of 21,872 total),
`world_landmarks.json` (3,414 landmarks), `world_mutators_audit.json` (in-engine audit),
`world_tiles_live.csv` (21,872 tiles, biome/hilliness/elevation), `world_objects.json`
(196 world objects, 96 settlements). Def-space cross-check: offline `TileMutatorDef.json`
(409 defs) / `LandmarkDef.json` (137 defs) from capture `2026-09-11T11-07-06Z` — same day
as the live exports but not byte-fingerprint-matched to them; treat def-space counts as
close but not certified-identical to the mod set that produced the tile data.

---

## MUTATORS

### Density per biome (mutator instances / total tiles in biome)
Top 10 of 29 biomes, full table computed:

| biome | tiles | mutator instances | density | distinct defs |
|---|---|---|---|---|
| AB_MechanoidIntrusion | 236 | 1365 | 5.78 | 40 |
| COMIGO_GreaterSwamp_Tropical | 43 | 245 | 5.70 | 18 |
| Volcano | 5 | 25 | 5.00 | 10 |
| BiomeCypreJungle | 235 | 936 | 3.98 | 49 |
| AB_PyroclasticConflagration | 31 | 105 | 3.39 | 17 |
| LavaField | 8 | 27 | 3.38 | 10 |
| AB_MiasmicMangrove | 93 | 294 | 3.16 | 35 |
| AB_OcularForest | 179 | 562 | 3.14 | 41 |
| AB_FeraliskInfestedJungle | 161 | 448 | 2.78 | 36 |
| ZBiome_DesertOasis | 223 | 489 | 2.19 | 43 |

Lowest: RUT_TwilightSea (0.42), AB_GelatinousSuperorganism (0.55), AB_TarPits (0.63),
Wasteland (0.68), Desert (0.70) — the four common desert/sea biomes that carry most of
the map's tile count sit at the bottom of density, which is expected (small exotic
biomes get mutator-dense treatment).

### Variety per biome (distinct TileMutatorDefs seen)
Highest: ZBiome_Badlands (77 distinct defs across 970 tiles), AridShrubland (61/628),
ExtremeDesert (53/3969), BiomeCypreJungle (49/235), ZBiome_DesertOasis (43/223).
No biome shows fewer than 9 distinct defs (RUT_TheScald, 312 tiles).

### Gate violations
**Coast** — the engine's own `world_mutators_audit.json` reports `offenderCount: 104`
(Coast mutator on a tile with `waterCovered: false`) but its `offenders` array is
silently truncated to 30 rows despite `ResultWasTruncated: false`. Recomputed directly
from `world_mutators.json`: **all 104 tiles bearing the Coast mutator have `waterCovered:
false`** — the audit's count is confirmed and its list is now complete. By biome:
Wasteland 32, AridShrubland 32, ZBiome_Badlands 21, Desert 11, ZBiome_DesertOasis 4,
PoisonForest 2, AB_MiasmicMangrove 2. Full 104 tile IDs recovered; first 15: 36, 81, 269,
448, 707, 2234, 2236, 2607, 2917, 2919, 2920, 3221, 3224, 3226, 3869.
Side finding: `isCoastal` is `false` on **all 14,400** tiles in this export (0 tiles
true) — that field is not populated/reliable in this data source; `waterCovered` is the
only trustworthy coastal proxy here (678/14,400 true).

**Hilliness** — not checked by the engine audit at all (its `marineChecked` names only
`["Coast"]`). Cross-checked independently against `minHilliness`/`maxHilliness` on all
47 hilliness-gated TileMutatorDefs. **153 violations** (mutator on a tile whose
hilliness falls outside its declared range):
- Cliffs (requires ≥Mountainous): 43 violations — e.g. tiles 290, 923, 924 (LargeHills,
  ZBiome_Badlands), 2015 (Flat, BiomeCypreJungle)
- InsectMegahive (requires ≥Mountainous): 28 — e.g. tiles 890, 3468, 3470 (Flat,
  swamp/mangrove biomes)
- Hollow (requires ≥Mountainous): 19 — e.g. tiles 32, 494, 3063 (Flat)
- VEE_SerpentineCanyons (requires ≥Mountainous): 14
- AncientQuarry (requires ≥Mountainous): 10 — all on LargeHills, one step short
- Cavern (9), VEE_StagnantRivulet (9, above-max Flat), Chasm (9), Valley (5),
  VEE_FloodPlains (3, above-max Flat), HotSprings (2), Junkyard (2, above-max SmallHills)

**River** — UNMEASURED. `world_tiles_live.csv` carries no river/riverDist column, and
`world_mutators.json` tiles carry no river flag, so a River-mutator gate check (165
placed instances) cannot be derived from this export. Would need a live
`jawa/world_tiles` river field or `jawa/world_rivers` export.

### Stacking extremes (top 10 by mutator count on one tile)
| tile | biome | count | notable |
|---|---|---|---|
| 69 | AB_MechanoidIntrusion | 12 | AncientWarehouse+AncientRuins+3×Ancient*+Pollution_Increased |
| 3214 | ExtremeDesert | 11 | duplicate VEE_RedDesert / VEE_Cactus_Barrel entries (same def twice) |
| 2837 | AB_MechanoidIntrusion | 10 | |
| 3678 | ExtremeDesert | 10 | duplicate VEE_RedDesert / cacti again |
| 3995, 6493, 14595, 21523, 21568 | AB_MechanoidIntrusion | 10 each | |
| 635 | BiomeCypreJungle | 9 | Cliffs+River+Muddy+Cenotes |

Side finding: several of the top-stacked tiles (3214, 3678) list the **same mutator def
twice** in one tile's mutator array (e.g. `VEE_RedDesert` ×2, `VEE_Cactus_Barrel` ×2) —
worth a corrective on the generator, not just a density outlier.

### Never-used census
409 TileMutatorDefs in the offline def space; **247 (60%) never placed anywhere** on
this world (60 distinct defs actually appear across the 14,400 mutator-bearing tiles).
A large share of the unused 247 look like Alpha Biomes flora/terrain mutators
(`AB_GauranlenGrove`, `AB_GinkgoForest`, `AB_MauvebloomFields`, `AB_WillowForest`, …),
water-body mutators that need lakes/oceans this desert world barely has (`Lake`,
`LakeWithIsland`, `Cove`, `Fjord`, `Iceberg`, `Pond`), and several RUT-tier defs
(`RUT_ColdLavaTube`, `RUT_Lightfall`, `RUT_LightlessSink`, `RUT_ShadowedOverhang`,
`RUT_Slough_GelatinousBreach`) that appear to be authored but never actually rolled.
This is a raw count, not a verdict — whether each is "should occur but doesn't" or
"correctly gated out of a desert-dominant world" needs per-def review, not an audit.

---

## LANDMARKS

### Density per biome (landmarks / total tiles in biome)
Top 10 of biomes with landmarks:

| biome | tiles | landmarks | density |
|---|---|---|---|
| AB_MechanoidIntrusion | 236 | 155 | 0.657 |
| RUT_GreySea | 472 | 280 | 0.593 |
| RUT_TwilightSea | 607 | 333 | 0.549 |
| AB_MycoticJungle | 2204 | 912 | 0.414 |
| AB_RockyCrags | 1135 | 452 | 0.398 |
| ZBiome_Badlands | 970 | 333 | 0.343 |
| Scarlands | 90 | 30 | 0.333 |
| AB_GelatinousSuperorganism | 96 | 32 | 0.333 |
| AB_OcularForest | 179 | 59 | 0.330 |
| ZBiome_DesertOasis | 223 | 73 | 0.327 |

### Stacked-on-settlement violations (landmark tile == settlement tile)
**14 of 96 settlements (14.6%)** sit on a tile that also carries a landmark:
19350 "Vicky's Ruse" (Ruins), 5072 "Joyce's Sundering" (TerraformingScar), 21547
"Wasoum Launch Site" (AncientLaunchSite), 2607 "Kaalltioinum Ruins"
(RUT_ComplexStructures), 6664 "Cody's Folly" (RUT_ComplexStructures), 21037 "Meoum Cave
Network" (Cavern), 11779 "Inforda Sand Pit" (DryLake), 4366 "Trobo Gulch" (Valley),
12624 "Sharptoe Vale" (Valley), 16898 "Crialbo Gorge" (Valley), 18359 "Isistia Gorge"
(Valley), 780 "Youinor Sand River" (VEE_DryRiver), 675 "Dorboduecai Howl"
(TerraformingScar), 21576 "Blueclaw Scar" (TerraformingScar). Tile 2607 also appears in
the Coast-gate violation list above — a double-hit tile.

### Name-reuse census (top 15 of 3,414 landmarks, 3,372 distinct names, 42 dupes)
"Dead Sarlacc" ×7 (owner-flagged, confirmed), "Mindy's Caves" ×3, "Black Caverns" ×3,
"Ash's Caves" ×3, "Combarro Karst Hollows" ×3, "The Grand Scar" ×3, "Abeneiro Cenote
Lakes" ×2, "Marulo Scar" ×2, "Barga Town" ×2, "Red Heat Vents" ×2, "Katia's Caves" ×2,
"Purple Cave Network" ×2, "Sandra's Caves" ×2, "Diana's Caves" ×2, "Howard's Caves" ×2.
The "X's Caves" possessive-name pattern accounts for most of the reuse (5 of the top 15
rows) — likely one namer table with too few name roots, not a per-landmark defect.

### Icon coverage
Measured from `LandmarkDef.json`: **137/137 LandmarkDefs declare a non-empty
`iconTexturePath`** — 100% at the def-field level, including all 65 defs actually used
on this world. Whether each referenced texture file exists on disk is UNMEASURED (would
need a per-path file check against the mod's Textures folder, out of scope for this
offline pass).

### Landmark def never-used census
137 LandmarkDefs total, 65 used on this world, **72 never placed** — includes most
Alpha Biomes flora landmarks (AB_GauranlenGrove, AB_GinkgoForest, AB_WillowForest,
AB_SweetForest, …), water-feature landmarks this desert world has little room for (Lake,
LakeWithIsland(s), Cove, Fjord, Iceberg, Pond, CoastalAtoll), and five RUT-tier
landmarks that appear unrolled (RUT_ColdLavaTube, RUT_Lightfall, RUT_LightlessSink,
RUT_ShadowedOverhang, RUT_Slough_GelatinousBreach).

---

## 8-line summary

1. Coast gate | VIOLATION, confirmed+completed | 104/104 Coast-mutator tiles fail (audit's own list was truncated to 30/104)
2. isCoastal field | BROKEN data source | 0/14,400 tiles ever true — do not use it for future coastal checks
3. Hilliness gates | VIOLATION, new finding | 153 violations across 12 defs; Cliffs (43), InsectMegahive (28), Hollow (19) worst
4. River gate | UNMEASURED | no river field in this live export; needs a dedicated river export to check
5. Mutator stacking | minor defect | top tiles (3214, 3678) carry the same mutator def duplicated twice
6. Mutator never-used | 247/409 (60%) | mostly water-body and Alpha Biomes flora defs a desert world rarely rolls
7. Landmark/settlement collision | VIOLATION | 14/96 settlements (14.6%) share a tile with a landmark
8. Landmark names | matches owner report | "Dead Sarlacc" ×7 confirmed; top-15 dupes otherwise mostly the "X's Caves" namer pattern
