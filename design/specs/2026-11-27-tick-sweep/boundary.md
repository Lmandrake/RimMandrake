# BOUNDARY: the sweep of the Maturation Pipeline tick, Design Version 0.1.0

Code: `src/RimMandrake/Utils/tick_sweep.py` (commands `grid [--quick] [--base B] [--plant P]`,
`one <base>.<window>.<offset> [--plant P]`). Its selftest: `src/RimMandrake/Utils/selftest_tick_sweep.py` (`--red` runs
each check against a sweep that cannot see its fault). Item: `RIMMANDRAKE_BUILD_TICK_SWEEP_SLACK_KEPT_TICKETS_45_HOURS`
(rank 3 of `design/specs/2026-11-26-simulation-census/one_page.md`). The code that it sweeps:
`src/RimMandrake/rimflow/maturation_dispatch.py` (`tick`, `road_back_decide`, `game_deploy_launch`),
`src/RimMandrake/rimflow/maturation_autonomy.py` (`resolve`, `execute`, `_gate`, `_stale_walk`),
`src/RimMandrake/rimflow/maturation.py` (the deploy unit's books), `src/RimMandrake/Utils/testq/visit_feed.py`
(`waiting`) and `src/RimMandrake/rimflow/conductor_stops.py` (`rows`, the owed list).

Offline simulation: yes. The sweep runs the real tick (`MD.tick(root, cfg, True, fx=..., now=t)`, autonomy on) every
600 s step of a simulated day on a fake clock, in a temp folder, against a stand-in world. After every step it checks
that no mod, open mod ticket or visit check stands in a state that no later step of the real code can leave.

## What it is

Each step: the world ends the runs and deploys whose time is up, the real tick decides and acts, the real visit feed
reads the tick's `ingame_testq` block and sends checks to the stand-in lane, the real `conductor_stops.rows` reads the
lane, and then the checks. Each thing on each step is one of:

- **moving**: a run or deploy started or ended, a live run that the world ends, a check measured, a stage changed;
- **held by the world**: the account gate shut, or both games taken by another lane (an in-game mod only); the stall
  clock does not run in a hold the world ends by itself;
- **told**: a Needs Conductor line, a held or planned row, a pause that a bar put there (`SPENT_PAUSES`:
  stopped, steward_spent, fixer_spent, holder_spent, auto_spent, cycle_limit, fix_chain_ended, hand_run_seen;
  `SET_PAUSES`: held, no_cap, blind_off, ingame_off, steward_off, disabled, designer_chain_cap, ceiling, owner_hold,
  pipeline_paused, control_off), or a row on the Conductor's owed list;
- **done**: past its start stage.

A thing that is none of these for longer than its limit is STUCK. At the day's end a mod that kept moving but never
left its start stage and is not told is STUCK (kind `day`: a loop that nothing ends). A row whose `why` carries a
Python exception that the tick caught is STUCK (kind `error`): a swallowed fault is never read as a pass.

The stand-ins replace only what touches the world:

| stand-in | replaces | model |
|---|---|---|
| the mods' facts | `build_facts` (git, the ledger, the game folders) | each mod's stage, its exit's refusal lines (the stale walk build), its owed testq checks, its road-back hold, its open tickets |
| the helper launches | `launch`, `launch_brief` | a run that the world ends in 40 min (`RUN_S`; 3 h in `long_runs`); a steward on a stale walk build ends only if the regime gives up (`gives_up_s`), and then keeps the build STALE while game `a` is up |
| the deploy unit | `game_deploy` and its unit | 10 min (`DEPLOY_S`; the one measured ran 998 s); started while both games are taken, it ends `wait` (`M.WAIT_MARK`), the real unit's answer |
| the games | the bridge (`fx["bridge"]`) | free, or taken by another lane in `bridge_busy`; game `a` down in `game_down` |
| Steve's test lane | testq jobs, records | one job each 5 min (`LANE_JOB_S`); in `lane_refuses` every job ends `REFUSED` (LOAD) |
| the account meter | `fx["account"]` | open, or shut in `account_shut` |
| git | publish, land, clone sync | answers in the real contract (`publish_filed` -> `(ok, text)`), touches nothing |
| the ledger and control db | `model.read`, `RM_CONTROL_DB` | a scratch ledger and db under the temp folder |
| the owner's hold | `RM_OWNER_HOLD_FILE` | a hold on the first mod until `hold_until` in `owner_hold_4h`, then lifted |

Every subprocess and socket that the real code opens is refused and counted (`touched`).

The grid: six bases (`stale`, `visit`, `met`, `road`, `rest`, `mixed`: all four faulty states at once) times nine
windows (`calm`, `lane_refuses_1h`, `lane_refuses_6h`, `account_shut_2h`, `games_taken_3h`, `archbig_down_2h`,
`owner_hold_4h`, `steward_gives_up`, `long_runs`) times two clock phases (on a step, half a step after) = 108 regimes of
24 h. The quick grid (what `./publish` runs): every base under `calm` and `mixed` under every other window, 12 h each
(14 regimes; every window ends by +6 h and every limit is under 2 h).

The limits: a mod 3600 s (`STILL_LIMIT_S`, the Conductor's own sort of a resting mod); an open ticket of a resting mod
`conductor_stops.REST_S` + one step = 4200 s; a visit check: spent with no run of its own measured. Each report prints the
worst value of each measure, its limit and the cases read.

Measured on this build (2026-11-27, `grid`, 185 s): 108 regimes, 15552 ticks, 33858 cases, 0 STUCK, worst mod 0 s of
3600, worst ticket 1500 s of 4200 (`rest.calm.300`: REST_S less the 1800 s the mod had already rested, less a step's
grain), worst chain 0, touched 0. The zeros are not blind: each plant reads its fault (below).

## ACCEPTS

- **a-regime.** A name `<base>.<window>.<offset>`; `regime()` builds it. A regime may carry its own `fx` (a stand-in
  that breaks its contract, for the swallowed-exception check).
- **a-plant.** A name from `PLANTS`: a monkeypatch that puts a measured fault back into the shipped code for one sweep.
- **the-tick-code-of-this-checkout.** The sweep imports the rimflow and testq modules from beside it.

## DOES NOT SURVIVE (not shown by the sweep)

- **the-real-facts.** `build_facts` reads git, the ledger and the game folders; the sweep gives the facts. A fault in
  how the facts are read (a stage read wrong, a stale build not seen) is not shown.
- **a-real-run.** A stand-in run ends when its time is up. That a real helper ends, or tells the truth about being
  done, is `run_alive`'s and the reaper's (design/specs/2026-11-23-run-alive/boundary.md).
- **the-real-deploy.** The stand-in deploy ends in 10 min or `wait`s. That `maturation.game_repair` stops a game,
  deploys and restarts is not shown.
- **the-real-lane.** Steve's lane is one job each 5 min. The lane's own pauses, stops and ssh marks are
  `design/specs/2026-11-27-steve-lane-sweep/boundary.md`'s.
- **the-other-stages.** The bases start in `in_game`, `offline_build` and `passed`. The pre-human and walk stages, the
  Designer's chain and the work bundles (`list_dispatch.py`, `work_bundle.py`) are not swept.
- **the-account-plan.** The meter is open or shut. Its switching is `design/specs/2026-11-25-account-plan-sweep/boundary.md`'s.
- **the-tick-period.** The live tick runs each 60 s; the sweep steps 600 s. A fault that lives under 10 min is not
  seen, and a limit is read to a step's grain.

## PROMISES (each one is owed a check of the same name in the selftest)

- **world_calls_are_refused_and_counted.** A process and a socket opened under the sweep are each refused and counted.
- **mod_resting_after_pass_keeps_open_tickets_found.** With `conductor_stops` listing no `mod_rest` row (07441d68f4
  reversed), the sweep reports both open tickets of the resting mod STUCK (Gimme Some Slack, 2026-11-24, 45 h).
- **refused_load_counted_as_visit_failure_found.** With a REFUSED load read as the check's own failure (5d09ae880d
  reversed), the sweep reports each visit check STUCK, spent by lane refusals alone
  (`RIMMANDRAKE_ROUTE_VISIT_TESTQ_CHECKS_AHEAD_OF_FILLER`).
- **deploy_given_to_a_steward_that_may_not_stop_the_game_found.** With the stale walk build a steward's again
  (9f802d6866 reversed), the sweep reports the mod STUCK on a live steward that nothing ends
  (`RIMMANDRAKE_LET_TICK_DEPLOY_STALE_WALK_BUILD_STEWARD_MAY_NOT_STOP_GAME`).
- **road_back_hold_read_blocked_with_games_free_found.** With `road_back_decide` reading `blocked`, the sweep reports
  the road-back mod STUCK on `blocked` with both games free (design/specs/2026-11-25-tick-launches-road-back-hold).
- **relaunch_loop_that_never_leaves_found.** With the once-per-key steward gate removed and a steward that gives up,
  the mod moves every step and never leaves `in_game`: the day-end check reports it, and the step check does not.
- **swallowed_exception_found.** A stand-in that breaks its contract makes the tick catch a TypeError into a row; the
  sweep reports it as an error case.
- **sweep_is_deterministic.** The same regime twice gives the same events and cases.
- **shipped_tick_sweeps_clean.** The quick grid over the shipped code reads no STUCK case and touches nothing.
