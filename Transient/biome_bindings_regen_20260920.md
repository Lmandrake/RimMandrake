# BIOME_BINDINGS_TABLE_STALE_1 — per-row proof notes (2026-09-20)

Instrument: `world/ASHKARR_WORLDMAP_tiles.csv` parsed with Python's `csv`
module (a parse, not a byte scan — `grep`/`wc` on this file are refused by
`.claude/hooks/block_blind_scan.py` and would return a wrong number anyway).
MEASURED: **21,872 data rows, 27 distinct painted biomes.**

## 1. Painted tile counts (MEASURED 2026-09-20)

```
3969 RUT_ExtremeDesert   2531 RUT_Umbra          2390 RUT_Desert
2204 RUT_TheRot          1853 RUT_Wasteland      1506 RUT_NightsideIce
1135 RUT_ForsakenCrags   1029 RUT_BlueDesert      970 RUT_CrackedLands
 628 RUT_AridShrubland    607 RUT_TwilightSea     546 RUT_PoisonForest
 472 RUT_GreySea          312 RUT_TheScald        236 RUT_RustCathedral
 235 RUT_Greentide        223 RUT_WeepingStones   222 ZBiome_Grasslands
 179 RUT_Contagion        161 RUT_Webwork          96 RUT_Slime
  93 RUT_Miasma            90 RUT_Scarlands        57 RUT_PropaneLake
  44 RUT_TheForge          43 RUT_FeverWood        41 RUT_Sump
```
Sum = 21,872. ✅ Every painted biome is accounted for by exactly one table row.

## 2. Def labels (MEASURED from `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/*.xml`)

Parsed with `ElementTree`; every `BiomeDef`'s `defName`, `label` and
`wildAnimals` child count read off the tree.

## 3. Per-row successor proofs

Proof method, per row: the OLD row's **sheet** is looked up in
`README_BIOME_GRAMMAR.md`'s progress table, which states the owner-given biome
NAME for that sheet; that name is then matched against the live def's
`<label>`. Tile-count identity is a corroborating second signal, never the
proof on its own.

| old def | sheet | README-stated name | live def `<label>` | new def | old→new tiles |
|---|---|---|---|---|---|
| `Desert` → already fixed | `desert.md` | `Desert` | "the Desert" | `RUT_Desert` | 2390 → 2390 |
| `ExtremeDesert` → already fixed | `dune_sea.md`+`deep_desert.md` | `ExtremeDesert` (Dune Sea) | "the Extreme Desert" | `RUT_ExtremeDesert` | 3969 → 3969 |
| `AB_PropaneLakes` | `the_propane_lakes.md` | "`AB_PropaneLakes` + Umbra, the antistellar cap" | "Umbra" | `RUT_Umbra` | 2531 → 2531 |
| `AB_MycoticJungle` | `the_rot.md` | "The Rot" (owner-named) | "the Rot" | `RUT_TheRot` | 2258 → 2204 |
| `RUT_NightsideIce` | `nightside_ice.md` | `RUT_NightsideIce` | "the Nightside Ice" | unchanged | 1506 → 1506 |
| `AB_RockyCrags` | `forsaken_crags.md` | "Forsaken Crags" | "the Forsaken Crags" | `RUT_ForsakenCrags` | 1170 → 1135 |
| `Wasteland` | `wasteland.md` | `Wasteland` | "the Wasteland" | `RUT_Wasteland` | 1126 → 1853 |
| `BiomeGRimond` | `the_blue_desert.md` | "Blue Desert" | "the Blue Desert" | `RUT_BlueDesert` | 1029 → 1029 |
| `ZBiome_Badlands` | `the_cracked_lands.md` | "the Cracked Lands" (owner-named) | "the Cracked Lands" | `RUT_CrackedLands` | 985 → 970 |
| `AridShrubland` | `arid_shrubland.md` | `AridShrubland` | "the arid shrubland" | `RUT_AridShrubland` | 665 → 628 |
| `PoisonForest` | `poison_forest.md` | `PoisonForest` | "the Poison Forest" | `RUT_PoisonForest` | 557 → 546 |
| `RUT_TwilightSea` | `terminator_sea.md`/`the_twilight_deep.md` | `RUT_TwilightSea` | "the Twilight Sea" | unchanged | 479 → 607 |
| `RUT_GreySea` | `terminator_sea.md`/`the_grey_deep.md` | `RUT_GreySea` | "the Grey Sea" | unchanged | 429 → 472 |
| `RUT_TheScald` | `the_scald.md` | `RUT_TheScald` | "the Scald" | unchanged | 312 → 312 |
| `AB_MechanoidIntrusion` | `the_rust_cathedral.md` | "the Rust Cathedral" | "the Rust Cathedral" | `RUT_RustCathedral` | 236 → 236 |
| `BiomeCypreJungle` | `the_greentide.md` | "the Greentide" (owner-named) | "the Greentide" | `RUT_Greentide` | 235 → 235 |
| `ZBiome_DesertOasis` | `weeping_stones.md` | "the Weeping Stones" (owner-named) | "the Weeping Stones" | `RUT_WeepingStones` | 223 → 223 |
| `ZBiome_Grasslands` | `the_pyrelands.md` | "the Pyrelands" | *(donor def, no RUT successor)* | unchanged | 222 → 222 |
| `AB_OcularForest` | `the_contagion.md` | "the Contagion" (owner-named) | "the Contagion" | `RUT_Contagion` | 179 → 179 |
| `AB_FeraliskInfestedJungle` | `the_webwork.md` | "the Webwork" (owner-named) | "the Webwork" | `RUT_Webwork` | 161 → 161 |
| `AB_GelatinousSuperorganism` | `the_slime.md` | "The Slime" (owner-named) | "the Slime" | `RUT_Slime` | 96 → 96 |
| `AB_MiasmicMangrove` | `the_miasma.md` | "the Miasma" (owner-named) | "the Miasma" | `RUT_Miasma` | 93 → 93 |
| `Scarlands` | `the_scarlands.md` | `Scarlands` (name kept) | "the Scarlands" | `RUT_Scarlands` | 90 → 90 |
| `RUT_PropaneLake` | `the_propane_lakes.md` | `RUT_PropaneLake`, 57 tiles | "the Propane Lake" | unchanged | 57 → 57 |
| `COMIGO_GreaterSwamp_Tropical` | `the_fever_wood.md` | "the Fever Wood" | "the Fever Wood" | `RUT_FeverWood` | 43 → 43 |
| `AB_TarPits` | `the_sump.md` | "the Sump" (owner-named) | "the Sump" | `RUT_Sump` | 42 → 41 |
| `AB_PyroclasticConflagration` + `LavaField` + `Volcano` | `the_forge.md` | "the Forge" — **one sheet, one massif** | "the Forge" | `RUT_TheForge` | 31+8+5 = 44 → 44 |

**Nothing was inferred from name similarity.** The three that name-similarity
would have got wrong — `AB_MycoticJungle`→`RUT_TheRot`,
`ZBiome_Badlands`→`RUT_CrackedLands`, `BiomeGRimond`→`RUT_BlueDesert` — plus
`AB_PropaneLakes`→`RUT_Umbra`, `AB_OcularForest`→`RUT_Contagion`,
`AB_FeraliskInfestedJungle`→`RUT_Webwork`, `AB_MechanoidIntrusion`→
`RUT_RustCathedral`, `BiomeCypreJungle`→`RUT_Greentide`,
`ZBiome_DesertOasis`→`RUT_WeepingStones`, `AB_TarPits`→`RUT_Sump`,
`COMIGO_GreaterSwamp_Tropical`→`RUT_FeverWood` and
`AB_GelatinousSuperorganism`→`RUT_Slime` all came out of the sheet→name→label
chain.

**Rows deleted: 0 for unprovable successor.** Two rows were MERGED, not
deleted: `LavaField` and `Volcano` collapse into `RUT_TheForge` along with
`AB_PyroclasticConflagration`, because all three shared one sheet
(`the_forge.md`, "one sheet, one massif") and the paint now carries one def of
44 tiles = 31+8+5. 29 rows → 27 rows, one per painted biome.

**Painted biomes with no row: none.** All 27 map to an old row.

## 4. wildAnimals owner re-derivation

⛔ **`src/RimUtinni/UtinniPatches/Patches/BiomeCast_Ashkarr.xml` DOES NOT
EXIST.** The old table named it as the owner for 23 of 29 rows. MEASURED
2026-09-20: no such file anywhere in the repo. That whole column was dead.

Method: (a) parse every `src/**/Defs/**/*.xml`, find each `BiomeDef` whose
`defName` is a painted biome and which declares a `wildAnimals` child;
(b) scan every non-`Defs/` XML for a `<xpath>` naming both the defName and
`wildAnimals`.

Result: **26 of the 27 painted biomes declare `wildAnimals` directly in their
own `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/<def>.xml`.** No patch file
wholesale-replaces any of them.

Two of those 26 declare an EMPTY `<wildAnimals />`: `RUT_BlueDesert` (1029
tiles) and `RUT_PropaneLake` (57 tiles) — 1,086 painted tiles with no cast.

`ZBiome_Grasslands` is the sole exception: it is a donor def, we ship no local
BiomeDef for it, and nothing of ours replaces its `wildAnimals`. The only
local operations on it are duplicate REMOVALS
(`AnimalBiomeDuplicates_Fix.xml` op on `…/wildAnimals/Iriaz[2]`,
`ZZZ_BiomeWildAnimalDuplicates_Generated.xml` on Gizka/Nuna/Orray/Zeer).

🔴 **Corroborates `PYRELANDS_WRONG_BIOME_DEF_1`:**
`src/RimUtinni/UtinniPatches/Patches/WildAnimals_Pyrelands.xml` wires the
ruled Pyrelands roster into **`RM_FE_Pyrelands`**, which carries **0** painted
tiles. Its only two mentions of `ZBiome_Grasslands` — the def that actually
holds the 222 Pyrelands tiles — are inside comments. The ruled roster reaches
no ground.

## 5. Traps and open-item exposure

- ⚠️ `GRASSLANDS_TILES_CSV_STALE_1` bites exactly one row: **`ZBiome_Grasslands`
  222**. That open item says this CSV disagrees with a live world read on
  Grasslands vs Pyrelands. Every other row's def is a `RUT_*` def we authored,
  and the CSV is the only instrument consulted here — a live world read has NOT
  been run and would be the confirming instrument.
- The `wildAnimals` entry counts above are structure counts off the def XML,
  not a live game read.
