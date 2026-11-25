# BOUNDARY: the Workshop Pipeline's Waiting, Ready and Work stages (list_dispatch.py), Design Version 0.1.0


The program names keep the old word "list" (`list_dispatch`, `list_pipeline`, `list_home`, `list_effect`, the key `list_dispatch`); the pipeline's name is the Workshop Pipeline.
Code: `src/RimMandrake/rimflow/list_dispatch.py` (all of it), `src/RimMandrake/rimflow/list_dispatch.json`,
`src/RimMandrake/rimflow/mod_work.py` (all of it) and its callers `list_pipeline.facts`/`stage_of`, `list_home.offer`
and `maturation_nonmod.section`,
`maturation_dispatch.occupancy` (the lane's runs only),
`src/RimMandrake/Utils/systemd/rm-list-dispatch.{service,timer}`, the `list_dispatch` family in
`src/RimMandrake/rimflow/control.py`, `detached_helper.py launch --next-act-owner` and the one line in
`left_open_continue.plan` that reads it.
Item: `RIMMANDRAKE_BUILD_LIST_LANE_ON_RED_DISPATCH_GOALS_FIRST`, step 2 of
`design/specs/2026-11-22-coordination-every-agent-must-use/plan.md`. Why: on 2026-11-23 about 918 open list items
waited for the Conductor's hand, because no program launched them. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_list_dispatch.py`. The plan's acceptance script
(`src/RimMandrake/rimflow/acceptance/step2_list_lane_accept.py`) checks `decide` over fake facts.

## ACCEPTS (the only inputs this is built for)

- **an-open-list-item-with-an-outcome-check.** A ledger item that is not done, dropped or superseded and that carries an
  outcome check (`Item.effect`, step 1). The check is run by `list_effect.run` in the clone that the tick runs from.
- **an-open-list-item-whose-verify-names-an-acceptance-script.** An item with no check whose `## verify` or
  `## criteria` section names `python3 <repo path>_accept.py`, and that file exists. The tick attaches
  `cmd:python3 <path>` as its check through `rimflow effect` (the step-1 gate: it must be seen failing). It launches
  nothing on that tick.
- **the-detached-run-records.** `detached_helper.all_records()` and `live_status`: a unit is live while it is
  `launching` or `running`. The lane asks `all_records` to report unreadable records during that same scan.
- **the-gates.** The pipeline's pause (`pipeline_pause.blocks`), the control store (`control.blocked` with family
  `list_dispatch`, the item and the item's mod), the owner's mod holds (`mod_owner_hold`), the switching plan's drain (`detached_helper.drain_refusal`),
  the Dispatcher's account pick (`maturation_dispatch.account_gate`), the clone pool's admission (`scratch_clone.pool_admit`).

## DOES NOT SURVIVE (not promised)

- **an-item-whose-mod-is-not-named-in-its-id-or-title.** The mod of a list item is read from its id and title words.
  An item about a held mod that names no mod is launched. `detached_helper.launch` refuses it only if its brief sets
  `RM_CONTROL_MOD`.
- **a-mod-ticket-that-names-no-home-and-no-mod-path.** `mod_work.of` reads the ticket's home, then the repo paths in its
  title, check and prose. A ticket about one mod that has no home and names the mod only by a word stays in the List
  Pipeline. A ticket with an explicit non-mod home (`pipeline:`, `game:`, `machine:`) stays, whatever its paths say.
- **a-check-that-passes-for-the-wrong-reason.** Step 1's page says it. The lane trusts the check.
- **two-ticks-at-once.** The tick holds a file lock; a second tick on another clone with another state directory is not
  seen.

## PROMISES (each one is owed a test of the same name)

- **decide-is-pure-and-says-why-on-every-row.** `decide(cfg, st, facts, now, account)` reads only its inputs, writes
  only `st`, and returns one row per item with a non-empty `why`. A ledger that could not be read (`facts["items"]` is
  None) is one `blind` row and no launch.
- **a-mod-ticket-is-not-the-list-pipelines.** A ticket whose home is `mod:<folder>`, or that has no home (or `unplaced`)
  and whose every repo path (title, check, prose) lies inside one mod's folder (`src/<Tier>/<Mod>/` or
  `design/concepts/<Mod>/`), is one mod's work (`mod_work.of`, the one rule). The tick runs no check on it, adopts,
  closes and launches nothing (decision `mod_work`); `list_home.py offer`, the feed of a Codex lane, does not offer it
  and counts it under its mod; its status line on the page (`stage_of`, stage `waiting`) says that it waits for the
  Maturation Pipeline run of that mod, and names the mod. A pipeline ticket that names a mod only as its example (a
  path outside the mod, or paths in two mods) stays in the Workshop Pipeline. A home that cannot be read, or prose that
  cannot be read, launches nothing and is not offered: the row reads `blind` and the stage `unmeasured`, "could not
  look". A live run on such a ticket still shows as Work. Measured 2026-11-24: the Codex lane built two HugeThings tickets
  (home mod:HugeThings), because HugeThings has no version folder and the page counted them as list work.
- **the-check-runs-before-every-attempt.** An item whose check holds reads `close`, whatever its runs; the tick closes it
  as the pipeline's act (`list_effect.close_item`, role unit `rm-list-dispatch.service`) if its live gate allows it,
  and launches nothing on it. Both ticks share the live gate on the outcome-check boundary page. An
  unmeasured check reads `blind`. An item with no check reads `no_effect`, unless it is routed (`routed`) or due for
  Shape (`shape`); those two are promised on the Shape page, `design/specs/2026-11-23-list-shape/boundary.md`.
- **one-work-run-then-one-more-only-on-a-named-next-act.** An item gets a first Work run. After a run ended with the check
  failing, it gets one more run only when that run left a `LEFT OPEN:` note (its next act) and did not put a wait on the
  item. `max_runs_per_item` (2) runs is the most. Every other end reads `stopped`. A re-shape by another party starts the
  count again (the Shape page).
- **a-launch-that-never-started-is-not-spent.** A launch that returned no unit is recorded with `failed` set and is not
  counted as a run. After `max_never_started` such launches in a row the item reads `system_wait`, is said once, and the
  next launch waits `SYSTEM_WAIT_S`, so a launch that cannot start is not sent again on every tick. A launch refused for
  its form reads `stopped` with its repair. A run that died of a cause outside the work is not counted either
  (`design/specs/2026-11-23-one-failure-classifier/boundary.md`).
- **a-stop-names-the-outcome-the-reason-and-the-smallest-act.** A `stopped` row carries `need` with `outcome` (the
  check that still fails), `why_not_recovered` and `smallest_act`, all non-empty. The tick writes it once as a Needs
  Conductor line, and not again until the item changes.
- **waits-are-not-launched.** An item that waits on an open item reads `waits_on` and names that item. An item with a
  dated wait in the future reads `waiting`. An old item that nobody named, whose dated wait has passed and whose check
  still fails, reads `reshape` and launches nothing (plan: a date never launches old work). An item with no check that is
  due for Shape goes on to `shape`. A blocked item reads `blocked`.
- **a-passed-wait-gets-one-second-look.** A lane item with a check (named for the lane, or filed at or after `shape_from`)
  whose dated wait passed and whose check still fails gets one Work run (opus) after that date, whose brief names what the
  wait was for and asks first if the work is still worth the touch. It counts as a Work run: after `max_runs_per_item` the
  item reads `stopped`, with its Needs Conductor line. A lane run launched since the date was that look. Measured
  2026-11-24: such an item read `reshape` for good and no program ever launched it.
- **a-block-whose-predecessor-is-done-is-not-a-block.** `block_facts` asks `priority.block_holds`, the one rule of every
  offer path. When each ticket that the block names has reached its level, the item reads neither `waits_on` nor
  `blocked` and the lane works it. A superseded predecessor is followed to its successor. A block of another kind, or on
  a predecessor dropped with nothing released, still reads `blocked`. Measured 2026-11-23: 40 open items were blocked on
  a done ticket, and the plain-English batch chain had stood still for 16 hours behind such blocks.
- **the-gates-launch-nothing.** The lane launches nothing when it is disabled, under the pause, under `pipe off` (all,
  `family:list_dispatch`, the item or its mod), on an item whose mod is held by the owner, under an account hold (the plan's drain or the Dispatcher's pick), when
  the control store cannot be read, or when the clone pool refuses a new clone. Each reads its own decision. Disabled, the pause and `pipe off` (or a
  control store that cannot be read) also stop its closes and its adoptions, and the tick runs no check under the pause.
- **the-lane-has-its-own-slots-and-chain-rule.** The lane keeps `max_live` slots for lane items at any load. Past them it
  launches only while the larger of the 1 and 5 minute load averages, plus `load_per_run` for each launch of the same
  tick and each recent lane launch, is under `load_line`; a load that cannot be read is no spare room. Mod and nightly-test runs do not count. An item whose chain of causes (its `caused_by` ancestors) already holds `max_chain_depth` lane runs reads
  `chain_stop`. Live runs on items that carry no check do not fill the lane's slots, except Shape runs on items due for
  Shape, which do.
- **the-tick-counts-recent-lane-launches-before-taking-spare-room.** For the load gate, the tick counts live detached
  records marked `next_act_owner=list_dispatch` whose launch time is within `load_lag_s` before the tick, including
  records outside the tick's item selection. An unreadable record or launch time means no spare room.
- **a-lane-run-on-a-mod-takes-no-mod-slot.** The mod tick (`maturation_dispatch.occupancy`) does not count a live run that
  this lane launched (`next_act_owner` list_dispatch) in its own `max_live`. The run is still live on its mod, so no mod
  run starts beside it on the same files. Measured 2026-11-24: lane runs on FlowWorks held the Gimme Some Slack walk brief
  at slots_full.
- **a-claimed-item-is-not-the-lanes.** An item that is `doing` under a live lease, with no lane run on it, reads
  `claimed`: it is not launched and not adopted. The lease of the lane's own run does not stop its second run.
- **a-raised-item-goes-first.** Items that `rimflow raise` raised come before every other item, in the order they were
  raised (`model.raise_key`, the rule of every offer path).
- **oldest-blocking-item-first.** Items not raised are taken in this order: an item that another open item waits on first, then the
  oldest filing first.
- **the-run-owns-no-continuation.** A lane launch passes `--next-act-owner list_dispatch`; `left_open_continue.plan` does
  not continue such a run, so its `LEFT OPEN:` note is read by the lane alone and the two-run rule holds.
- **a-heavy-acceptance-script-is-not-adopted.** Before it adopts an acceptance script, the tick runs it once, bounded by
  `max_adopt_check_s`, and keeps the reading per item state. A script that does not end inside the bound reads
  `adopt_too_heavy` (or `shape`, when the item is due for Shape) and is not attached, because an attached check runs on
  every beat of two timers.
- **a-write-that-stands-unlanded-is-not-a-refusal.** A `rimflow close` or `rimflow effect` that exits 4 (written, not
  landed: another writer moved origin during the publish) stands. The row reads `closed_by_check` or `adopted` and says
  it is not landed yet; it is never recorded as a refusal. Measured 2026-11-23: two of the first ticks' writes exited
  4 and landed on origin minutes later.
- **the-tick-files-nothing.** A tick writes no `file` or `spawn` event. It writes `close` for a check that holds,
  `effect` for an adopted acceptance script, or the one shared note when a required live line is missing or fails.
- **a-dry-tick-writes-nothing.** A tick without `--apply` launches nothing, closes nothing, attaches nothing and writes no
  state.
- **only-narrows-the-items-never-the-gates.** `tick --only ID...` (the Conductor's run-now) decides only the named
  items, in the order given, through every gate and the same slots; a named item that is not open with a check or an
  acceptance script reads `not_found`.
- **each-limit-names-its-danger.** Each numeric setting in `list_dispatch.json` has a `_<name>_doc` that names the danger
  it guards.

Later lists beside this page: `polish.md` (none yet).
