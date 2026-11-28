# Polish beside design/specs/2026-11-27-steve-lane-sweep/boundary.md

## (fresh read, WB-pipeline-read-utils-20261128-092119, 2026-11-28)
- `src/RimMandrake/Utils/testq/steve_lane_sweep.py` the page's ACCEPTS lists `off` for steve1, but the code honours `off` only for steve2; no call site produces steve1 off.
- `src/RimMandrake/Utils/testq/steve_lane_sweep.py` `World.pick`: `self.ids += 0` does nothing.
- `src/RimMandrake/Utils/testq/selftest_steve_lane_sweep.py` 'jobs end' is checked only as a total over all regimes (`done > 0`), not per regime.
