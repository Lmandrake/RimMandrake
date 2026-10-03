# WORLDVIEW_MISLABEL_FALLOUT_1 — audit, 2026-10-02

Audit only (BENCH helper, owner away). No bridge, no item verbs, no code edits.

## 1. Is the bug fixed? — FIXED

- Fix commit `1a96f1e2a` (2026-09-21 01:24 -0700), an ancestor of `origin/main`.
- `src/RimMandrake/Utils/worldmap.py:405-420` — `features()` returns `uid` (the
  `<uniqueID>`) beside the list `index`.
- `src/RimMandrake/Utils/worldview.py:196-203` — `PlanetView` remaps the raw `tileFeature`
  values through `_uid2pos` once, so every consumer (label placement at `:1181`, settlement
  `region` at `:381`, body `named` at `:347`, tooltips at `:989`) joins on list position.
- The only other `tileFeature` readers, `world_label_curve.py` and
  `feature_drawcenter_audit.py`, were written after the fix (2026-09-25) and key on uid.
- Uid offsets of the committed saves (measured now with `worldmap.WorldObjects`):
  `ASHKARR_DRAFT_2026-08-24.rws` +21, `WORLDMAP_V1_original.rws` +21, `WORLDMAP_gen.rws`
  +18, `WORLDMAP_sub7b_source.rws` 0, `WORLDMAP_source.rws` 0. The bug only bit the offset
  ones.

## Key finding: the blast radius is much smaller than the item said

The item said "every region label on every Ash'karr render" was wrong. That is false.
`worldview.py` has two loaders. `PlanetView` reads `.rws` and had the bug. `BundlePlanet`
(`worldview.py:673-735`) reads a bundle (`world/ASHKARR_WORLDMAP`, the normal authoring input
since 2026-08-18). It builds membership from the CSV `region` column and never reads
`tileFeature`. Bundle renders were always labelled correctly.

Census of every worldview `*.report.json` ever committed before the fix (git history,
including deleted Transient files): **39 reports, 35 bundle-sourced, 4 `.rws`-sourced.**
Of those 4, one is the fix commit's own output, made with the fixed code. One is
`WORLDMAP_sub7b_source` (offset 0, unaffected). The other two are `WORLDMAP_ashkarr.rws` /
`WORLDMAP_ashkarr_v2.rws` from `04e36f443` (2026-08-19), both pre-gazetteer worlds that have
since been replaced. The v2 report shows the bug's signature (`The Rust Cathedral` 0 tiles).

## 2. Conclusions drawn from pre-fix renders

| source file:line | conclusion | verdict | evidence |
|---|---|---|---|
| `infrastructure/state/items/WORLDVIEW_MISLABEL_FALLOUT_1.md:1,7-9` | "every region label on every Ash'karr render pointed at the wrong region" | **FALSE — corrected** | Bundle loader never reads `tileFeature`; 35 of 39 pre-fix reports were bundle-sourced (census above) |
| `infrastructure/state/handoffs/BENCH_REBOOT_HANDOFF_202609210912.md:70` | same "every Ash'karr render" claim | **FALSE — corrected** | same |
| `skills/rimworld-world-editing/references/savegame-editing.md:187` | `tileFeature` = "index into `world/features`" | **FALSE — corrected** | the root misreading itself; the uid offset of +21 was measured on the committed Ash'karr saves |
| `world/view/WORLDMAP_ashkarr{,_v2}.report.json` @`04e36f443` (2026-08-19) | per-region tile counts / labels on the pre-gazetteer Ash'karr saves | **wrong at the time, now moot** | the v2 report lists `The Rust Cathedral` at 0 tiles, which is the bug's signature; that planet was rebuilt from the gazetteer CSV on 2026-08-18/19, so no live conclusion rests on it |
| `name_ashkarr_regions.py` @`41ac15cf2` (2026-08-16, file since deleted) | wrote `tileFeature[t] = k` (list position) into the save | **same id-vs-index error, write side, now moot** | that world was replaced; today's features come from the C# `jawa/world_features_import` (engine-side), and the fix commit measured save-vs-CSV membership at Jaccard 1.000 on all 71 |
| same script's docstring | drawCenter convention `(cosLat*sinLon, sinLat, -cosLat*cosLon)*100`, fitted against member-tile centroids | **still true** | re-verified after the fix by `feature_drawcenter_audit.py:_selfcheck_transform`, which joins on uid and refuses to run unless the known-good features align |
| `design/Jawa/worldbuilding/the_one_map.md:102-110` | tidal lock is a point (corr(T, arc) −0.98), measured with worldview on `WORLDMAP_ashkarr` | **still true, unaffected** | uses temperature and tile geometry only, no feature membership; also reconciled against the mod's C# (same doc, 2026-08-20) |
| `world/audit_2026-08-26/README.md` ("nine empty regions", E-regions fills) | regions found empty and then filled | **unaffected** | bundle form (`AFTER_*.csv`), README line 9-10 |
| `world/_audit/report_body.html` (POST_FREEZE audit, 2026-09-11) | 71 WorldFeatures vs CSV regions | **unaffected** | already resolved `tileFeatureDeflate` through the uniqueID map (report lines 90-91) |
| `world/_label_audit.py` @`2174503fe` (V19 nightside renames, 2026-09-08) | four nightside labels renamed to match their terrain | **unaffected** | membership from the live bridge (`jawa/world_features_get`) plus the CSV `region` column, not worldview or `tileFeature` |
| `infrastructure/state/items/closed/WORLD_FEATURE_LABELS_OVERSIZED_1.md` (2026-09-19) | label-size formula; Dune Sea 1,692 / Deadstone 2,051 tiles | **unaffected** | counts come from the CSV and the C# importer, and match the fixed renderer's numbers in `1a96f1e2a`. Tile counts are not evidence of design state anyway |
| `LIQUID_BIOMES_MAP_1` note (2026-09-07) "region Scald, 312 tiles" | which region is the boiling ocean | **unaffected** | taken from the bundle/CSV region column |
| Biome sheets, `the_one_map.md` and the Transient biome renders (contagion, horrorwastes, fungalforest, blue desert, final_review; 2026-09-07..11) | biome/colour/placement judgments | **unaffected** | all bundle-sourced (`save` field = `ASHKARR_WORLDMAP*` CSV) |
| `Transient/world_label_hierarchy_2026-09-21.md` + `fall_line_major_region_label.md` | label hierarchy, Fall Line span | **unaffected** | produced in the fix commit with the fixed code |
| Uncommitted ad-hoc `.rws` renders of `CANONICAL_ASHKARR_START_2026-09-12.rws`, 2026-09-12..09-21 | anything | **cannot tell** | no committed artifact, item, ledger note or handoff from that window cites one. If such renders existed they left no recorded conclusion |

**Counts:** 3 false (corrected) · 2 wrong-at-the-time but now moot (superseded planet) ·
9 still true or unaffected · 1 cannot tell (unrecorded renders, with no conclusion on record).

## Can the item close?

Yes. It meets the criteria: every label-bearing worldview artifact is listed and
classified, and no conclusion still standing rested on a mislabelled region. There is
nothing to bring to the owner. The proof is the loader split plus the 39-report census
above, and the fix is `1a96f1e2a`, which is an ancestor of `origin/main`.
