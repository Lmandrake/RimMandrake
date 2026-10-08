# Placeholder guard (owner rule 2026-10-07 22:33 PDT)

> "make sure that at no time can geometric placeholder art ever remain a viable Variant or selection, ok?"

## Status
- [x] 1 detector + calibrated selftest
- [x] 2a review-sheet builder
- [x] 2b art install / ingest
- [x] 2c repo lint in run_selftests.py + allowlist
- [x] 2d artpipe validator
- [x] 3i Webwork Brennoth/Ruddreth/Sorrivel jobs
- [x] 3ii Webwork sheet rebuilt + served
- [x] 4 placeholders, all kinds, across served sheets

## Done so far
- detector: `placeholder_detect.placeholder_reason()` (few colours + one dominant colour + circle/ellipse/rect silhouette). Calibration: 21/21 known circles, 0/11 low-colour real sprites, 0/150 artpipe renders. Repo-wide: 70 hits, all visibly flat shapes (3 UI buttons + 1 Blank.png outside art scope).
- 2a `art_sheet.py`: placeholder set greyed "placeholder — not selectable", no pick, no variant, stripped from saved variants; row whose current art is a placeholder prefills `redo` + flag NEEDS ART. (ef5aed1bf → 7d8586163)
- 2b `artledger.install` refuses placeholder bytes under any authorisation; `ingest` turns a placeholder pick into a `redo` ruling (raw_verdict placeholder-pick, `why` recorded), refuses placeholder variants/graphic picks.
- 2c `placeholder_lint.py` + `selftest_placeholder_lint.py` (REQUIRED in run_selftests.py) + `placeholder_allowlist.json` frozen 2026-10-07: 66 entries, 35 with jobs, 31 OWED.
- 2d `artpiped.py`: a finished render that is a placeholder fails `placeholder_output` (daemon pid 441 picks it up only on restart).
- 3i 9 jobs queued priority 0: webwork_{brennoth,ruddreth,sorrivel}_real_v1{a,b,c}.  (c8907f223)
- 3ii Webwork sheet rebuilt (gate PASS, html-only; decisions untouched) — live on the existing setsid server: http://localhost:34871/?t=akw0P54hCTqopbWYe66c6A (curl 200). Dulloth C = dulloth_redo_v2, Kollavane C/D/E = kollavane_redo_v2a/b/c beside the old art; 21 placeholder sets greyed; Brennoth/Ruddreth/Sorrivel/Dulloth/Kollavane flagged NEEDS ART. SHEETS_INDEX still lists the stale port 42715.
- 4 sweep of all served sheets: `placeholder_sheet_sweep.py` → `.json`; results in placeholder_plants.md "Placeholders, all kinds". FeverWood, Grey Sea, Miasma, The Chill, The Scald, Twilight Sea sheets rebuilt html-only so their placeholder sets are greyed too (all 6 gate PASS).
