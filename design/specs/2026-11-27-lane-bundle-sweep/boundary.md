# BOUNDARY: the sweep of the ticket lane and the work bundles, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/lane_sweep.py` (`python3 lane_sweep.py [--regime NAME ...] [--plant NAME]`). Its
selftest: `src/RimMandrake/rimflow/selftest_lane_sweep.py`. Item: `RIMMANDRAKE_BUILD_LANE_BUNDLE_SWEEP_FIVE_STUCK_STATES_SEEN`.
The code that it sweeps: `src/RimMandrake/rimflow/list_dispatch.py` (`tick`: gather, decide, execute; `main clear`),
`src/RimMandrake/rimflow/work_bundle.py` (the bundle launch, overlay, `loc_plan`, `plan_restart`, `note_end`,
`note_restart`, `READ_MEMBERS`), `src/RimMandrake/rimflow/left_open_continue.py` (`at_finish`, `run`) and
`src/RimMandrake/rimflow/conductor_stops.py` (`rows`, the Conductor's stops view). Evidence:
`design/specs/2026-11-26-simulation-census/evidence.md` (rank 2) and the FlowWorks bundle WB-mod-FlowWorks-20261126-113858.

Offline simulation: yes. The sweep runs the real `list_dispatch.tick` every 10 minutes (the timer
`rm-list-dispatch.timer`, `OnUnitActiveSec=10min`) through one simulated day (144 ticks) on a fake clock, in a temp
folder that holds the lane state, the bundle store, the run records, the control db and the Conductor log. A run's end
calls the real `left_open_continue.at_finish`, and its continuation step calls the real `left_open_continue.run` a
minute later. After every tick it checks that no open ticket and no bundle stands in a state that no later step of the
real code, and no one told of it, can leave.

## What it is

Each regime is a world that the lane can meet: its tickets (filed, claimed, homes, blocks, causes) and, for each
ticket, the worker's ledger act at the end of its 1st, 2nd ... run (close, file a child and close, a `LEFT OPEN:` note,
a `REFUSED BY BUNDLE:` note, a dated wait, nothing). The written range (`REGIMES_SPEC`): `idle`; `block` (a block on a
ticket that closes); `chain` (each run files the next ticket of a chain, to the chain limit); `load_held` (an outside
load over the machine's line that only an act ends); `load_burst` (an outside load that falls by itself in 40
minutes); `bundle_left_open` (six members of one home, one closes per run, the sixth is rightly LEFT OPEN every run);
`home` (a ticket with a home and two children without one); `death` (the first run is killed); `refuse` (every run
refuses); `wait` (a 3 h dated wait, then a close). Left out, and why (`LEFT_OUT`): ssh hosts (a launch there is an
ssh call); onboarding of old tickets; `mod_work` rows (the maturation lane's); a block whose ender is a person; the
account gate held (`account_plan_sweep.py` sweeps it).

The Conductor stand-in acts on what it is told (a row of `conductor_stops.rows`, or a Conductor need line since the
state began): a `chain_stop` or `stopped` gets `list_dispatch.py clear` twice, then a 24 h wait; a `machine_load`
hold gets its outside load ended; any other hand state gets a 24 h wait.

The stand-ins replace only what touches the world:

| stand-in | replaces | model |
|---|---|---|
| the ledger store | `model.read`, `model.ITEMS` | a list of events in memory; the real `model.replay` folds it |
| the worker | the model inside a run | the regime's act for that ticket's nth run, written at the run's end (40 min) |
| helper launches | the lane's launch (`fx["launch"]`), `left_open_continue.run`'s `launch_fn` | a run record (`detached_helper.write_record`) and a scheduled end; `detached_helper.launch`, `left_open_continue.kick` and `work_bundle.launch_remote` raise |
| the members' states | `work_bundle.read_members` (a git fetch and a script in the clone) | the real `READ_MEMBERS` script, run in this process over the sim ledger |
| the outcome check | `list_effect.run` | fails while the ticket is open |
| the machine | `load_now`, `os.cpu_count`, `host_facts`, `_games`, `_mods`, `_off`, `_paused`, `_held`, `_pool`, `_clone_exists` | 14 cores; the regime's outside load; no hosts, games, mods, switches or pool |
| the account | `account_gate`, `left_open_continue.account_end_wait`, `GATES` | open |
| the clock | `time.time` | from 2026-11-27T00:00Z |

## ACCEPTS

- **a-regime.** A name in `REGIMES_SPEC` (`--regime`).
- **a-plant.** A name in `PLANTS` (`--plant`): a reversal of one fix, laid over the shipped code for one sweep.
- **the-lane-code-of-this-checkout.** It imports the four lane files from beside it.

## DOES NOT SURVIVE (not shown by the sweep)

- **a-real-run.** The stand-in run ends after 40 minutes with the regime's act. The sweep does not show that a real
  run does its work, leaves an honest `LEFT OPEN:` note, or ends at all.
- **the-real-conductor.** The stand-in acts at once on a row. The sweep shows that someone is told and that the act
  ends the state; it does not show that the Conductor wakes and reads its view.
- **ssh-hosts.** No host takes a ticket: SteveDesktop's room, its sort and its lease are not swept.
- **a-git-fetch.** The members' states are read from the sim ledger at once; a fetch that fails or lags is not swept.
- **a-second-day.** One day: the daily limits' 24 h windows reset is not swept.

## PROMISES (each one is owed a check of the same name in the selftest)

- **block-on-a-finished-ticket-found.** A block whose predecessor is closed still blocking (planted: `block_facts` as
  it read before its fix) is a `no_ender` in regime `block`; the shipped code shows none.
- **chain-limit-with-no-next-step-found.** A ticket at the chain limit that nobody is told of (planted: the stops view
  without its `chain_stop` row) is `untold` in regime `chain` after `REST_S` and a tick; the shipped code shows none.
- **load-line-hold-without-end-found.** A machine-load hold that nobody is told of (planted: the stops view without
  its `machine_load` notice) is `untold` in regime `load_held`; the shipped code shows none.
- **bundle-member-rightly-left-open-restarts-found.** A Conductor line that claims a daily limit it is over ("N of at
  most M today", N > M; planted: the continuation line as it read before its fix) is a `false_count` in regime
  `bundle_left_open`; the shipped code shows none, and the bundle restarts once per run that ends a member (5) and is
  raised by the restart that ends none.
- **one-ticket-bundles-found.** A home's ready tickets launched apart (planted: `system_of` without the item table, so
  a child with no home of its own stops joining its parent's home) is a `split` in regime `home`; the shipped code
  shows none.
- **shipped-code-sweeps-clean.** Over every regime, the shipped code shows no finding, every tick of every regime is
  read (at least 144 cases per regime), and the written range is swept.

## LIMITS

- `TICK_S = 600`: the timer's cadence (`rm-list-dispatch.timer`). A run state or a waiting state that fails its ender
  for one full tick is a `no_ender`.
- An untold hand state's limit is `conductor_stops.REST_S + TICK_S`: his words "Conductor sorts after 1 hour", plus the
  tick that reads it. On the shipped code the worst untold hold is 3000 s of 4200 (the load hold is listed at 3600 s).
- `RUN_S = 2400`, `STEP_S = 60`, `CORES = 14`, `HIGH_LOAD = 30`: a run of 40 minutes, the minute from a run's end to
  its continuation step, Archmagi's cores and a load over its line of 28 (`list_dispatch.json`).

## LIFE CYCLES

- **a sweep:** per regime a fresh temp folder; seed the tickets; 144 times: the due run ends and continuation steps,
  `list_dispatch.tick`, the checks, the Conductor stand-in; then the Conductor log's counts; the folder is deleted.
- **at `./publish`:** `pipeline_tests.json` runs the selftest when a lane file changes (about 9 s).
