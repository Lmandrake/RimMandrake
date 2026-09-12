# CANON_CENSUS_RECOUNT_2026-09-12 — fresh re-census against the frozen worldmap CSV

Closes the "gaps honest" list in `infrastructure/state/items/CANON_PLANET_CENSUS_1.md`'s
"Sitting prep 2026-09-12" section, per `Transient/CANON_PLANET_CENSUS_1_replacement_block.md`.
Read-only measurement task — no files edited, nothing committed.

## Instrument

- File: `world/ASHKARR_WORLDMAP_tiles.csv` (confirmed as the path named in the item/prep files;
  no other candidate CSV found).
- **sha256**: `756d9ffc8a22c3d220ada5988df7d89527685766344d63cc667664cf28ee6bb7`
- **sha256_12**: `756d9ffc8a22`
- **Row count** (data rows, header excluded): **21872** — matches `tiles: 21872` already in
  canon.yml / the replacement block.
- Columns (header row, verbatim): `tile, lat, lon, arc, bearing, elev_m, temp_c, rain_mm, biome,
  water, river_flow, region, hilliness, swampiness`
- Parsed with Python's `csv.DictReader` only. No grep/wc/awk was run against this file.

All numbers below are **MEASURED-from-this-CSV** unless explicitly marked otherwise.

---

## 1. Per-biome tile counts — ALL 29 biomes present (complete table)

| biome | tiles | pct of 21872 |
|---|---:|---:|
| ExtremeDesert | 3969 | 18.146% |
| AB_PropaneLakes | 2531 | 11.572% |
| Desert | 2390 | 10.927% |
| AB_MycoticJungle | 2204 | 10.077% |
| Wasteland | 1853 | 8.472% |
| RUT_NightsideIce | 1506 | 6.886% |
| AB_RockyCrags | 1135 | 5.189% |
| RUT_BlueDesert | 1029 | 4.705% |
| ZBiome_Badlands | 970 | 4.435% |
| AridShrubland | 628 | 2.871% |
| RUT_TwilightSea | 607 | 2.775% |
| PoisonForest | 546 | 2.496% |
| RUT_GreySea | 472 | 2.158% |
| RUT_TheScald | 312 | 1.426% |
| AB_MechanoidIntrusion | 236 | 1.079% |
| BiomeCypreJungle | 235 | 1.074% |
| ZBiome_DesertOasis | 223 | 1.020% |
| ZBiome_Grasslands | 222 | 1.015% |
| AB_OcularForest | 179 | 0.818% |
| AB_FeraliskInfestedJungle | 161 | 0.736% |
| AB_GelatinousSuperorganism | 96 | 0.439% |
| AB_MiasmicMangrove | 93 | 0.425% |
| Scarlands | 90 | 0.411% |
| RUT_PropaneLake | 57 | 0.261% |
| COMIGO_GreaterSwamp_Tropical | 43 | 0.197% |
| AB_TarPits | 41 | 0.187% |
| AB_PyroclasticConflagration | 31 | 0.142% |
| LavaField | 8 | 0.037% |
| Volcano | 5 | 0.023% |
| **TOTAL** | **21872** | **100.000%** |

MEASURED-from-this-CSV. Sum of all rows equals the file's row count exactly (21872 = 21872) — no
biome value was blank, unparsed, or dropped.

Note (not asked for, offered as a correction): `PoisonForest` = **546** in this CSV, matching the
item's 2026-09-12 addendum figure ("546, frozen CSV, 2026-09-11") exactly. Discrepancy #1 in
`Transient/CANON_PLANET_CENSUS_1_replacement_block.md` (546 "does not appear anywhere in
post_freeze_2026-09-11.json") is real for that json, but this CSV — the declared sole census
instrument — does independently support 546. Vanilla `Ocean`, `Lake`, `SeaIce`, `IceSheet` are
**absent from the CSV entirely** (0 rows, not merely 0 in some other table) — consistent with the
post-freeze audit's "now 0" verdict.

---

## 2. Distinct biome count — 29, not 30

**MEASURED: 29 distinct `biome` values in the CSV.** This settles the item's 29-vs-30 question in
favor of **29** (matching `biomes_on_map: 29` already in canon.yml / the replacement block) — but
NOT by the arithmetic the item guessed at ("naively removing 4 zeroed vanilla biomes from the old
28-row list and adding the 6 new RUT_* rows gives 30"). That arithmetic used a set of 24 legacy
non-RUT biome names (the old 28-row table minus Ocean/Lake/SeaIce/IceSheet) plus the 6 new RUT_*
names = 30 names. Comparing that 30-name expected set against the CSV's actual 29 names, by exact
set difference:

- **Present in the old/expected list but ABSENT from the live CSV (3 names):**
  `BMT_CrystalCaverns`, `BMT_FungalForest`, `HorrorWastes`
- **Present in the live CSV but NOT in the old/expected list (2 names):**
  `BiomeCypreJungle`, `COMIGO_GreaterSwamp_Tropical`

Net: 30 (expected) − 3 (dropped) + 2 (new) = **29 (measured)**. This is **not a single rename** —
it is three legacy biomes no longer on the map plus two biomes not in the item's legacy list. Named
here per the task's instruction rather than guessed at; which of the three drops (if any) is a
rename target for `BiomeCypreJungle`/`COMIGO_GreaterSwamp_Tropical` is UNKNOWN from this CSV alone
(would need the mod/def history, not tile data).

Full list of the 29 live biome names (alphabetical), for reference:
`AB_FeraliskInfestedJungle, AB_GelatinousSuperorganism, AB_MechanoidIntrusion, AB_MiasmicMangrove,
AB_MycoticJungle, AB_OcularForest, AB_PropaneLakes, AB_PyroclasticConflagration, AB_RockyCrags,
AB_TarPits, AridShrubland, BiomeCypreJungle, COMIGO_GreaterSwamp_Tropical, Desert, ExtremeDesert,
LavaField, PoisonForest, RUT_BlueDesert, RUT_GreySea, RUT_NightsideIce, RUT_PropaneLake,
RUT_TheScald, RUT_TwilightSea, Scarlands, Volcano, Wasteland, ZBiome_Badlands, ZBiome_DesertOasis,
ZBiome_Grasslands`

---

## 3. rivers_tiles — per-column count (not adjudicated)

The CSV has exactly **one** river-related column: `river_flow`. There is no second river column
(no `river`, `has_river`, `river_id`, etc.) in this file to cross-check against.

| definition | count | note |
|---|---:|---|
| `river_flow` not equal to 0 (parsed as float; `'0'` and `'0.0'` both treated as zero) | **298** | matches the audit's own "CSV river_flow non-zero on 298 tiles" figure exactly |
| `river_flow` equal to 0 | 21574 | — |
| unparseable / blank `river_flow` values | 0 | every value parsed as a float cleanly |

The other three figures named in the item's disagreement (326 river edges over 217 distinct origin
tiles; the recorded canon.yml value of 254) are **not derivable from this CSV** — they come from a
different instrument (engine/save-side river-edge topology read via a `jawa/world_*` bridge call,
per the item's own text), which this CSV does not encode. This report states only what this CSV
contains: **298** tiles with nonzero `river_flow`. It does NOT adjudicate 298 vs 217 vs 326 vs 254
— that requires the live bridge read the item already flags as owed.

---

## 4. Water tiles and water_pct

**Classification used:** two independent methods on this CSV, cross-checked tile-for-tile — they
agree exactly.

- **Method A — the CSV's own `water` column** (binary, values only `0`/`1` observed, no other
  values): count of `water == 1`.
- **Method B — by `biome` name**: tiles whose biome is one of the four water biomes present or
  formerly present in this lineage — `RUT_TheScald`, `RUT_TwilightSea`, `RUT_GreySea`,
  `RUT_PropaneLake` (plus vanilla `Ocean`, `Lake`, `SeaIce`, `IceSheet`, all at 0 rows in this CSV).

| method | water tiles | water_pct (of 21872) |
|---|---:|---:|
| A: `water` column == 1 | **1448** | **6.6203%** |
| B: biome-name water set | **1448** | **6.6203%** |

Both methods return the identical 1448-tile set (verified: every `water==1` row's biome is one of
`RUT_TheScald` (312), `RUT_TwilightSea` (607), `RUT_GreySea` (472), `RUT_PropaneLake` (57) — sums to
1448 exactly; no row with `water==1` carries any other biome, and no row with `water==0` carries one
of those four biome names). This reconfirms the post-freeze audit's `water_tiles: 1448` and, unlike
that audit, gives a **MEASURED water_pct: 6.6203%** (1448 / 21872 × 100), which the audit itself
declined to state (it gave tile counts only, not a percentage).

**Incl-ice variant:** `RUT_NightsideIce` (1506 tiles) is the one ice biome present on the map. In
this CSV's own `water` column, **every `RUT_NightsideIce` row is `water == 0`** — the CSV classes
ice as land, not water. Reporting the incl-ice variant the item's addendum implies (the old
liquid+ice-split framing) for completeness only, explicitly built by adding the ice biome to the
water set rather than reading it off any column:

| variant | tiles | pct |
|---|---:|---:|
| water only (methods A/B) | 1448 | 6.6203% |
| water + RUT_NightsideIce (incl-ice) | 1448 + 1506 = **2954** | **13.5059%** |

The incl-ice row is arithmetic on this CSV's own biome counts, not a value the CSV encodes directly
(the CSV's `water` flag does not mark ice as water) — flagged as such rather than presented as
equivalent to the water-column reading.

---

## Definitions (every classification choice made in this report)

- **Row count / instrument scope**: 21872 data rows (header excluded), read via `csv.DictReader`.
  No line-oriented tool (`grep`/`wc`/`awk`) was used on this file, per the task's instrument rule.
- **Per-biome counts**: exact string match on the `biome` column value, case-sensitive, no
  normalization or grouping of similarly-named biomes (e.g. `AB_PropaneLakes` and `RUT_PropaneLake`
  are counted as two distinct biomes, not merged).
- **Distinct biome count**: number of unique `biome` string values across all 21872 rows.
- **rivers_tiles**: `river_flow` column parsed as a float per row; "has river" = value != 0.0.
  Values written as `'0'` and `'0.0'` are both treated as zero. No other river-indicating column
  exists in this CSV.
- **Water classification**: a tile is "water" if its `water` column reads `1` (equivalently, if its
  `biome` is `RUT_TheScald`, `RUT_TwilightSea`, `RUT_GreySea`, or `RUT_PropaneLake` — verified
  identical sets). Vanilla `Ocean`/`Lake`/`SeaIce`/`IceSheet` biome names were checked and are
  absent from the CSV (0 rows each), consistent with them being retired from the map.
- **Ice classification**: `RUT_NightsideIce` is the only ice-named biome on the map; the CSV's
  `water` column does NOT mark it as water (all 1506 rows read `water == 0`). The "incl-ice"
  water_pct variant is this report's own addition (water tiles + RUT_NightsideIce tiles), stated
  separately and not implied to be a value the CSV itself encodes.
- **water_pct**: tile count / 21872 × 100, to 4 decimal places. This computation is arithmetic
  performed on numbers this CSV directly contains (a tile count and the total row count), not an
  imported figure from any other source.

## UNKNOWN

- Whether `BiomeCypreJungle` and/or `COMIGO_GreaterSwamp_Tropical` are renames of one or more of
  `BMT_CrystalCaverns`, `BMT_FungalForest`, `HorrorWastes`, or are unrelated new biomes — not
  determinable from tile data alone.
- Reconciling `river_flow`-nonzero (298, this CSV) against the engine-side 326/217/254 figures —
  this CSV does not encode river-edge topology; a live `jawa/world_*` bridge read is still owed per
  the item's own text.
