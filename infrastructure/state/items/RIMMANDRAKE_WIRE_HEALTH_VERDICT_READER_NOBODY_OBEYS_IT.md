# RIMMANDRAKE_WIRE_HEALTH_VERDICT_READER_NOBODY_OBEYS_IT

## spec

Operations still writes ONE health verdict every ops_watch pass (`src/RimMandrake/Utils/ops_health.py` ->
`$RM_OPS_WATCH_DIR/health.json`: state, spent SLIs and their scope, the ordered `system_items`, `content_paused`).
The owner's ruling (2026-11-03, `design/RimMandrake/standing_rulings.md` §Relentless fixes the system first) is that
the build pipeline asks Operations for health and takes system items first, and pauses only what a spent SLI touches.
Its one reader was the retired Relentless tick. Measured 2026-11-19 (BENCH, item
`RIMMANDRAKE_FINISH_RETIRED_ERA_REMAINS_TWENTY_ONE_NO_TICKETS`): no file of the Maturation Pipeline's launchers
(`maturation.py`, `maturation_dispatch.py`, `maturation_autonomy.py`, `dispatcher.py`, `detached_helper.py`) names
`ops_health` or `health.json`; the only importers are ops_watch, alarm_census and model. So the verdict is computed
and obeyed by nobody, and a spent budget pauses no content.

Do: make the pipeline's launch decision read `health.json` (system items first pick, never preemption; pause new
content only in a spent SLI's scope; an UNMEASURED or stale verdict treats every open system item as first and says
so), or, if the Conductor rules the Maturation Pipeline's own "fixes its own defects" rule replaces it, drop this item
and say so in standing_rulings. `maturation_dispatch.py` is a pipeline file under its boundary page: a boundary
promise and its test come first.

## verify

Acceptance test (watched failing on base `9761a57a92`+this run's edits, rc=1, 2026-11-19 BENCH):

    git grep -l -E 'ops_health|health\.json' -- src/RimMandrake/rimflow/maturation_dispatch.py \
      src/RimMandrake/rimflow/maturation_autonomy.py src/RimMandrake/rimflow/dispatcher.py \
      src/RimMandrake/rimflow/detached_helper.py src/RimMandrake/rimflow/maturation.py

passes (rc=0, at least 1 file listed) once a launcher reads the verdict; plus the launcher's own boundary test of the
promise, run red first.

## criteria

- A1: a pipeline launcher reads Operations' `health.json` before choosing what to launch (the grep above lists a file).
- A2: with a degraded verdict whose spent SLI scope is `game`, a content item that needs the live game is not launched
  and a system item is; shown by a selftest.

## refs

file: src/RimMandrake/rimflow/maturation_dispatch.py
file: src/RimMandrake/Utils/ops_health.py
