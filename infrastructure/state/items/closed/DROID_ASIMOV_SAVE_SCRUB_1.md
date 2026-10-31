
## done (BENCH via Opus subagent, 2026-09-06 — owner-authorized: "remove the troublesome spots in WORLDMAP_v1_original.rsw_(most recent letter available)... Same for the gravship family")
- `Saves\WORLDMAP_V1_original_c.rws`: `Asimov.Need_Energy` 82 → 0 (10,588 bytes, 328 lines removed).
- `Saves\gravship_scratch_d.rws`: 133 → 0 (17,020 bytes, 532 lines).
- Text-line surgery only (no XML re-serialization; grids byte-identical); 5 droids left with an empty `<needs></needs>` — verified equivalent to `<needs />` under RimWorld's loader.
- ⚠️ Residue NOT touched: 75 / 71 other `Asimov` occurrences (Workgiver names, research/techprint and blueprint registries, one `Asimov.WorldComp_EnergyNeed` world component). If Asimov's retirement makes those log, that is a separate pass — D4 (`DROID_RETIRE_DEPOT_ASIMOV_1`) must check the load log for them.
- Untouched: `_b`, gravship `_b/_c`, `Autosave-1`, and the repo's `world/WORLDMAP_V1_original.rws` (still 82 — the owner loads only the latest letters).

Recount, 2026-10-31, on copies: 82 and 133 hold, and so do both byte and line totals, from `world/WORLDMAP_V1_original.rws`, `WORLDMAP_V1_original_b`, `gravship_scratch_b` and `_c` against the scrubbed `_c` / `_d` (now in `D:\Luke\dev\RimMandrake\Transient\droidworks_detonation_review\saves_backup_20260908_085545\`). Residual `Asimov` strings 75 and 71; the 5 droids are the worldmap's. The `.bak-asimov-20260906` backups no longer exist anywhere on D: or in the Saves tree, so a deletions-only diff cannot be re-run (`ASIMOV_SCRUB_BACKUPS_RESTORE_LOST_PAIR`). The 0 did not last while Asimov stayed loaded: `gravship_scratch_e` 22, `WORLDMAP_V1_original_e` 61. Current canon R3 has 0.
