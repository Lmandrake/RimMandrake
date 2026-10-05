# Sheet join fix 2026-10-05 (ART_SHEET_DONOR_JOIN_GAPS_1)

Skeleton. Sections: root cause / fix / failed-canon badge / selftest / rebuild results / donor-only remaining.

## Coverage of the 157 donor-only rows (matched through subject.py; jobs in _artpipe pending/active)
- Already covered by a pending/active job: 91
- Owner-ruled, skipped: 19
- Newly queued: 47 flora jobs `gapfin_<def>_v1` (`gapfill_final_jobs_2026-10-05.json`, prompt from the in-game description, no canon entry exists for any of them, no facing words). 7 of them had a `done` manifest whose render bytes no longer exist anywhere (aridgrass, giantstikehr, scorchedstars, ...).
- Cannot be queued: 0.

## Refresh
`python3 src/RimMandrake/Utils/art/refresh_sheets.py` (state in `sheets_state.json`; `--dry-run`, `--force`; selftest `selftest_refresh_sheets.py`). URLs stay stable because serve_sheet re-reads sheet and decisions per request; run once, 27/27 rebuilt, URLs unchanged, 200.
