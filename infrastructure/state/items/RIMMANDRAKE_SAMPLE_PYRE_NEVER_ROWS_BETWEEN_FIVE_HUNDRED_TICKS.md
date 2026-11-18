# RIMMANDRAKE_SAMPLE_PYRE_NEVER_ROWS_BETWEEN_FIVE_HUNDRED_TICKS

## spec
Codex review, 2026-11-18 (finding 5, `D:\ClaudeWork\rimmandrake\evidence\scene_snapshot\codex_round1.txt`), on
`src/RimMandrake/Pyrelands/wind_burn_live.py`: the rows "F,R never more fires than 3 x the cells lit" and "F,R nothing
burns beside the lit lanes" are read from samples every 500 ticks (`run()`: 20 x `adv(500)`). A fire population over the cap,
or an outer-lane fire, that comes and goes between two samples passes. Either sample densely enough for the claim (a
cheaper per-tick peak read in the companion, e.g. a MapComponent_BurnLine probe that keeps the peak and the outer-lane
max since the line was lit) or reword the row to what it measures ("at every 500-tick sample"). Which one is a Pyrelands
test-design call for the builder or Designer of that mod; a row's wording that changes what the bar promises stays the
owner's.

## criteria
- The two rows either read a continuous peak (probe-backed) or name the sampling they rest on.
- Acceptance test: none, test-design choice between a new companion probe and a row rewording; the chosen route writes its
  own offline check (selftest_pyrelands_wind_burn_rows.py drives these rows).

## verify
- `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_pyrelands_wind_burn_rows` GREEN after the change.

## refs
file: src/RimMandrake/Pyrelands/wind_burn_live.py
file: src/RimMandrake/Pyrelands/selftest_pyrelands_wind_burn_rows.py
