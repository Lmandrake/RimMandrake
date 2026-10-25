# FAUNA_DRIVE_FIX_TEST_RUNS_COUNTED

Three lesser defects in src/RimMandrake/Utils/art_eval/fauna_drive.py found by full-file review (FOUNDRY 2026-10-24):

1. `rows`, `candidates` and `latest()` (used by `install`) read `round_series.decisions()`, which includes `--test`
   runs; runner.py counts rounds with `production_decisions()` (skips run.json test:true). A test run named
   `fauna_*` would bump the round tag in `rows` and could supply the "ACCEPT" that `install` reads. No fauna_* run is
   a test run today (60/60 test:false), so nothing is wrong yet.
2. `latest()` tells candidate runs from first-pass runs by `"_r" in run name after "fauna_"`; a biome whose name
   contains `_r` (e.g. `glass_reef_00`) would be read as a candidate run. Use a pattern like `(^|_)(s\d+_)?r\d+_`.
3. `rows`: `specs[t]` raises KeyError inside the thread pool for a def with no spec, so the whole batch writes no
   rows file. Hold that row (print it) instead.

Failing-test sketch: decisions() fixture with a test run fauna_t_r1_00 ACCEPT newer than the production REGEN;
latest(D, True) must ignore it.
