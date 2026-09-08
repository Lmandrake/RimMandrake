# W9_RUN_STAGE_RESULTS_UNCHECKED_1 — w9_run.py logs stage bridge-call results but never checks them before continuing

Discovered 2026-09-07 (FOUNDRY, code-review sweep). Deliberately NOT fixed in the same
pass as the report-write fix (commit `9cf1c2ed`) — this is a behavioral change to a
bridge-driving tool BENCH was actively using mid-session, and could not be live-verified
while the bridge was held.

## spec
- `src/RimMandrake/Utils/w9_run.py`'s stages are strictly ordered and each invalidates
  assumptions the last one made (its own docstring, lines 13-30). Stage 3 (tiles-adjacent),
  stage 4, and stage 4b already correctly branch on `rr.get("success")` per call/chunk and
  stop or report per-item.
- **Stage 1 tiles** (~line 305-307), **stage 2 links** (~311-316), **stage 3b
  landmark-leftover removal** (~351-353, doesn't even print `success`, only
  `rr.get("removed")`), **stage 5 settlements** (~439-442), **stage 6 regions** (~450-453),
  and `world_commit` (~465) all call the bridge and log the result, but none branches on
  `r.get("success")` — the run always falls through to the next stage and eventually to
  lint/screenshot regardless of failure.
- A failed stage 1 (tiles never actually painted) would still let stages 2-6 run against
  inconsistent world state, with the only trace being one `success=False` sitting mid-report
  — easy to miss, and the doctrine ("each stage invalidates the last one's assumptions" per
  the docstring) is silently violated.

## verify
Each of stage 1/2/3b/5/6/commit checks `r.get("success")` (or the equivalent field) and
either aborts the remaining stages with a clear message, or at minimum marks every
subsequent report line as UNRELIABLE when a prior stage failed. Fix verified against a real
live run (this needs the bridge — schedule for whoever next drives it, not a dry inspection)
showing a deliberately-forced stage failure correctly halts/flags downstream stages.
