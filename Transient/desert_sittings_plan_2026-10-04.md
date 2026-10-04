# Desert re-review: sittings plan, 2026-10-04 (`ART_VERSION_WRANGLING_1`)

Owner rulings 2026-10-04: one sitting per biome (desert, deep desert, blue desert); the 14 at-risk creatures first;
rows prefill with his latest keep (fallback: what the game shows).

**Biome split of the 109 desert-family rows: desert 95 · deep desert 13 · blue desert 1.**

## How each row was placed (my rule, flagged as invented on the sheet)

1. **Live roster commonality** in our XML (BiomeDefs plus patch-added `wildAnimals`/`wildPlants`, parsed as elements): Desert = `Desert`/`RUT_Desert`; deep desert = `ExtremeDesert`/`RUT_ExtremeDesert`/`RM_Stillsand` (deep_desert.md: the Stillsand is the one def); blue desert = `RM_BlueDesert`/`RUT_BlueDesert`/`BiomeGRimond`. Highest commonality wins.
2. If that share is tiny (<0.1) and the biome design sheets (`design/Jawa/worldbuilding/biomes/desert.md`, `deep_desert.md`+`dune_sea.md`+`stillsand_*`, `the_blue_desert.md`+`bluedesert_*`) name it 5+ times in another biome, the design sheet wins (Sand Squid/Ommok → deep).
3. No live roster: design-sheet mentions (3+), else the donor's own casting (Desert vs ExtremeDesert).
4. 🔴 **35 rows are cast ONLY in Arid Shrubland**, which is none of the three. They sit at the END of sitting 1 as group 3 (Desert is the nearest dry neighbour). If Arid Shrubland deserves its own sitting, they move there; nothing else changes.

⚠️ **The blue desert barely overlaps the 109.** Its live roster (`RM_BlueDesert`, `WildAnimals_BlueDesert.xml`) is its own RM cast (Vekkit, Utikka, Dorrak, Ossivel, Krissek …), none of which are desert-family rows. Only Scrubgrass leans blue, by design-sheet mentions.

Full per-row record: `Transient/desert_sittings_assignment_2026-10-04.json`. Builder: `Transient/desert_sitting1_build_2026-10-04.py`.

## Sitting 1 — built: `Transient/desert_sitting1_2026-10-04.html`

102 graphic rows (one per body texPath; f/m/juvenile are separate rows under one creature) for 80 creatures/plants: the 14 at-risk, then the rest of the Desert, then the Arid-Shrubland-only group. Korrum (boulder mit) and Eyeling are deep-desert but sit here as at-risk.
17 rows have no graphic of ours resolved (7 Outer Rim droids, Rat, Cindermite, Ashworm, 7 plants), so they are not on the sheet: DUM Repair Droid, Destroyer Droid, GNK Power Droid, MSE Repair Droid, Muckraker Crab Droid, creep stern, crimson cushion, dervish, dessert tree, fuelmite, fx-7 medical droid, hardy grass, low shrubs, rat, ripthorn, salvage assist droid, terrorworm. `swplants/Nysillin` is on the sheet with zero picture sets (the def points at donor art the ledger does not hold) and is left undecided.

## Sitting 2 — deep desert (not built yet)

| creature | def | why here |
|---|---|---|
| granite slug | `RSW_GraniteSlug` | live roster deep 0.1 |
| greater krayt dragon | `RSW_GreaterKraytDragon` | live roster deep 0.001 |
| krayt dragon | `RSW_KraytDragon` | live roster deep 0.15 |
| needleroll | `RSW_Kudda` | live roster desert 0.2, deep 0.3 |
| sand squid | `RSW_Ommok` | live roster desert 0.025; overridden: tiny live share and the deep design sheet names it 27x |
| scurrier | `RSW_Scurrier` | live roster deep 0.1; NOTE: cast more heavily in Arid Shrubland (0.8) |
| tetra slug | `RSW_Vozzik` | live roster deep 0.0005 |
| war wyrm | `RSW_WarWyrm` | live roster deep 0.2 |
| bloddle plant | `RSW_Plant_Bloddle` | live roster deep 0.05 |
| bush | `rut_grellbush` | no live desert-family roster; design sheets name it {'desert': 2, 'deep': 11, 'blue': 9} |
| giant stikehr | `RSW_AB_GiantStikehr` | no live roster of ours; donor casting ExtremeDesert=0.04 — **no graphic of ours resolved; not on a sheet** |

`AB_GiantStikehr` is out of scope (cut from the Extreme Desert 2026-09-20; do not re-add).

## Sitting 3 — blue desert (not built yet)

| creature | def | why here |
|---|---|---|
| grass | `RSW_Scrubgrass` | no live desert-family roster; design sheets name it {'desert': 0, 'deep': 1, 'blue': 8}; also Arid Shrubland 0.5 — **no graphic of ours resolved; not on a sheet** |

So sitting 3 holds almost none of the 109. Whether it should instead review the blue desert's own RM cast art is his call.

