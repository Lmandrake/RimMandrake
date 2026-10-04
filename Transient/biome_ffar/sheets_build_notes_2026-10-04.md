# Biome FloraFauna Art Review — per-biome sheets (BIOME_FLORAFAUNA_ART_REVIEW_1)

Built 2026-10-04 from census `git_head 79c294972` (Baroque Biomes RM_ scope). NOT served — BENCH hands them over.

## Rebuild command (picks up finished artpipe renders)
    python3 src/RimMandrake/Utils/art/art_sheet.py --refresh --biome first3 --date 2026-10-04
`--refresh` = `art.py backfill artpipe` (~45 s) + `biome_census.py`; sheets ~4 min for three biomes (thumbs cached in `img/`).
Letters stay stable across re-runs (read back from the previous snapshot); an untouched prefill decisions file is
regenerated, a sidecar-written one is never overwritten. Serve: `serve_sheet.py --sheet <html> --decisions <json>`.

## Per-sheet counts
| sheet | rows (census) | canon rows w/ images + Must show | linked rows on sheet | prefilled from desert sitting 1 | NO ART YET |
|---|---|---|---|---|---|
| desert_sheet (RM_LongShade) | 75 (75) | 34 / 34 | 0 | 40 | 0 |
| deep_desert_sheet (RM_Stillsand) | 28 (28) | 6 / 6 | 0 | 2 | 0 |
| blue_desert_sheet (RM_BlueDesert) | 20 (20) | 0 | 0 | 0 | 2: AA_Thunderbeast, Vapaad |

## Notes
- Linked pairs are 0 because under the RM_-only scope every census twin (e.g. RM_Ommok -> RSW_Ommok, 14 on LongShade)
  is NOT on that biome's roster; each such row shows "also related, not in this biome: RSW_X". In-sheet two-way links +
  shared group/colour band are built and selftested, and fire whenever both rows sit on one sheet.
- Blue Desert's 6 other census no-art rows (Dorrak, Krissek, Vekkit, Chimeglobe, Glassfern, Palefloss) DO have renders
  in the ledger; the builder joins them by name ("renders found by NAME") and prefills the newest (marked ⚠).
- Rows with a second graphic (swimming/flying) get their own strip; a header click there records `picks` per graphic;
  ingest.py records those as keep rulings too.
- Verified: check_sheet 0 FAIL on all three; desert served on a scratch decisions copy and rendered in headless Chrome:
  75 rows, no console errors. NOT done: clicking controls in a real browser (headless dump only).
