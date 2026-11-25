# BOUNDARY: the Workshop Pipeline's one stage function and its stage view, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/list_pipeline.py` (all of it: `stage_of`, `six`, `facts`, `lane_verdict`, `last_act`, `MOVED_BY`),
the call in `src/RimMandrake/rimflow/list_dispatch.py` `tick` (each reading row carries its `stage`), and the stage view in
`src/RimMandrake/Utils/maturation_nonmod.py` (`section`, `blocks`; it reads the lane's `reading.json` in `read_stores`).
Tests: `src/RimMandrake/rimflow/selftest_list_pipeline.py` (each promise below has a test of its name) and the
section's own `src/RimMandrake/Utils/selftest_maturation_nonmod.py`. Acceptance:
`src/RimMandrake/rimflow/acceptance/step3b_stage_view_accept.py`.
Item: `RIMMANDRAKE_BUILD_ONE_OWNER_VIEW_NO_HOME_COUNT_BESIDE`, step 3 of
`design/specs/2026-11-22-coordination-every-agent-must-use/plan.md` (§The stages, §The six questions). Why: the plan
says one function decides an item's stage, and the tick and the page both call it, so the launcher and the page cannot
disagree.

## ACCEPTS

- **an-item-as-plain-facts.** `stage_of(item, now)` takes a dict: `state` (the ledger state), `effect` (the outcome
  check or None), `verdict` (`holds`, `fails`, `unmeasured`, or None when the check has not been run since the last
  run ended), `route` (None or `{who, ask, resumes}`; from the Shape stage's parts, plan step 4), `waits` (None or
  `{on, resumes, until}`), `run` (None, `live_shape`, `live_work` or `ended`), `stopped` (bool), `promise` (None,
  `kept` or `dead`), and optional `note` (the lane's words) and `age_h`.
- **the-ledger-item-the-runs-and-the-lane-row.** `facts(...)` builds that dict from one ledger item (model.Item or a
  dict), its detached-run records (oldest first), the Workshop Pipeline tick's row for it (`list_dispatch` `reading.json`,
  `items[id]`) with the reading's time, whether `owner_queue.is_his` holds for it, whether a note says it is ready to
  show, and the time of its last ledger event.

## DOES NOT SURVIVE

- **a-verdict-older-than-the-lane-reading.** The page takes the check's verdict from the tick's last row, not by running
  the check. A check that turned since that tick shows the old verdict until the next tick (every 10 min).
- **a-route-said-only-in-prose.** An item is routed only by the Shape stage's parts (`list_shape.first_route` over its
  `shape` event), by `owner_queue.is_his`, or by a note that says `READY TO SHOW`, `keeper save` or `pick image`. A
  route said only in a note is not seen.
- **a-run-on-an-item-with-no-check.** The page reads any live run on an item with no check as a live Shape run, also
  one the Conductor launched by hand.

## PROMISES

- **one-stage-per-item-from-one-rule.** `stage_of` returns exactly one of `STAGES` and a non-empty `why`, for any input
  of the accepted shape, and never raises on a missing key. The order: closed state; stopped; a live run; a route; a
  wait not yet due; no check; a check that holds; a check that is unmeasured; a due wait with a failing check (back to
  Shape: a date never launches old work); an ended run or a check not yet run (Verify); a failing check (Ready).
- **facts-that-disagree-are-a-conflict.** A `done` item whose check fails reads `conflict`, never `closed` or `ready`.
- **unmeasured-is-never-closed-or-ready.** A verdict that is not `holds` or `fails` reads `unmeasured` (or a stage the
  verdict does not decide: a live run, a route, a wait), never `closed` or `ready`.
- **a-wait-and-a-route-name-what-resumes.** A `waiting` or `review` row carries `resumes` from the wait or the route.
- **a-promise-rides-beside-the-stage.** A closed operational item keeps stage `closed`; its promise (`kept`, `dead`) is a
  separate field.
- **lane-row-to-verdict.** `lane_verdict(decision)`: `close`, `closed_by_check`, `close_refused`, `would_close` are
  `holds`; `blind` is `unmeasured`; a decision taken before the check ran (`disabled`, `pipeline_paused`, `off`, the
  adoption rows, `no_effect`, `not_found`) is None; every other decision of an item with a check is `fails`. A lane
  reading older than `LANE_STALE_S` or unreadable makes the verdict of every item with a check `unmeasured`, with the
  cause in `note`.
- **a-run-end-the-tick-has-not-read-is-verify.** In `facts`, an item whose newest run ended after the tick's reading
  has verdict None and run `ended`: it reads `verify`, not the stale verdict.
- **a-dead-run-nobody-acted-on-is-trouble.** In `facts`, an item with no check whose newest run was stopped, capped or
  refused (`maturation_nonmod.run_end`), and with no act after that run ended, has `stopped` true. `last_act` gives
  the time of an item's last act; a program's note about a run's end (`DETACHED run ...`, why `detached run ended`)
  is not an act.
- **six-answers-from-the-stages.** `six(items, now)` returns `doing` (a live run), `next` (`ready`, in the given order),
  `closed`, `open_why` (every item not closed, grouped by one reason per stage, a wait grouped by what it waits on, each
  group with its count, its oldest item and that item's age), `escalated` (`trouble` and `conflict`) and `review`.
  Each item is in exactly one `open_why` group or in `closed`.
- **a-question-for-the-conductor-is-not-trouble.** A part routed to the Conductor reads `waiting` ("routed to the
  Conductor") and is in `six`'s `asked`, never in `escalated`. A stopped run on the same item still reads `trouble`. Why:
  on 2026-11-23 such a question stood under "stuck, needs a hand", and the owner read it as a broken run.
- **a-block-on-an-item-names-it-with-or-without-a-kind.** In `facts`, a block with a `blocked_on` and no kind is a wait on
  that item (`priority.block_kind`); a block on an item that is not open is no wait.
- **the-tick-and-the-page-call-it.** `list_dispatch.tick` writes each row's `stage` into `reading.json`, from
  `list_dispatch.row_stage`: `stage_of` over the tick's own facts (its fresh verdict, waits and decision).
  `maturation_now` hands `stage_of` to `maturation_nonmod.section`, which places every open non-mod item by
  `stage_of(facts(...))`.
- **each-stage-says-program-or-by-hand.** `MOVED_BY` names, for each stage, who moves an item on: `program` or
  `by hand`, with how. The page prints it on each stage row. Shape reads `program` (the lane launches a Shape run on an
  item due for Shape, plan step 4); an older item enters only when someone names it, and the row says so.
- **each-limit-names-its-danger.** `LANE_STALE_S` is written beside its danger.

## LIFE CYCLES

- **a tick:** `list_dispatch.decide` → `row_stage` (the tick's facts) → `stage_of` → the row's `stage` in
  `reading.json`.
- **a page build:** `maturation_nonmod.read_stores` reads the lane's `reading.json` → `section` builds `facts` per
  open non-mod item → `stage_of` → `six` → the stage rows and the six blocks.

Later lists beside this page: `polish.md` (none yet).
