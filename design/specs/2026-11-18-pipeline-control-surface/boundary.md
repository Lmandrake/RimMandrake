# BOUNDARY: the control store and `pipe`, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/control.py`. This page says where the control store stops. A claim about the store
counts only if it quotes an entry here (`standing_rulings.md` §A boundary page before pipeline code). Written
2026-11-18 11:50 PM PST. Read fresh 2026-11-19 by `RIMMANDRAKE_READ_CONTROL_PAGE_FRESH_BEFORE_CODE_IS_CUT`: 4 holes
added. Code cut to it 2026-11-19 by `RIMMANDRAKE_CUT_CONTROL_STORE_TO_PAGE_ARGV_READER_GOES`. "Tested by" names today's test in `selftest_control.py`; each promise also has a test of its own name there, and
`./publish` refuses a promise without one (`src/RimMandrake/Utils/boundary_check.py`).

## ACCEPTS (the only inputs the store is built for)

- **launch-through-one-door.** A launch is `launch_unit(args, spec)`. `args` are systemd-run's arguments: its
  options, `--`, then the payload; they are never read. The unit's name is the field `spec["unit"]`, and `spec` names
  one of the 9 launch families. Only `launch_unit` writes `systemd-run`: an `args` that starts with it, or has no `--`,
  is refused by name and never run.
- **one-name-one-run.** A unit name is one run. A launcher that uses one name for every run says `reuse_name` (the
  stop-resume sweep and the testq wake do). Any other name that has run is refused as DUPLICATE, so a left-open run
  is continued once.
- **a-launch-names-its-mods.** A launch is checked against the mods its spec names and no others. A hand-launched
  detached helper names none unless it passes `--env RM_CONTROL_MOD=<Mod>`: 98 of 98 detached runs in the store
  named none [measured 2026-11-19], 6 of them on FeverWood design tickets while he held FeverWood.
- **scope-names.** `all`, a mod in the pipeline, `stage:S`, `item:ID`, `family:F`, `role:R`. A wrong name is refused
  with the nearest names.
- **stop-target.** A scope, or one unit named `rm-...` with or without `.service`. A unit with another name (the
  testq wake) is named `unit:NAME`. Exactly one stop mode.
- **why-on-every-write.** Every command that changes something carries `--why`. A granted look and lifting his hold
  carry his words.
- **his-hold-as-a-file-row.** His hold is a row (mod, date, his words) in `mod_owner_hold.json`, brought in by
  `pipe init --import`. The import may be run any number of times.
- **plain-paths.** Paths of clones and of the store have no `$` in them (a launch with one is refused by name before
  it is admitted). A deadline is 1 whole second or more.
- **one-machine.** One user on one Linux machine, the store on its ext4 disk, units under that user's systemd.

Anything else is outside. Some outside inputs are refused by name today; refusing the rest is owed work.

## DOES NOT SURVIVE (not promised; where the store notices, it says so and stops)

- **two-failures-at-once.** A kill that fails while the cgroup also cannot be read. A failed escalation while a second
  kill finishes the same run.
- **cgroup-folder-that-cannot-be-listed.** Linux does not do this for our own user's units: 0 of 66 folders under
  `user.slice` failed to list, and every `cgroup.procs` under our `user@1000.service` was readable [measured 2026-11-19].
- **hand-command-in-a-run's-own-second.** A `pipe void` typed in the instant between a judge's start and its
  reservation. The held look is freed when that judge's process ends.
- **deliberate-bypass.** An agent that calls `systemd-run` by hand. The store is not a security wall.
- **launch-code-in-a-new-shape.** The census of launch sites finds a list whose first word is `systemd-run`; one
  built another way is not seen.
- **corrupt-or-lost-store.** It is not repaired. Nothing launches (a promise below) and `pipe doctor` names the fix.
- **a-store-locked-over-3-seconds.** The command says it could not look and exits 3. A unit kill does not wait.

## PROMISES (each one is owed a test of the same name)

- **off-blocks-starts.** After `pipe off` returns, nothing that had not begun can begin. Tested by `t_race`.
- **one-admission-point.** Every pipeline launch site goes through `launch_unit`, and a site that does not turns the
  selftest red. Tested by `t_sites`.
- **his-hold-refuses-launch.** A launch that names a mod he holds is refused, with his words, until he lifts it with his words.
  `pipe on all` never lifts it. A new hold after a lift holds again. Tested by `t_owner_import`, `t_scope`.
- **three-named-stops.** `pipe stop` is `--write-now`, `--at-easy-spot` or `--kill`. With none named it uses
  at-easy-spot and says so. A write-now order becomes a kill at its deadline. Tested by `t_stop`.
- **stop-reaches-the-agent.** A writing stop order is shown to the running agent after its next tool call, from the
  run's own clone. Tested by `t_stop`, `t_hooks_in_run_clone`.
- **kill-verified-dead.** `--kill` sends SIGKILL to the run's whole process group and its claude scope at once. It
  reports "killed" only after every process is seen gone. A survivor is reported and nothing is recorded killed. (His
  words, 11:28 AM.) Tested by `t_stop`, `t_stop_review_fixes`.
- **kill-works-without-the-store.** `pipe stop <unit> --kill` kills by unit name when the store is locked or
  unreadable. Tested by `t_review_claims_round_two`.
- **killed-run-needs-no-hand-step.** A killed detached run's record is closed and its clone returned by the command.
  Tested by `t_kill_bookkeeping`.
- **stopped-run-spends-no-trial.** A stopped or voided run charges nothing, in the store and in the dispatch books.
  Tested by `t_stop_review_fixes`, `t_void_books_by_run_id`.
- **look-charged-only-on-a-verdict.** A granted look is held before its judge runs and charged only on a valid
  verdict. Of two judges racing for the last look, one gets it. A judge that dies gives it back. Tested by `t_look`,
  `t_coverage_look`.
- **void-gives-back-once.** A voided run's charges come back exactly once. Tested by `t_look`.
- **void-never-moves-a-stage.** A void moves no stage. `pipe show` flags a stage that advanced on a voided run, and
  flags no other run. Tested by `t_void_stage`.
- **unreadable-store-launches-nothing.** With the store missing, corrupt or locked, nothing launches. `pipe show`
  says `CONTROL UNREADABLE` with the cause, or `STORE LOCKED` before the last saved state. Tested by `t_unreadable`.
- **probe-never-lies.** A failed `systemctl` call, an unreadable store or an unreadable `cgroup.procs` file is
  reported as "could not look". It never reads as "nothing there". Tested by `t_review_round_four_p1`.
- **same-command-twice.** A void, a settlement, an import or a keyed command sent twice has the effect of once.
  Tested by `t_look`, `t_scope`, `t_owner_import`.
- **every-change-is-an-act.** Each change is one record: who, when (Pacific), why, before, after. A write prints at
  most 3 lines. `pipe undo` reverses an act or refuses with the later acts in its way. Tested by `t_verbs`,
  `t_accounts`.
- **binds-at-once-from-any-clone.** An act binds when its command returns. It needs no git, publish or tick. Tested
  by `t_clones`.
- **verbs-answer-in-a-second.** A `pipe` verb usually answers in under 1 second on this machine. Tested by `t_verbs`.
- **queue-order-is-the-store's.** `pipe queue` sets the order the tick advances mods in. Tested by `t_queue`.
- **counts-and-limits-are-adjustments.** `pipe set`, `add`, `reset` and `limit` write a change at a moment; a run
  that finishes afterwards still counts. Tested by `t_accounts`.
- **a-test-never-touches-the-live-store.** Tested by `t_stop_review_fixes`.
- **ended-run-is-recorded-ended.** A unit that ends by itself is recorded ended: its start check and end receipt run
  the first `control.py` still on disk (the run's clone, the launcher's, then the seat clones'), so a clone returned
  before the receipt does not leave its run `started`. A run whose receipt still never ran (systemd reads its unit gone)
  is ended by `pipe doctor`, its stop orders done; a unit systemd cannot read is left started and named UNREADABLE.
  `ops_watch` reads `flow.ghost_runs` every run and alarms on any (`RIMMANDRAKE_END_GHOST_RUN_RECEIPT_NEVER_RAN_LUVL`). Added 2026-11-19 by
  `RIMMANDRAKE_END_GHOST_RUNS_STORE_SAYS_STARTED_SYSTEMD_GONE` (4 runs stayed started for good). Tested by
  `t_end_receipt_outlives_its_clone`.
- **reused-name-runs-again.** A `reuse_name` launch is admitted again once its earlier run is over, and refused while
  that run is live. Tested by `t_reused_name_runs_again`.

## LIFE CYCLES (a move not listed here is a defect)

- **run:** admitted → started → ended or killed. admitted → cancelled (an off came first), refused (at its start
  check), failed-to-launch, or abandoned (its launcher died). ended → killed only when a kill and the run's own end
  crossed. A name that never ran, or a `reuse_name` name whose run is over, may be admitted again under a new run id.
- **held look:** held → charged or released. charged → voided.
- **stop order:** pending → seen → done or escalated. escalated → back to pending or seen when the kill failed.
- **switch:** on ↔ off, one row per scope and layer (ours, his). His layer moves only with his words. A timed off
  (`maturation_dispatch.py pause --until`) turns on by itself at its time, with no new act.

Later lists beside this page: `polish.md` (outside claims, not fixed) and `next_version.md` (what 0.2.0 might add).
