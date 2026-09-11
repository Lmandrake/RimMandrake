# Biome-seam and landform audit — Ash'karr worldmap

Read-only. Data: `Transient/final_review/tiles.csv` (live truth, 21,872 rows),
`world/ASHKARR_WORLDMAP_tiles.csv` (arc/region, 21,872 rows, biome column
byte-identical to tiles.csv — 0/21872 mismatches), `world/world_neighbors_sub7b.csv`
(adjacency, 21,872 rows). Calibration against the owner's three numbers
(AB_PropaneLakes 2531, RUT_PropaneLake 57, ZBiome_Grasslands 222) via
`measure csv --where` all passed exactly — parse trusted.

All numbers below are MEASURED against this data unless marked UNMEASURED.
Full script: `/tmp/claude-1000/-mnt-d-Luke-dev-Rimworld/d0835c1a-1b61-4719-9ea6-f4dfb6c00495/scratchpad/audit.py`
(raw output: `.../scratchpad/audit_out.txt`, border pairs CSV:
`.../scratchpad/border_pairs.csv`).

## 1. Border matrix

Top 25 biome-pair edge counts (undirected, each adjacency counted once):

```
1024 Desert -- ExtremeDesert          412 Desert -- ZBiome_Badlands       178 AridShrubland -- RUT_GreySea
 502 Desert -- Wasteland              354 AB_FeraliskInfestedJungle --    148 AB_RockyCrags -- Wasteland
 491 AB_PropaneLakes -- BiomeGRimond      BiomeCypreJungle                134 AB_RockyCrags -- ZBiome_Badlands
 451 BiomeGRimond -- RUT_NightsideIce 351 AridShrubland -- Desert         131 AB_FeraliskInfestedJungle --
 440 AB_MycoticJungle --                326 AB_MycoticJungle --               ZBiome_DesertOasis
     RUT_NightsideIce                      AB_RockyCrags                 129 AridShrubland -- RUT_TwilightSea
 418 Desert -- PoisonForest           323 AridShrubland -- ZBiome_Badlands 127 ZBiome_DesertOasis --
                                      318 AB_RockyCrags -- Desert              ZBiome_Grasslands
                                      225 AB_RockyCrags -- RUT_NightsideIce 112 AB_MycoticJungle -- PoisonForest
                                      201 AridShrubland -- Wasteland       111 PoisonForest -- Wasteland
                                      199 AB_OcularForest -- ZBiome_Badlands
                                      192 Wasteland -- ZBiome_Badlands
                                      189 AB_MycoticJungle -- Desert
```

Already-ruled, excluded from findings below: AB_PropaneLakes--BiomeGRimond (491,
the propane cap), BiomeGRimond--RUT_NightsideIce (451) and AB_MycoticJungle
(the Rot)--RUT_NightsideIce (440, the Rot's cold tail).

**Seams with ≥100 edges where neither side's owning sheet mentions the other
(grep of `design/Jawa/worldbuilding/biomes/*.md`, defName + prose):**

- **AB_FeraliskInfestedJungle -- BiomeCypreJungle, 354 edges.** `the_webwork.md`
  (Feralisk's sheet) never mentions BiomeCypreJungle or "Greentide";
  `the_greentide.md` (Cypre's sheet) never mentions AB_FeraliskInfestedJungle or
  "Webwork". This is the single largest undocumented seam on the planet by edge
  count — two named jungle biomes share a 354-tile border and neither sheet
  acknowledges the other exists.
- **Desert -- PoisonForest, 418 edges** (6th-largest border on the whole
  planet). `poison_forest.md` contains **zero** occurrences of "desert",
  "wasteland", "rot", "mycotic", "badlands" or "arid" in any form — its
  neighbors are simply never discussed, despite `the_one_map.md`'s own
  night-margin doctrine chaining "terminator → poison forest → dark margin".
  Same silence covers PoisonForest--Wasteland (111) and
  AB_MycoticJungle--PoisonForest (112): PoisonForest's sheet is silent about
  every one of its real top neighbors.
- **AridShrubland -- ZBiome_Badlands, 323 edges** and **AridShrubland --
  Wasteland, 201 edges.** `arid_shrubland.md` names Desert/ExtremeDesert as
  neighbors but never Badlands or Wasteland; `the_cracked_lands.md` (Badlands)
  and `wasteland.md` never name AridShrubland back.
- **AB_FeraliskInfestedJungle -- ZBiome_DesertOasis, 131 edges** and
  **ZBiome_DesertOasis -- ZBiome_Grasslands, 127 edges.** `weeping_stones.md`
  (Oasis) never mentions Feralisk/Webwork or Grasslands/Pyrelands;
  `the_webwork.md` and `the_pyrelands.md` don't mention Oasis back.
- **AB_RockyCrags -- ZBiome_Badlands, 134 edges.** Neither `forsaken_crags.md`
  nor `the_cracked_lands.md` mentions the other. Lower-confidence than the
  above: AB_RockyCrags has no single owning sheet (it's a shared background
  hills biome referenced from three different docs), so this may just be
  generic-terrain adjacency rather than a designed seam gap.

**Checked and NOT a finding (documented on purpose):** AridShrubland--RUT_GreySea
(178) and AridShrubland--RUT_TwilightSea (129) — `arid_shrubland.md` explicitly
states "each shrubland is the plume of the sea upwind of it" and gives
region-level tile counts against Grey Sea (81) and Twilight Sea (49). AB_RockyCrags
--RUT_NightsideIce (225) is documented in `nightside_ice.md`. Wasteland--
ZBiome_Badlands (192) is documented in `the_cracked_lands.md`. AB_OcularForest--
ZBiome_Badlands (199) is loosely covered ("ocular/Contagion valleys" in
`the_cracked_lands.md`).

## 2. Dryland ladder

Dayside land tiles (arc<90, elevation>0) binned by 5° arc, mean temperature:

```
arc[0,5)=63.57C  [20,25)=57.87C [40,45)=48.07C [60,65)=33.40C [80,85)=18.90C
[5,10)=64.26C    [25,30)=57.08C [45,50)=44.42C [65,70)=30.38C [85,90)=15.19C
[10,15)=62.97C   [30,35)=54.90C [50,55)=40.94C [70,75)=27.13C
[15,20)=59.72C   [35,40)=51.69C [55,60)=37.24C [75,80)=23.04C
```

**MEASURED: strictly monotonic decreasing, no band breaks by >3°C.** No finding
— the arc→temperature ladder is clean across all 18 bands, n=46 to 842 tiles/band.

## 3. Hilliness composition vs sheet claims

Only two sheets state a numeric hilliness split:

- **`weeping_stones.md` (ZBiome_DesertOasis, n=223 stated).** Stated: 61
  small-hill / 60 mountainous / 54 flat / 38 large-hill / 10 impassable →
  27.4/26.9/24.2/17.0/4.5%. Measured: SmallHills 27.4%, Mountainous 26.9%,
  Flat 24.2%, LargeHills 17.0%, Impassable 4.5%. **Exact match, 0.0pp delta
  on every bucket.** No finding.
- **`forsaken_crags.md` (AB_RockyCrags, n=1170 stated, matches measured n
  exactly).** Stated "614 tiles at large-hills-or-worse, 17 impassable" (of
  1170) = 52.5% large-hills-or-worse. Measured large-hills-or-worse
  (LargeHills+Mountainous+Impassable) = 722/1170 = **61.7%, a 9.2pp delta** —
  under the 10pp report threshold, but note the sheet itself flags this
  figure as "hilliness-bucket counts are unmeasured by this pass, carried
  from the prior census," i.e. it already knows it's stale. Not reported as
  a violation (threshold not cleared) but flagged as self-admitted stale.
- **`the_greentide.md` (BiomeCypreJungle)** makes a qualitative, non-numeric
  claim: "gorge country, not flat jungle." Measured composition is Flat
  46.0% / LargeHills 18.3% / Mountainous 17.4% / SmallHills 9.8% / Impassable
  8.5% — **Flat is the single largest bucket, directly contradicting "not
  flat jungle."** No percentage was stated to diff against the 10pp rule, but
  this is a real qualitative mismatch worth a second look.

No other sheet states a numeric hilliness split, so no further diff is possible;
UNMEASURED for the remaining biomes' sheets against doctrine (their own text
doesn't commit to a number).

## 4. Named massifs

**(a) The Scald rim.** RUT_TheScald = 312 tiles (matches `the_one_map.md`'s "312
of unbroken Lake" exactly). 79 rim tiles (adjacent, non-Scald): elevation
min 1m / p25 187m / median 501m / p75 914m / max 1354m / mean 561m. Rim biome
mix: ZBiome_Badlands 23, AB_OcularForest 19, AB_FeraliskInfestedJungle 12,
ZBiome_DesertOasis 7, BiomeCypreJungle 7, ZBiome_Grasslands 4,
AB_PyroclasticConflagration 3, Volcano 2. **MEASURED: high ground on average**
(mean 561m vs. planet-wide land tiles), consistent with "mountain ring"
doctrine — though the 1m-elevation rim tile is a notable outlier worth a
manual look (one gap in the ring, or a river outlet notch per doctrine's
"spills through the one notch in the Spine").

**(b) The Forge massif** (Volcano+LavaField+AB_PyroclasticConflagration, 44
tiles). Elevation min 300m / median 1446m / max 2266m / mean 1516m. Its 2-hop
neighborhood (125 tiles, forge tiles excluded) has mean elevation 700.8m, max
2101m. **MEASURED: the Forge is the high ground of its neighborhood** — more
than double the mean elevation of the surrounding 2-hop ring.

**(c) 1-tile elevation spikes >800m above all six neighbors.** Count = **1**,
planet-wide: tile 5873, biome AB_PropaneLakes, elevation 1042m, sitting
1202m above its highest neighbor (six neighbors all between -200m and -160m —
this tile is a lone peak inside what is otherwise a below-sea-level propane
basin). Worth a manual look — either an intentional landmark or a paint
artifact.

## 5. Water bodies

Flood-fill over adjacency, water = elevation≤0: **1,458 tiles total (6.67% of
planet)**, 16 connected components. 4 bodies ≥8 tiles, 12 puddles (<8 tiles,
24 tiles total).

```
body#0  604 tiles  RUT_TwilightSea(479)+AB_MycoticJungle(54)+AB_RockyCrags(25)
body#1  465 tiles  RUT_GreySea(422)+AridShrubland(17)+Wasteland(12)
body#2  312 tiles  RUT_TheScald(312) — pure, matches doctrine exactly
body#3   53 tiles  RUT_PropaneLake(53)
```

Matches `the_seas.md`'s "Three named waters: the Twilight Sea..., the Grey
Sea..., and The Scald, a round crater lake" — the 4th body (RUT_PropaneLake,
53 tiles) is not one of the three named seas, consistent with it being a
chemical feature rather than a sea. `the_one_map.md`'s 2026-08-23 figure ("6.46%
water, 1412 tiles, exactly three bodies ≥8 tiles, 5 counting puddles") is
**superseded by tonight's data**: now 6.67% (1458 tiles), **4 bodies ≥8 tiles**
(RUT_PropaneLake crossed the ≥8 threshold since the last count) and **12
puddles**, not 2 — puddle count has grown materially since the doctrine's last
measurement. This is drift to flag to whoever owns `the_one_map.md`'s numbers,
not necessarily a defect.

Puddle biomes: ZBiome_Badlands 8, RUT_GreySea 7, RUT_PropaneLake 4, AB_TarPits
2, Desert 2, AB_RockyCrags 1. **UNMEASURED** whether any of these sheets "ban
standing water" — searched `the_cracked_lands.md`, `desert.md`, `the_sump.md`
for explicit water-ban language and found none; no sheet makes that claim in
words, so there is nothing to contradict.

## 6. Swampiness sanity

Biomes with mean swampiness >0.25: COMIGO_GreaterSwamp_Tropical (0.847, n=43),
AB_MiasmicMangrove (0.757, n=93), AB_FeraliskInfestedJungle (0.446, n=161),
BiomeCypreJungle (0.445, n=235), AB_MycoticJungle/"the Rot" (0.375, n=2258).
**No finding**: every one of these is a swamp/mangrove/jungle biome by name and
lore (checked `the_rot.md`, which explicitly describes "wet gloss on every
surface," "milky ponds," fungi that "own all the moisture they need" — wet by
design, not a dry biome mislabeled). No desert/wasteland/badlands biome
exceeds 0.25 mean swampiness.

## 7. Coastline quality (bodies >50 tiles)

```
body#0 Twilight Sea  area=604  perim_edges=494  perim/area=0.818  perim²/area=404.0
body#1 Grey Sea       area=465  perim_edges=412  perim/area=0.886  perim²/area=365.1
body#2 The Scald      area=312  perim_edges=154  perim/area=0.494  perim²/area=76.0
body#3 Propane Lake   area=53   perim_edges=84   perim/area=1.585  perim²/area=133.1
```

Using `the_one_map.md`'s own metric (perimeter²/area, circle≈12.6): all four
bodies sit well above a circle (76–404), i.e. none reads as an artificially
smooth disc. The Scald (76.0) is by far the smoothest of the four — 5x lower
than Twilight/Grey — which is exactly the doctrine's stated exception ("the
Scald is a crater, everything else stays torn"); Twilight and Grey Sea
(365–404) read as genuinely ragged/torn, matching intent. Propane Lake
(133.1, only 53 tiles) is high but that's expected noise at small N. **No
finding — coastline shapes match doctrine for all four bodies measured.**
