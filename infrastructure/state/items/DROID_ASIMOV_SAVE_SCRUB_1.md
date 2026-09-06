
## done (BENCH via Opus subagent, 2026-09-06 — owner-authorized: "remove the troublesome spots in WORLDMAP_v1_original.rsw_(most recent letter available)... Same for the gravship family")
- `Saves\WORLDMAP_V1_original_c.rws`: `Asimov.Need_Energy` 82 → 0 (10,588 bytes, 328 lines removed; full diff = deletions only). Backup `WORLDMAP_V1_original_c.rws.bak-asimov-20260906`.
- `Saves\gravship_scratch_d.rws`: 133 → 0 (17,020 bytes, 532 lines). Backup `gravship_scratch_d.rws.bak-asimov-20260906`.
- Text-line surgery only (no XML re-serialization; grids byte-identical); 5 droids left with an empty `<needs></needs>` — verified equivalent to `<needs />` under RimWorld's loader.
- ⚠️ Residue NOT touched: 75 / 71 other `Asimov` occurrences (Workgiver names, research/techprint and blueprint registries, one `Asimov.WorldComp_EnergyNeed` world component). If Asimov's retirement makes those log, that is a separate pass — D4 (`DROID_RETIRE_DEPOT_ASIMOV_1`) must check the load log for them.
- Untouched: `_b`, gravship `_b/_c`, `Autosave-1`, and the repo's `world/WORLDMAP_V1_original.rws` (still 82 — the owner loads only the latest letters).
