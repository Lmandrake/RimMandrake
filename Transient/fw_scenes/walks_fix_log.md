# walks_fix_log -- water/river/objects walks for level water (FOUNDRY offline helper, 2026-10-17)

Scratch clone /home/mandrake/rm/scratch/FOUNDRY/walks (base 6955ddf0a). No bridge, no game.

## Job 1 -- water_scenes_walk.py reads decilitres, settled test, level rows
- status: DONE
- Squares are read through `ProofReadout` (litres to the litre -> dL), ponds through stock*10,000; `cells()` returns
  (depth, fill, dL). Tolerance `TOL_DL` = 10 dL per square read. No bridge method returns raw dL for a square, so the
  readout's litre rounding (+-5 dL) is the floor of the instrument.
- Expected rows rewritten from `level_solution` (S5 A 4,737 dL a canal square / B 909 / E 2,222 / F 20,000 each / G six squares
  at 0.333 m after the bugs-fix pump; C total conserved, D exactly 10,000 dL). The sealed doc wording stays printed as "doc",
  the level-water number beside it as "level". Scenes json untouched.
- New `.lvl` rows: ProofLevelSurface per body, bar 1 cm (S2.lvl.end, S3.lvl, S5.lvl.A/F/E/G, S6.lvl.run1/run2).
- S2.d: settled = 8 unchanged pulses in a row AND pond+trench full (`settled_at`); the live p7-p10 plateau is a selftest case.
## Job 2 -- river index + objects index accumulate
- status: DONE. `fw_walk_common.write_index(accumulate=True)` keeps `<index>.groups.json`, merges by group id (newest replaces
  in place); `--reset-index` on both walks. objects_sheet `rows.json` still holds only the latest run's rows.
## Job 3 -- annotate_water_scenes.py
- status: DONE. Prints level expectation, ProofReadout strings and per-body surface gap from the rows; S5 un-stubbed with the
  redrawn wording and S5AB/C/E/G images; step keys `AB/C/E/G`; `main(live)` callable.
## Job 4 -- selftests
- status: DONE. `northstar/selftest_water_walks.py` 49 checks (readout parse, level_solution vs P3 numbers, settled_at, mock
  walk all scenes + crash path, level row red/unmeasured, annotate, three index accumulations); selftest_fw_walks and
  selftest_level_water still PASS under run_selftests.py.
## Publish
- status: pending
## Not done / claimable
- Live rerun of the walk on the e40b3d972 DLL (S2, S3, S5, S6) to see which new rows MATCH: needs the bridge.
- S3.e round trip still unstaged.
