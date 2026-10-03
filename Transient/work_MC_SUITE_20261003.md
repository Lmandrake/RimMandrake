# MC_SUITE work log 2026-10-03

Goal: module-level `suite = Suite("MessyConduit")` in src/RimMandrake/MessyConduit/validation.py.

- started: reading sources
- read: validation.py (offline O1-O5, run_live battery, M4/M9 modes), suite.py, runner.py, Graffiti/FlowWorks suites, walk, matrix README/run_live, jobs.suite_mods
- plan: suite chains `offline_O1_O5` (in-process on posix; under python.exe via `wsl.exe python3 validation.py --rows-json -` since numpy/PIL live in WSL) and `live_battery` (Bridge refactored into _BridgeBase; SuiteBridge routes calls via t.session and ticks via t.wait_ticks so watch/clockgate see every tick; scene origin moved to the runner's anchor, clamped to map). Each standalone row -> one component (FAIL raises; UNMEASURED/UNBUILT/UNCOVERED -> UNMEASURED; rows are independent measurements so a failed row does not blank later rows). Teardown destroys SITE.
- separate lanes (documented): matrix (absolute 226x100 REGION + map-wide clears, needs precomputed spec JSON, ~26 min), M4 --save-load (loads a save: replaces the runner's map), M9 --removal-check (needs a cold load on a tier without the mod).
- implemented suite + SuiteBridge + _set_origin + --rows-json; FakeWorld dry run: 2 chains, row->component mapping, toggles, origin clamp, findings OK
- verified: offline standalone 6/6 PASS; --rows-json emits one ROWS_JSON line; northstar_matrix selftest 50/50; run_selftests 121/121; jobs.suite_mods() keeps MessyConduit (14 mods); modcheck status lists MessyConduit REFUSED at a STALE hash (validation.py is inside the hashed mod dir, so this edit staled the matrix record -- expected; a fresh record needs a live run).
- not done (by brief): no live run, no bridge, no commit. The live chain has only been exercised against rimdrive FakeWorld with stubbed tiers.
