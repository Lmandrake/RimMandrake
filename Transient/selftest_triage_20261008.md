# Selftest triage 2026-10-08 (each rerun alone, foreground)

| # | test | result | class |
|---|------|--------|-------|
| 1 | Utils/selftest_solarmirrors_fuzz.py | OK, 14300 cases 0 failures | flake (load/memory) |
| 2 | rimflow/selftest_items_glob_live.py | 3/3 | flake (likely ran while ledger/items mid-change) |
| 3 | Utils/artpipe/selftest_artpipe_state.py | 0 failures | flake |
| 4 | MandrakePatches/selftest_mandrakepatches.py | all passed | OOM victim (rc 137) |
| 5 | Utils/modcheck/selftest.py | 22/22 (run from Utils dir) | OOM victim |
| 6 | src/RimStarWars/StarWarsPatches/selftest_starwarspatches_semantics.py | all passed | OOM victim (task paths lacked RimStarWars/ prefix) |
| 7 | src/RimUtinni/UtinniPatches/selftest_utinnipatches_dump.py | all passed | OOM victim (path lacks RimUtinni/ prefix) |

No L0 regression found; no source changes. Re-run of the full suite should be sequential or capped to avoid rc 137.
