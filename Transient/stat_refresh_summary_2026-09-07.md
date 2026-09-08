# Biome sheet stat-refresh pass — 2026-09-07 (V12 canon)

Mechanical refresh of measured stat lines against `world/ASHKARR_WORLDMAP_tiles.csv`
+ `world/ASHKARR_WORLDMAP_links.csv`, re-derived independently with a Python script
(not just copied from `Transient/biome_sheet_stat_deltas_2026-09-07.md`), then
cross-checked against that report. Rulings, mechanisms and lore prose untouched;
🧊 FROZEN stamp blocks byte-identical (verified: no diff line touches a FROZEN block).

## Sheets edited (lines changed: added+removed, per `git diff --numstat`)

- `poison_forest.md` — 5+0. No prior MEASURED block; added one contradiction card
  on the θ ≈ 75-105° planetary-position claim.
- `deep_desert.md` — 11+6. Refreshed 6-region table (tiles/arc/temp), total
  3,035→3,594, Kiln biome split 418/412→418/414.
- `desert.md` — 2+2. Tile count 4,151→4,204 (19% unchanged); table temp 24.5→24.3°C.
- `arid_shrubland.md` — 12+5. Whole-def 748→633, core 361→329, flat fraction
  86%→73%; 1 contradiction card (core-region ranking, Thornbelt now outranks
  Grey Sea/Twilight Sea).
- `wasteland.md` — 3+3. Tiles 1,699→1,713, arc range refreshed; cross-referenced
  `AB_PropaneLakes` figure 554→987.
- `forsaken_crags.md` — 13+6. Tiles 1,225→1,984, temp floor −30→−81.7°C, water
  5→0; 1 contradiction card (Ammonia Flats/Umbra now the two largest regions,
  absent from the original list).
- `the_slime.md` — 3+3. Arc p90 99.1→98.5, dead-flat 88→91/96 (minor).
- `the_contagion.md` — 7+0. No number rewritten; 1 contradiction card (actual
  paint: 179 tiles vs. the ~210-tile candidate set, different region mix).
- `the_blue_desert.md` — 7+0. No number rewritten; 1 contradiction card (actual
  paint: 1,328 tiles across 8 regions vs. the "core 700–900" plan estimate).
- `the_propane_lakes.md` — 16+9. Tiles 1,589→987 (−38%), region reshuffle; 1
  contradiction card (Umbra "antistellar cap 332/360" claim now 59/262).
- `the_cracked_lands.md` — 14+7. Tiles 1,086→1,023, water 27→0, mountainous
  328→49; 1 contradiction card (both claims now false/collapsed).
- `weeping_stones.md` — 12+11. Tiles 236→223, hilliness reshuffled, river 1→2,
  region fraction "two-thirds"→61%, hash citation refreshed.
- `the_greentide.md` — 13+5. THE flagship card: 191→227 tiles, river coverage
  100%→84%. Original defining sentence left untouched; card added beneath it.
- `the_webwork.md` — 13+6. THE other flagship card: 172→169 tiles, river 0→8.
  Original defining sentence left untouched; card added beneath it. Also
  refreshed rain-bimodal split (99→96 zero-rain tiles).
- `the_scarlands.md` — 6+4. Temp 59.4→59.5°C; hilliness total unchanged (47/90)
  but category split moved — flagged as provisional on the unconfirmed enum
  mapping rather than asserted as a new finding.
- `the_rust_cathedral.md` — 6+5. Flat 211→217/236, river 8→10 (river-note
  applied).
- `the_miasma.md` — 7+3 (after fixing a mid-sentence insertion bug on
  re-verify). Tiles 92→93, river 32→31 (river-note applied); 1 contradiction
  card (6 stated sea tiles now 0).
- `the_fever_wood.md` — 3+3. Tiles 60→43 (−28%), now 100% flat, temp 45.7→45.5°C.
- `the_sump.md` — 5+5. Tiles 62→40 (−35%), temp 4.7→1.2°C, flat 82%→65%.
- `the_pyrelands.md` — 7+5. Tiles 226→222, Anvil 36→41, river 9→12 (river-note
  applied).
- `the_forge.md` — 4+3. Tile counts unchanged (all three defs); LavaField elev
  med 1,496→1,753 m.

## Sheets left untouched, and why

- `nightside_ice.md`, `the_rot.md` — delta report and my own recompute both
  show an EXACT match on every field (tiles, arc, temp, elevation, regions).
  Nothing moved, not even by noise; no line was stale.
- `dune_sea.md`, `terminator_sea.md` — no "MEASURED <date>" tagged stat block
  exists in either sheet (both are qualitative/candidate descriptions). Checked
  the one specific worry the delta report raised (region "Dune Sea" carrying 99
  river tiles against the "no water of any kind" ban) — that ban applies to the
  `ExtremeDesert` def itself, which measures 0 water/0 river exactly as stated;
  the 99 river tiles belong to the region's non-`ExtremeDesert` sub-biomes
  (jungle/oasis/mangrove), which the sheet's own "green line" exception already
  predicts. No contradiction.
- `the_scald.md` — every number (312 tiles, −350 m depth, 8 rivers) is an exact
  match. The temperature-figure mismatch the delta report flagged is judged a
  units mismatch (ambient air vs. tile temp_c), not a canon drift — not carded,
  per the delta report's own assessment.
- 8 sheets skipped per the task's explicit instruction (no worldmap presence or
  superseded): `fall_line.md`, `assailant_weapon_remnants.md`, `the_grey_deep.md`,
  `the_twilight_deep.md`, `wreck_fields.md`, `the_lantern_deeps.md`,
  `edible_genepack_native_mechanism.md`, `the_slime_gene_lists.md`.

## Contradiction cards added (verbatim), by sheet

**poison_forest.md** (§2, under the θ ≈ 75-105° line):
> ⚠️ MEASURED 2026-09-07 (V12 canon): 542 tiles, arc p10/med/p90 85.3/115.5/136.8°
> (the def now reaches 32° further past the terminator than this band describes) —
> contradiction card for the owner; the ruling text stands until ruled.

**arid_shrubland.md** (§2, under the "Damp, Grey Sea and Twilight Sea" region-ranking claim):
> ⚠️ MEASURED 2026-09-07 (V12 canon): core-band (arc 70–95) region ranking is now
> Damp 91, Thornbelt 80, Combs 42, Dew Belt 33, Grey Sea 29, Twilight Sea 12 —
> Thornbelt now outranks Grey Sea and Twilight Sea — contradiction card for the
> owner; the ruling text stands until ruled.

**forsaken_crags.md** (§0):
> ⚠️ MEASURED 2026-09-07 (V12 canon): Ammonia Flats and Umbra are now the two
> largest regions in this def (342 and 267 tiles), absent from the original
> region list; the temperature floor dropped from −30 °C to −81.7 °C and the
> stated 5 water tiles are now 0 — contradiction card for the owner; the
> ruling text stands until ruled.

**the_contagion.md** (§0, under the candidate set):
> ⚠️ MEASURED 2026-09-07 (V12 canon): `AB_OcularForest` as actually painted holds
> **179 tiles** — Dew Horn 87, Scald Spine 44, Ashfall Range 24, Dune Sea 17,
> Fall Line 5, Anvil 2 — a different population than the candidate set above
> (Dew Horn got far fewer than the optional 137, and 22 tiles landed in
> Dune Sea/Fall Line, absent from the candidate list) — contradiction card for
> the owner; the ruling text stands until ruled.

**the_blue_desert.md** (§0, under the dissolve-plan paragraph):
> ⚠️ MEASURED 2026-09-07 (V12 canon): `BiomeGRimond` (this def) is now painted at
> **1,328 tiles** — well above the "core 700–900" estimate above — across 8
> regions (Deadstone 986, South Crags 93, Umbra 86, Thornend 61, Lantern Deeps
> 57, Nightspill 17, Ammonia Flats 13, Sunreach 6), where this plan described
> one ring; arc now p10 126.7/med 137.1/p90 148.8, temp med −45.3 °C, elev med
> 597 m — contradiction card for the owner; the ruling text stands until ruled.

**the_propane_lakes.md** (§0):
> ⚠️ MEASURED 2026-09-07 (V12 canon): tile count dropped 1,589→987 (−38%) and
> Deadstone overtook Umbra as the second-largest region (Ammonia Flats 362,
> Deadstone 360, Umbra 262 — all roughly halved/reshuffled from the stated
> 732/558/299); the "Umbra IS the antistellar cap: 332 of 360 tiles at arc
> ≥165" claim is now 59 of 262 — contradiction card for the owner; the ruling
> text stands until ruled.

**the_cracked_lands.md** (§0):
> ⚠️ MEASURED 2026-09-07 (V12 canon): the "no standing surface water beyond the
> measured 27 tiles" claim is now false (0 water tiles), and the mountainous
> fraction the fauna/relief story was built on collapsed from 328 to 49
> (328→49, −85%; large-hill grew 197→359 in its place) — contradiction card
> for the owner; the ruling text stands until ruled.

**the_greentide.md** (§0, the flagship claim — sentence left untouched):
> ⚠️ MEASURED 2026-09-07 (V12 canon): 227 tiles, of which 191 (84%) are river
> tiles — 36 non-river tiles now exist, so the "every single one is a river
> tile" claim no longer holds — contradiction card for the owner; the ruling
> text stands until ruled.

**the_webwork.md** (§0, the flagship claim — sentence left untouched):
> ⚠️ MEASURED 2026-09-07 (V12 canon): 169 tiles, 8 river tiles (per canon links
> CSV; live world carries +9 unattributed edges — see meander_v12/REPORT.md), 0
> water tiles — the "0 river tiles" claim no longer holds — contradiction card
> for the owner; the ruling text stands until ruled.

**the_miasma.md** (§0):
> ⚠️ MEASURED 2026-09-07 (V12 canon): the 6 stated "sea tiles" are now 0 —
> contradiction card for the owner; the ruling text stands until ruled.

## Verification method

Wrote `biome_stats.py` (scratchpad), validated it against `nightside_ice.md`'s
already-exact figures (802 tiles, arc 128.1/159.1, elev med 1,128.5, regions —
all matched exactly), then used it to independently recompute every def's tiles,
arc percentiles, temp med/min/max, elev med/max, hilliness histogram (cat 0–5),
water count, river-link membership count, and region breakdown. Where the region
filter in a sheet was "any biome in region X" rather than "def X" (e.g.
`deep_desert.md`'s 6-region table), recomputed on that exact filter and confirmed
it matches the delta report's totals (3,594 tiles, arc p10/med/p90
44.6/60.6/77.8, hilliness 2044/1258/292) before writing it into the sheet.
Re-read every edited file's diff after writing and caught one bug on
re-verification: the `the_miasma.md` card was first inserted mid-parenthetical,
splitting "(tile 6645, 29 m," from "27 °C)" — fixed before this summary was
written.

## UNKNOWN

- **Hilliness 1–5 enum mapping** is still unconfirmed against a def/enum source
  (inherited from the delta report's own UNKNOWN). Where a sheet's hilliness
  *split* moved but the *total* did not (`the_scarlands.md`), left the split
  un-asserted rather than risk propagating a wrong category label.
- **`deep_desert.md`'s "from water" column** (degrees of arc to nearest water) —
  not re-derived; it requires a geodesic nearest-water-tile computation the CSVs
  don't give directly, and neither the delta report nor this pass computed it.
  Left as the sheet's prior stated values (unmeasured this pass).
- **`wasteland.md`'s per-family (dayside basins / margin / dark scour) arc-temp-
  elev sub-ranges** — spot-checked and found real drift beyond the delta
  report's aggregate-only "not material" verdict (e.g. elevation ranges now
  overlap heavily across families where they were previously distinct bands).
  Deliberately NOT rewritten: the delta report never assessed this sub-table,
  my region-name mapping confidence is lower for a 3-way family split than for
  a single def, and rewriting risked introducing a worse error than the
  existing staleness. Flagged here for a follow-up pass rather than edited blind.
- **`forsaken_crags.md`'s Lightfall-chasm tile citations** (specific tile IDs,
  e.g. tile 9023) — spot-checked one (hilliness now reads 4, not the stated 5;
  elevation matches exactly at 919 m) but left untouched: this is a landmark
  citation embedded in mechanism prose, not a biome-population stat, and the
  single-category hilliness drift is exactly the kind of enum-mapping noise
  flagged above.
