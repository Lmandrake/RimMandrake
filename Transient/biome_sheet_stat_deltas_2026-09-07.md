# Biome sheet stat deltas — sheet claims vs current canon (2026-09-07)

Canon: `world/ASHKARR_WORLDMAP_tiles.csv` (21,872 rows, sha256 `82999c4c2382…`) +
`world/ASHKARR_WORLDMAP_links.csv` (1,713 rows). Read-only measurement, computed
fresh from these two files (structured CSV parse, not a grep/wc scan). Sheet→def
mapping taken from `README_BIOME_GRAMMAR.md` §"Progress". `arc` and `region`
columns exist in the CSV, so both are used directly (arc = angular distance from
substellar point; no derivation needed). "River tiles" = tiles appearing as an
endpoint of a `kind=river` row in `ASHKARR_WORLDMAP_links.csv`. "Water tiles" =
CSV `water==1` (not elevation-derived; the column exists). Hilliness 1–5 assumed
ordinal Flat/SmallHills/LargeHills/Mountainous/Impassable — **UNCONFIRMED against
a def/enum source, see UNKNOWN at bottom.**

🔴 **Important, discovered mid-measurement:** several sheets (e.g. `weeping_stones.md`,
2026-09-06) state they were measured off this exact file, row count 21,872, with a
cited sha256 (`b38fd68569237c96…`) that does **not** match the file's current hash.
Same row count, different content — the world was repainted again after those
sheets were written, so even the "freshly measured" sheets are against a superseded
state. This is the single biggest finding of this pass.

Notation: `stated → measured (Δ)`. `~` = matches within rounding, not flagged.
`?` = sheet gave no explicit number for this field.

---

## poison_forest.md → `PoisonForest`

Sheet gives no MEASURED tile-count block — qualitative only: "terminator band,
θ ≈ 75–105°."

| field | stated | measured |
|---|---|---|
| tiles | (none given) | **542** |
| arc p10/med/p90 | ? | 85.3 / 115.5 / 136.8 |
| temp med / range | ? | −21.4 °C / −51.9…+39.4 |
| elev med | ? | 532 m |
| hilliness (1–5) | ? | 178/125/56/173/10 |
| water / river | ? | 0 / 0 |
| top regions | ? | Twilight Crags 87, South Crags 87, Slough 73, Venom Wood 72 |

No numeric baseline to diff against, but the sheet's own qualitative arc window
(75–105°) is well inside the def's actual current spread (85–137°) — the def now
reaches **32° further past the terminator** than the sheet describes.

---

## dune_sea.md → `ExtremeDesert` (shared with `deep_desert.md`)

No MEASURED tile-count block; qualitative "deep dayside, θ ≈ 0–40°," `ExtremeDesert`
unbroken below 30°, mixed with `Desert` out to 40°.

| population | tiles | arc p10/med/p90 | temp med | elev med | water/river |
|---|---|---|---|---|---|
| `ExtremeDesert` — whole def | 3,172 | 23.3/42.7/62.4 | 48.3 °C | 198 m | 0/0 |
| `ExtremeDesert`, arc<40 (sheet's own filter) | 1,377 | 16.2/30.7/38.1 | 56.3 °C | 178 m | 0/0 |
| region "Dune Sea" (any biome) | 1,692 | 22.8/31.5/38.3 | 55.3 °C | 148 m | 0/99 |

No numeric claim to diff. Note region "Dune Sea" now carries **99 river tiles** —
worth a look given the sheet's whole thesis is that this ground is riverless
except at its one hard green edge.

---

## terminator_sea.md → `RUT_TwilightSea` + `RUT_GreySea`

Sheet gives single-point positions, not aggregate stats: Twilight Sea "θ 91,"
Grey Sea "θ 92," "~+14 °C at θ 90" for the terminator band generally.

| def | tiles | arc med | temp med | water/river |
|---|---|---|---|---|
| `RUT_TwilightSea` | 436 | 80.7 | 21.4 °C | 436/1 |
| `RUT_GreySea` | 381 | 86.0 | 17.2 °C | 381/3 |

Sheet's "~+14 °C at θ 90" is qualitative/approximate; both seas measure warmer
(17–21 °C median) — informative only, not a formal claim to flag as broken.

---

## nightside_ice.md → `RUT_NightsideIce`

| field | stated (2026-09-06) | measured | Δ |
|---|---|---|---|
| tiles | **802** | **802** | 0 |
| arc | 128→159 | p10 128.1 / p90 159.1 | ~ |
| temp p10/med/p90 | −70/−56/−39 | med −56.1 | ~ |
| elev med (max) | 1,129 (1,884) | 1,128.5 (1,884) | ~ |
| regions | Deadstone 509, Umbra 158, Ammonia Flats 73, Rimewall 30 | **identical** | 0 |

**UNCHANGED** — this sheet's numbers still hold exactly against current canon.

---

## deep_desert.md → `ExtremeDesert`, far ring (region-filtered)

Sheet's own filter is the 6 named regions, not the bare def (it explicitly mixes
`ExtremeDesert`+`Desert` per region). Comparing on that filter:

| region | stated tiles | measured tiles | Δ | stated arc | stated temp |
|---|---|---|---|---|---|
| Cracklands | 138 | **227** | **+89 (+64%)** | 67° | 31 °C |
| Thornbelt | 263 | **502** | **+239 (+91%)** | 69° | 30 °C |
| Dry Marches | 345 | **387** | +42 (+12%) | 68° | 29 °C |
| Long Sand | 532 | **721** | **+189 (+36%)** | 67° | 32 °C |
| Glare | 879 | 879 | 0 | 50° | 43 °C |
| Kiln | 878 | 878 | 0 | 51° | 43 °C |
| **total** | **≈3,035** | **3,594** | **+559 (+18%)** | | |

Measured (6-region filter): arc p10/med/p90 44.6/60.6/77.8 (sheet's aggregate was
"arc 50–69"; the low end now extends 6° further); temp med 36.2 °C; elev med 146 m;
hilliness 1/2/3 = 2044/1258/292 (no 4/5 — flat def); water 0, river 6.

**MATERIALLY MOVED** — Glare and Kiln (the "deep" and "the margin") are untouched;
Cracklands, Thornbelt, Dry Marches and Long Sand (the outer four) all grew, most by
a third to nearly double.

---

## desert.md → `Desert`

| field | stated | measured | Δ |
|---|---|---|---|
| tiles | 4,151 (19%) | **4,204** | +53 (+1.3%, not material) |
| arc (core) | 60–88 | med 75.8, p10 52.9, p90 99.4 | consistent |
| temp (core) | 24.5 °C | med 24.3 °C | ~0.2 °C, not material |
| hilliness (core) | 2.0 | full-pop mode is 1 (2,159 of 4,204) | see caveat below |

Sheet itself already flags "only ~51% of the def's tiles currently fit this
definition" and cites a stale 2,401-tile world-definition census — its own
caveat, not a new finding. Full-population hilliness (not core-filtered) skews
flatter than the core-only "2.0" the sheet reports, consistent with that caveat.

---

## arid_shrubland.md → `AridShrubland`

| field | stated (2026-09-05) | measured | Δ |
|---|---|---|---|
| tiles (whole def) | 748 | **633** | **−115 (−15.4%)** |
| core (arc 70–95) tiles | 361 | **329** | **−32 (−8.9%)** |
| core temp med | 18.3 °C | 18.5 °C | ~ |
| core hilliness "flat" | 312/361 (86%) | cat 1+2 = 239/329 (73%) | **material — 13pt drop in flat fraction** |
| tail: arc<70, up to 59.6 °C | 248 tiles | whole-def temp max 59.4 °C | consistent shape |

**MATERIALLY MOVED** — the def lost roughly 1 in 7 of its tiles since 2026-09-05,
and the core band lost proportionally as much; the flat-ground fraction the sheet
built its ecology on ("flat 312/361") is now visibly less flat.

---

## wasteland.md → `Wasteland`

| field | stated | measured | Δ |
|---|---|---|---|
| tiles | 1,699 | 1,713 | +14 (+0.8%, not material) |
| arc | 75→130, med 100 | p10 75.7, med 99.7, p90 125.3 | ~ |
| temp med (overall) | (not given, per-family only) | 0.8 °C | — |

Not material by the thresholds; arc and tile count both hold within noise.

---

## forsaken_crags.md → `AB_RockyCrags`

| field | stated (2026-09-05/06) | measured | Δ |
|---|---|---|---|
| tiles | **1,225** | **1,984** | **+759 (+62%)** |
| arc | 99→121 | p10 102.6, med 118.3, **p90 163.4** | **range now extends to 163°, not 121°** |
| temp med (range) | −14 °C (−30…+30.9) | **−23.7 °C** (**−81.7**…+30.9) | **Δ 9.7 °C med; min dropped 51.7 °C** |
| elev med | 566 m | 675 m | +109 m |
| hilliness ≥ large-hill | 614/1,225 (50%) | 687/1,984 (35%) | **material — proportion fell 15pt** |
| water | 5 | **0** | **−5** |
| top regions | Rimewall 258, Gray Crags 181, Sunreach 174, Nightspill 172, Twilight Crags 169, The Verge 103 | **Ammonia Flats 342, Umbra 267**, Rimewall 258, Gray Crags 181, Sunreach 174, Nightspill 172, Twilight Crags 169, Deadstone 159 | **two entirely new top regions, absent from the sheet's list** |

**MAJOR MOVE, the largest in this pass.** The def grew by nearly two-thirds and
picked up two whole new regions (Ammonia Flats, Umbra — nightside-ice/propane-lake
country) it did not have when the sheet was written; the temperature floor dropped
52 °C and water tiles vanished entirely.

---

## the_rot.md → `AB_MycoticJungle`

| field | stated (2026-09-05) | measured | Δ |
|---|---|---|---|
| tiles | 1,939 | 1,939 | 0 |
| arc | 89→130 | p10 88.7, p90 129.9 | ~ |
| temp med (range) | −19.3 (−54.3…+23.8) | −19.3 (−54.3…+23.8) | **exact** |
| elev med | 703 | 703 | 0 |
| water/river | 0/0 | 0/0 | 0 |
| regions | Nightspill 368, Frostcaps 224, Sporefields 170, Blindwood 135, Mould Marches 121, Hanging Wood 118 | **identical** | 0 |

**UNCHANGED — exact match on every field.**

---

## the_slime.md → `AB_GelatinousSuperorganism`

| field | stated | measured | Δ |
|---|---|---|---|
| tiles | 96 | 96 | 0 |
| arc p10/med/p90 | 84.6/90.0/99.1 | 84.6/90.0/98.5 | ~ |
| temp med (range) | 13.4 (−2.7…21.9) | 13.4 (−2.7…21.9) | exact |
| elev med | 3 | 3.0 | 0 |
| "dead flat" | 88/96 | cat-1 = 91/96 | minor, +3, not material |
| regions | Slough 58, Glass Reach 15, Nightspill 14, Chalk Marches 9 | identical | 0 |

**Essentially unchanged** — one 3-tile hilliness-category shift, nothing material.

---

## the_contagion.md → `AB_OcularForest`

Sheet describes a **not-yet-final candidate/placement** ("Exact list ruled in
`CONTAGION_BIOME_PLACEMENT_1`"), not a finished census: candidate set was Scald
Spine's 38 non-green high tiles + optional Ashfall Range 35 + Dew Horn 137
(≈210 tiles, optional).

| field | candidate (sheet) | measured (as painted now) |
|---|---|---|
| tiles | ~210 (optional, not committed) | **179** |
| regions | Scald Spine 38, Ashfall Range 35(opt), Dew Horn 137(opt) | **Dew Horn 87, Scald Spine 44, Ashfall Range 24, Dune Sea 17, Fall Line 5, Anvil 2** |
| elev med | Scald Spine candidate 1,170 m | 1,387 m |
| hilliness | (candidate = "non-green," i.e. hilly) | 4/5 only: 61/118 — all large-hill or worse |

**Already painted, but on different numbers than the candidate the sheet
describes** — Dew Horn got far fewer tiles than the optional 137, and 22 tiles
landed in Dune Sea/Fall Line, which the candidate list never mentioned at all.

---

## the_blue_desert.md → `BiomeGRimond`

Sheet describes a **5-lobe mosaic plan, "rendered for the owner before painting"**
— i.e. not committed at write time — against a 1,711-tile former-`HorrorWastes`
Deadstone-ring baseline (arc 126→143, temp med −44.4, elev med 691, hilliness
1,160 small-hill/512 large/8 mountain/31 flat, water 0, river 0).

| field | plan baseline | measured `BiomeGRimond` now |
|---|---|---|
| tiles | (core estimate 700–900, from a 1,711-tile source pool) | **1,328** |
| arc | 126→143 | p10 126.7, med 137.1, p90 148.8 |
| temp med | −44.4 °C | **−45.3 °C** (~1°C, borderline) |
| elev med | 691 m | 597 m |
| regions | (Deadstone ring, unsplit) | Deadstone 986, South Crags 93, Umbra 86, Thornend 61, Lantern Deeps 57, Nightspill 17, Ammonia Flats 13, Sunreach 6 |

**Already painted at 1,328 tiles — well above the plan's own 700–900 "core"
estimate**, and pulling from 8 regions where the plan described one ring.

---

## the_propane_lakes.md → `AB_PropaneLakes`

| field | stated (2026-09-06) | measured | Δ |
|---|---|---|---|
| tiles | **1,589** | **987** | **−602 (−38%)** |
| arc | 145→170 | **p10 135.2**, med 150.7, p90 165.5 | **low end now 10° past the stated floor** |
| temp p10/med/p90 | −75.7/−64.3/−55.1 | med **−60.8** | **Δ 3.5 °C** |
| elev med | 572 | 638 | +66 m |
| water | 0 | 0 | 0 |
| regions | Ammonia Flats 732, Umbra 558, Deadstone 299 | **Ammonia Flats 362, Deadstone 360, Umbra 262**, Nightspill 3 | **all three roughly halved/reshuffled; Deadstone overtook Umbra** |

**MAJOR MOVE.** Also confirms the sheet's own note that "the lake gets its own
tiles": a separate def `RUT_PropaneLake` now holds 57 tiles (all water=1,
regions Umbra 29/Ammonia Flats 28) — real, and consistent with the sheet's text.

---

## the_cracked_lands.md → `ZBiome_Badlands`

| field | stated (2026-09-06) | measured | Δ |
|---|---|---|---|
| tiles | 1,086 | **1,023** | −63 (−5.8%) |
| arc | 53→102, med 68 | p10 51.7, med 69.5, p90 102.1 | ~ |
| temp p10/med/p90 | 1/27/41 | med 26.3 | ~0.7 °C, not material alone |
| elev med (max) | 164 (2,101) | 132 (**1,936**) | **max dropped 165 m** |
| hilliness (flat/small/large/mtn) | 182/378/197/328 | **295/137/359/49** | **material — mountainous fraction collapsed 328→49** |
| water / river | **27** / 4 | **0** / 2 | **water tiles vanished entirely** |
| top regions | Dew Horn 353, Cracklands 210, Gray Crags 84, Salt 74, Damp 74, Dune Sea 62, Long Sand 29 | Dew Horn **278**, Cracklands 210, Gray Crags 84, Damp 78, Salt 74, Dune Sea 71, Long Sand 31, **Wither 28 (new)** | Dew Horn −75 |

**MATERIALLY MOVED** — the sheet's own headline "no standing surface water beyond
the measured 27 tiles" is now false (0 water tiles), and the mountainous-terrain
fraction it built the fauna/relief story on collapsed by 85%.

---

## weeping_stones.md → `ZBiome_DesertOasis`

Sheet cites the exact CSV it measured against: 21,872 rows, sha256
`b38fd68569237c96…` — **does not match the current file's hash**, despite the
same row count.

| field | stated | measured | Δ |
|---|---|---|---|
| tiles | 236 | 223 | −13 (−5.5%) |
| arc | p10 24.5/med 59.3/p90 80.0 (approx from "26.3→79.9, med 58.0") | p10 24.5, med 59.3, p90 80.0 | ~ |
| temp med (range) | 35.5 (17.8…63.5) | 35.3 (17.8…63.5) | ~ |
| elev med | 612 | 612 | 0 |
| hilliness (flat/small/large/mtn/imp) | 56/81/48/50/1 | **54/61/38/60/10** | **material — mountain+impassable dropped 51→10** |
| water/river | 0/1 | 0/2 | minor |
| top regions | Dew Belt 92, Dew Horn 66, Dune Sea 36, Scald Spine 24, Anvil 11, Hollow Verge 7 | Dew Belt **83**, Dew Horn **54**, Dune Sea 39, Scald Spine 24, Anvil 13, Hollow Verge 7, Fever Wood 3 (new) | Dew Belt −9, Dew Horn −12 |

**MODERATELY MOVED** — tile count down 5.5%, and the mountain/impassable share of
the terrain (the "seep oasis in gorge country" texture) fell from 51 to 10 tiles.

---

## the_greentide.md → `BiomeCypreJungle`

The sheet's entire thesis is one sentence: **"191 tiles — and every single one is
a river tile."**

| field | stated | measured | Δ |
|---|---|---|---|
| tiles | 191 | **227** | **+36 (+18.8%)** |
| river tiles | **191/191 (100%)** | **191/227 (84%)** | **the defining claim is now false — 36 non-river tiles exist** |
| arc | 27.8→53.6, med 44.6 | p10 23.5, med 44.7, p90 54.0 | low end extended |
| temp med (range) | 44.8 (37.3…64.4) | 45.5 (35.5…64.4) | ~0.7 °C med; min dropped 1.8 °C |
| elev med | 313 | 287 | −26 |
| hilliness ≥ large-hill | 125/191 (65%) | **60/227 (26%)** | **material — hilly fraction collapsed** |
| top regions | Dune Sea 70, Scald Spine 62, Dew Belt 31, Hollow Verge 13, Anvil 9, Dew Horn 6 | Dune Sea 81, Scald Spine 58, Dew Belt 41, Hollow Verge 13, Anvil 13, Dew Horn 11, **Fever Wood 10 (new)** | — |

**MAJOR MOVE** — the sheet's single defining number (100% river coverage) no
longer holds; the biome gained 36 non-river tiles and lost most of its hilly
"gorge country" character.

---

## the_webwork.md → `AB_FeraliskInfestedJungle`

Sheet states **"172 tiles, 0 river tiles, 0 water tiles"** explicitly.

| field | stated | measured | Δ |
|---|---|---|---|
| tiles | 172 | 169 | −3, not material |
| river tiles | **0** | **8** | **claim now false** |
| water | 0 | 0 | 0 |
| arc (sun median +50 → arc 40) | 21→54 | p10 21.2, med 39.4, p90 53.3 | ~ |
| temp med (range) | 47.4 (36.2…63.5) | **49.2** (36.2…63.9) | **Δ 1.8 °C** |
| hilliness ≥ mountainous | 69/172 (40%) | 43/169 (25%) | **material — collapsed** |
| top regions | Dune Sea 73, Scald Spine 50, Dew Belt 19, Hollow Verge 16, Anvil 14 | Dune Sea 81, Scald Spine 43, Dew Belt 16, Hollow Verge 16, Anvil 12 | minor shuffle |

**MOVED** — the "0 river tiles" invariant the sheet leans on ("the drunk river"
notwithstanding — it explicitly measured 0) is now 8; temp and hilliness both
moved materially.

---

## the_scarlands.md → `Scarlands`

| field | stated | measured | Δ |
|---|---|---|---|
| tiles | 90 | 90 | 0 |
| sun med (arc) | +72° (arc 18) | +71.7° (arc 18.3) | ~ |
| temp med (range) | 59.4 (57.6…66.0) | 59.5 (57.6…66.0) | exact |
| hilliness (large-hill+mtn) | 36+11 = 47/90 | cat-3 alone = 47/90 (cats 4/5 = 0) | **same total, different category split — see hilliness UNKNOWN** |
| river (flagged anomaly) | 3 | 3 | 0 |

**Essentially unchanged** on every field except the hilliness *category split*,
which sums identically (47) but is now concentrated in one bucket instead of two
— most likely an artifact of the unconfirmed 1–5 enum mapping, not a real
population change (see UNKNOWN).

---

## the_rust_cathedral.md → `AB_MechanoidIntrusion`

| field | stated | measured | Δ |
|---|---|---|---|
| tiles | 236 | 236 | 0 |
| arc med | 10.7 | 10.7 | exact |
| temp med (range) | 62.5 (58…66) | 62.5 (58…65.9) | ~ |
| flat tiles | 211/236 | 217/236 | minor, +6 |
| river (flagged anomaly) | 8 | 10 | +2, minor |

**Essentially unchanged** — small noise only.

---

## the_miasma.md → `AB_MiasmicMangrove`

| field | stated | measured | Δ |
|---|---|---|---|
| tiles | 92 | 93 | +1, not material |
| elev med | 22 | 22 | 0 |
| river / sea(water) | 32 / **6** | 31 / **0** | **water tiles vanished (6→0)** |
| sun med (arc) | +39° (arc 51) | +38.7° (arc 51.3) | ~ |
| temp med (range) | 42.8 (26…59) | 42.8 (26.0…59.1) | exact |
| top regions | Dune Sea 29, Fever Wood 21, Dew Horn 17, Salt Gate 16, Grey Sea 6 | **identical counts** | 0 |

**One material change**: the 6 stated "sea tiles" are gone; everything else,
including all named regions, matches exactly.

---

## the_fever_wood.md → `COMIGO_GreaterSwamp_Tropical`

| field | stated | measured | Δ |
|---|---|---|---|
| tiles | 60 | **43** | **−17 (−28.3%)** |
| region | 100% Fever Wood | 100% Fever Wood | 0 |
| elev med | 21 | 22 | ~ |
| flat | 47/60 (78%) | 43/43 (100%) | shrank but got *more* uniform |
| sun med (arc) | +43° (arc 47) | +42.6° (arc 47.4) | ~ |
| temp med (range) | 45.7 (37.6…51.5) | 45.5 (37.6…51.5) | ~ |
| water/river/rain | 0/0/0 | 0/0/— | 0 |

**MATERIALLY MOVED on tile count** (−28%) but the shape (arc, temp, elevation,
flatness) is preserved — a real shrink, not a redefinition.

---

## the_sump.md → `AB_TarPits`

| field | stated | measured | Δ |
|---|---|---|---|
| tiles | 62 | **40** | **−22 (−35.5%)** |
| sun med (arc) | −6.6° (arc 96.6) | **−10.7° (arc 100.7)** | **moved 4° further into the night** |
| temp med (range) | 4.7 (−6.5…21.2) | **1.2** (−6.3…20.3) | **Δ 3.5 °C** |
| elev med | 1 | 1.0 | 0 |
| flat | 51/62 (82%) | 26/40 (65%) | **material — less flat** |
| regions | Nightspill 31, Glass Reach 26 | Nightspill **23**, Glass Reach **11** | both down sharply |

**MAJOR MOVE** — over a third of the def's tiles are gone, arc/temp moved
materially, and the two named regions both shrank hard (Glass Reach −58%).

---

## the_pyrelands.md → `ZBiome_Grasslands`

| field | stated | measured | Δ |
|---|---|---|---|
| tiles | 226 | 222 | −4, not material |
| regions | Dune Sea 107, Pyrelands 63, Anvil 36, Dew Belt 12, Kiln 6, Hollow Verge 2 | Dune Sea **98**, Pyrelands 63, Anvil **41**, Dew Belt 12, Kiln 6, Hollow Verge 2 | Dune Sea −9, Anvil +5 |
| arc p10/med/p90 | ~17/34/57 | 16.9/34.2/57.3 | exact |
| temp med (range) | 53.6 (28…65) | 53.6 (28.4…64.7) | exact |
| elev med | ~245 | 260.5 | +15.5, minor |
| river | 9 | 12 | +3, minor |

**Essentially unchanged** — well inside noise on every field.

---

## the_forge.md → `Volcano` + `LavaField` + `AB_PyroclasticConflagration`

| def | stated tiles | measured tiles | Δ | elev med stated | elev med measured |
|---|---|---|---|---|---|
| Volcano | 5 | 5 | 0 | 1,875 | 1,875 (exact) |
| LavaField | 8 | 8 | 0 | 1,496 | **1,753** |
| AB_Pyroclastic | 31 | 31 | 0 | 1,382 | 1,382 (exact) |
| **total** | **44** | **44** | **0** | | |

**Tile counts unchanged exactly, all three defs.** One material internal drift:
LavaField's elevation median moved +257 m (1,496→1,753) with no tile-count
change — the flows shifted higher on the massif. The stated "max 2,266" belongs
to AB_Pyroclastic in the measured data, not Volcano — a sheet labeling
imprecision, not a canon change.

---

## the_scald.md → `RUT_TheScald`

| field | stated | measured | Δ |
|---|---|---|---|
| tiles | 312 | 312 | 0 |
| def actually painted | (open question — "Lake"-painted at reconciliation time) | **`RUT_TheScald`, confirmed** (`Lake` def now has only 10 unrelated tiles elsewhere) | resolved |
| depth | ruled −30 m; "live-measured −350 m" | elev med **−350** | **matches the sheet's own live figure exactly** |
| river | "eight rivers end in it, none leave" | 8 | exact |
| "air +58…+70 °C" | Anvil substellar-band context | tile temp_c med 46.3, range 36.0…52.9 | **does not overlap the stated range — likely ambient-air vs. tile temp_c, not a real conflict; flagged, not asserted as a drift** |

**Confirmed painted as `RUT_TheScald`, tile count and river count exact matches.**
The one apparent mismatch (temperature) is most likely a units/quantity mismatch
in the sheet's own text, not a canon change — noted, not counted as moved.

---

## Skipped sheets (8)

| sheet | reason |
|---|---|
| `fall_line.md` | injection layer over `ExtremeDesert`, no new BiomeDef — per task instruction |
| `assailant_weapon_remnants.md` | dissolved; neither `HorrorWastes` nor `AB_OcularForest`-as-Overdrive is a biome — per task instruction |
| `the_grey_deep.md` | sea-bottom, design-only, no worldmap tiles — per task instruction |
| `the_twilight_deep.md` | sea-bottom, design-only, no worldmap tiles — per task instruction |
| `wreck_fields.md` | superseded by `fall_line.md` — per task instruction |
| `the_lantern_deeps.md` | README rules it "NOT a worldmap biome — an injected underground layer"; its surface tiles were re-homed into `nightside_ice.md`/`the_blue_desert.md`, already reflected there |
| `edible_genepack_native_mechanism.md` | not a biome-def sheet (gene-list mechanism doc, absent from the README status table) |
| `the_slime_gene_lists.md` | not a biome-def sheet (gene-list doc for `the_slime.md`, absent from the README status table) |

26 sheets measured, 8 skipped — 34 total (matches the directory listing minus
`README_BIOME_GRAMMAR.md` and the underscore-prefixed prep files).

---

## Summary — biomes whose numbers moved materially

| biome (sheet) | what moved | old → new |
|---|---|---|
| `AB_RockyCrags` (forsaken_crags) | tile count, temp floor, water, +2 new regions | 1,225→1,984 tiles; temp med −14→−23.7°C (min −30→−81.7); water 5→0 |
| `AB_PropaneLakes` (the_propane_lakes) | tile count, temp med, region shuffle | 1,589→987 tiles (−38%); temp med −64.3→−60.8°C |
| `BiomeCypreJungle` (the_greentide) | tile count, **river-coverage claim broken**, hilliness | 191→227 tiles; 100%→84% river; hilly fraction 65%→26% |
| `ExtremeDesert` far ring (deep_desert, region-filtered) | tile count (4 of 6 regions) | ≈3,035→3,594 tiles (+18%) |
| `AridShrubland` (arid_shrubland) | tile count, core-band flatness | 748→633 tiles (−15%); core 361→329 |
| `ZBiome_Badlands` (the_cracked_lands) | tile count, water, hilliness | 1,086→1,023; water 27→0; mountainous 328→49 |
| `AB_TarPits` (the_sump) | tile count, temp med, regions | 62→40 tiles (−35%); temp med 4.7→1.2°C |
| `AB_TarPits` sibling: `COMIGO_GreaterSwamp_Tropical` (the_fever_wood) | tile count | 60→43 tiles (−28%) |
| `AB_FeraliskInfestedJungle` (the_webwork) | **river claim broken**, temp med, hilliness | river 0→8; temp med 47.4→49.2°C; hilly 40%→25% |
| `ZBiome_DesertOasis` (weeping_stones) | tile count, hilliness | 236→223; mountain+impassable 51→10 |
| `AB_MiasmicMangrove` (the_miasma) | water/sea tiles only | 6→0, everything else matched |
| `AB_OcularForest` (the_contagion) | placement realized, different from candidate | candidate ~210 (unrealized) → 179 painted, different regions |
| `BiomeGRimond` (the_blue_desert) | placement realized, above plan estimate | plan "core 700–900" → 1,328 painted |
| `LavaField` (the_forge, one of three defs) | elevation only, tile count unchanged | elev med 1,496→1,753 m |

Unchanged or noise-only: `RUT_NightsideIce`, `AB_MycoticJungle` (the_rot),
`AB_GelatinousSuperorganism` (the_slime), `Wasteland`, `Desert` (within its own
stated caveat), `Scarlands`, `AB_MechanoidIntrusion`, `ZBiome_Grasslands`
(the_pyrelands), `RUT_TheScald`, `Volcano`/`AB_Pyroclastic` (the_forge).

---

## UNKNOWN

- **Hilliness enum mapping (1–5) is assumed, not confirmed.** I mapped it
  ordinally to Flat/SmallHills/LargeHills/Mountainous/Impassable based on the
  task brief and sheets' own increasing-severity language. `the_scarlands.md`'s
  comparison (stated 36 large-hill + 11 mountain = 47, measured 47 all in one
  category) is consistent with the *total* but not the *split*, which is exactly
  what a wrong ordinal assumption would produce. I did not verify this against
  RimWorld's `Hilliness` enum or a def dump in this pass — treat every hilliness
  category-level (not total-level) delta above as provisional on this mapping.
- **`river_flow` column** (207 distinct non-zero values, mixing what look like
  tile IDs and flow-volume floats) was not used — I used link-membership
  (`ASHKARR_WORLDMAP_links.csv`, kind=river) instead, per the task's own
  fallback instruction, since the column's semantics weren't self-evident and
  using it uninterpreted risked a wrong count.
- **`the_scald.md`'s "air +58…+70 °C"** does not reconcile with the tile
  `temp_c` field (med 46.3, max 52.9) — flagged as likely a different quantity
  (ambient/regional air vs. the CSV's per-tile value) rather than asserted as a
  canon drift, because I could not confirm which the sheet intended.
- **Why the hash changed with the same row count** (world repainted again after
  even the 2026-09-06/07 sheets were measured) — I did not investigate the cause,
  only detected the mismatch. Worth a follow-up if anyone wants to know which
  pass did it.
