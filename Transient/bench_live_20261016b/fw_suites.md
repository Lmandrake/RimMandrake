# FlowWorks live suites, ratchet_pilot tier (21 mods), 2026-10-16, bench HEAD 602513b5e1 (export `D:\Luke\dev\_rmscratch\fw_export_0b`)

## HARNESS fault that blocked the first run (class, not a mod bug)
`Utils/modcheck/test_site_saves.py:388` `load_game` gives no `ignoreModCompatibility`; the calm save records 22 mods (incl. Alpha Animals `sarg.alphaanimals`), the tier has 21, so the load answers `save.missing_mods` and v2 ABORTs after 420 s (L0 FAIL SITE, 1 PASS / 2 FAIL). Re-run with that one argument added in the export copy only (not committed to the repo): load clean. river save loaded without it. Fix owed: re-save the calm site on the tier or pass the flag.

## validation_v2 --live (calm site) : 59 PASS / 2 FAIL / 0 UNMEASURED (61 rows; baseline 61/61). Result `validation_v2_result.json`
| row | class | evidence |
|---|---|---|
| L2_tier_live | HARNESS | "settings table misses C# toggles: joinFittings, pipeLinksIntoMachines, waterBodyTypeFlipFixEnabled" - three new settings not yet in the script's table; no behaviour read |
| P4b_ladder_raised_strands | HARNESS (stale oracle string) | every behavioural half is right: raised held True, lip 0/8, ordered-out canReach False; lowered held False, lip 8/8. Only the inspect-line prefix test fails: it expects `ladder_up`/`ladder_down` but the line now reads `Slid up onto the rim: nobody can climb down or out.` / `Ladder down: your people climb...` (reworded by the 2026-10-16 wall-ladder change) |
Log budget E9 PASS (0 FlowWorks errors, 0 ledger imbalances, 1 sanctioned exception). Litres/level-by-surface rows (A/B/C/R, X*, oracle==kernel) all PASS.

## extension_proof --live --site river : 20 PASS / 0 FAIL / 1 UNMEASURED (baseline 20/0/1). Result `extension_river_result.json` (UNMEASURED is the by-design first_find letter; not re-read by name).

## fw_live_checks.py (ledger harness, --fresh-map, no --theft-day) : 14 PASS / 7 FAIL / 10 UNMEASURED. Result `fw_live_checks_result.json`
Statuses are IDENTICAL to the 2026-10-11 final run (`Transient/bench_live_20261011/fw_live_checks_result3.json`) row for row: no regression, but the open ledger criteria stay open.
| row (criterion) | status | class |
|---|---|---|
| L2 dump drains with no pump (A3); L2 pump pour fast | FAIL, tank stays 100, drained 0 | MOD (presumed, unproven; same as 10-11 "pump pour rate" finding. Tank scale 100 may also be stale after litres: HARNESS possible, untraced) |
| L4 ship tank fill / empty (A5) | FAIL | MOD presumed (as 10-11); L4 real gravship UNMEASURED SITE |
| L5 switched-off hose spills (A6) | FAIL (filth 0 in rect, spilled units 102/10102) | MOD presumed; L5 colonists clean UNMEASURED SITE (no filth) |
| L6 theft spotted letter (A7) | FAIL (letters [], caught 0) | MOD (10-11 filed "liquid theft LOS"); L6 goodwill-after-a-day UNMEASURED (needs --theft-day) |
| W1 wakes terrain walked | FAIL (terrainUnder Soil, accepted null) | HARNESS (site shows Soil under all three walkers, so no liquid was walked; block new since 10-11, untraced) |
| W1 look / counter, B1 bottles, P1 hot pit, P1/R1 blocks, R1 save-load | UNMEASURED | HARNESS/SITE: starvation GovernorStop after the 14k-tick advances, no instrument for wakes, no pipe built |
PASS: L1, L3 (A4 intake needs pump), L6 foreign tank / free-end names faction, D1 x4 (sluice on wet canal, survives flooding), P1 x3, T1 worst tick 0.021 ms.

## Not run / no live path
- door facing, flow_map_controls(_six): the validation.py chains' `*_live` components are hard-coded UNMEASURED placeholders (offline selftests only); live needs `jawa/static_call RM_MapControls.PlaceSource/PlaceSink` by hand: NOT done (bridge time).
- lacquer bill chain: no `lacquer_bill` chain exists in validation.py or extensions.py; NOT done.
- review-map labels `8:` and `9:` (REVIEW_MAP_LABELS_FIX_ORPHANS_ADOPTED): `review_map.py --labels` added 463 labels, refused []; a `jawa/review_label list` read-back holds `8: the same drained pond with a muffalo standing` / `8: in its bed` and `9: a pond feeding a water canal, with a fill-in` / `9: order on the canal's far end`. PASS (on the calm-site map, not the built review map).

## Re-check

Run on ratchet_pilot tier, calm map RM_TestSite_calm_v1, after pull (already up to date).

- validation_v2.py --live: GREEN, 61 PASS / 0 FAIL / 0 UNMEASURED (result validation_v2_result_20261016T125532.json). Both earlier HARNESS fails now pass.
- liquid_checks.py --fresh-map --only L2,L4,L6 --theft-day: 8 PASS / 0 FAIL / 2 UNMEASURED (liquid_checks_result_20261016T125537.json). L2 x2, L4 fill/empty, L6 foreign tank / theft letter / free-end faction all PASS.
  - L4_on_a_real_gravship UNMEASURED, SITE: no gravship fixture on a quicktest map; a plain RM_UniversalCargoTank stands in (no ship-tank def exists).
  - L6_block UNMEASURED, HARNESS: GovernorStop, safe_advance stopped at 1200/1500 ticks, colonist Kiyoshi (843) Starving (seq 39, tick 47904), after the three L6 rows had already passed. Fresh map's unfed colony starved during the theft-day advance; the trailing block, not a mod row.
- L5 skipped (needs deploy+restart). Game returned to calm map (test_site_saves load calm: CLEAN), paused.
