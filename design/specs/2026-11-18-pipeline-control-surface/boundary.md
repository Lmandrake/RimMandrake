# BOUNDARY: the control store and `pipe`, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/control.py`, and the two doors that ask `src/RimMandrake/rimflow/test_process.py`
(`launch_unit` here, `append` in `src/RimMandrake/rimflow/model.py`). This page says where the control store stops. A claim about the store
counts only if it quotes an entry here (`standing_rulings.md` §A boundary page before pipeline code). Written
2026-11-18 11:50 PM PST. Read fresh 2026-11-19 by `RIMMANDRAKE_READ_CONTROL_PAGE_FRESH_BEFORE_CODE_IS_CUT`: 4 holes
added. Code cut to it 2026-11-19 by `RIMMANDRAKE_CUT_CONTROL_STORE_TO_PAGE_ARGV_READER_GOES`. "Tested by" names today's test in `selftest_control.py`; each promise also has a test of its own name there, and
`./publish` refuses a promise without one (`src/RimMandrake/Utils/boundary_check.py`).

## ACCEPTS (the only inputs the store is built for)

The ledger's `append` writes whole criterion text inline when an `implemented` event fits. An oversize event can keep
long criteria in the fulltext store with bounded previews on the ledger (`selftest_model.py`, `selftest_prooflint_at_filing.py`).

- **launch-through-one-door.** A launch is `launch_unit(args, spec)`. `args` are systemd-run's arguments: its
  options, `--`, then the payload; they are never read. The unit's name is the field `spec["unit"]`, and `spec` names
  one of the 9 launch families. Only `launch_unit` writes `systemd-run`: an `args` that starts with it, or has no `--`,
  is refused by name and never run.
- **one-name-one-run.** A unit name is one run. A launcher that uses one name for every run says `reuse_name` (the
  stop-resume sweep and the testq wake do). Any other name that has run is refused as DUPLICATE, so a left-open run
  is continued once. Each launch is its own call: two threads launching one name in the same instant are outside.
- **a-launch-names-its-mods.** A launch is checked against the mods its spec names and no others. A hand-launched
  detached helper names none unless it passes `--env RM_CONTROL_MOD=<Mod>`: 98 of 98 detached runs in the store
  named none [measured 2026-11-19], 6 of them on FeverWood design tickets while he held FeverWood.
- **scope-names.** `all`, a mod in the pipeline, `stage:S`, `item:ID`, `family:F`, `role:R`. A wrong name is refused
  with the nearest names. `pipe queue` and `pipe grant` take a mod and refuse any other scope (slice review 4, 20).
  `pipe off` and `pipe on` also take a mod not yet in the pipeline whose shipping folder exists
  (`src/RimMandrake|RimStarWars|RimUtinni/<Mod>/About/About.xml`), so an admitted mod is switched off before it is
  seeded (WreckedMachines, 2026-11-19, read "no mod in the pipeline"; item
  `RIMMANDRAKE_HOLD_NEW_CONCEPT_DISABLED_DESIGNER_CHAINS`).
- **stop-target.** A scope, or one unit named `rm-...` with or without `.service`. A unit with another name (the
  testq wake) is named `unit:NAME`. Exactly one stop mode.
- **why-on-every-write.** Every command that changes something carries `--why`. A granted look carries his words;
  lifting his hold carries his words or the Conductor's lift (below).
- **his-hold-as-a-file-row.** His hold is a row (mod, date, his words) in the store, written by `mod_owner_hold.py
  hold|lift|allow-design` with his words (a lift may instead be the Conductor's, below). `mod_owner_hold.json` is its mirror: the store rewrites it after each of
  those writes (`mod_owner_hold.py mirror` rewrites it by hand), and a clone publishes it. A file row the store lacks
  (a hand edit, a clone not yet synced) is learned into the store by `pipe init --import` or the next mirror; a mod the
  store already holds keeps the store's words. The import may be run any number of times. Added 2026-11-19 by
  `RIMMANDRAKE_BUILD_HOLD_FILE_MIRROR_HE_SAID_COMMISSION_ALL`.
- **plain-paths.** Paths of clones and of the store are made of letters, digits, `-`, `_`, `.` and `/` (259 of 259
  pool clone names [measured 2026-11-19]). A launch with a `$` in one is refused by name before it is admitted. A
  deadline is 1 whole second or more.
- **one-machine.** One user on one Linux machine, the store on its ext4 disk, units under that user's systemd.

Anything else is outside. Some outside inputs are refused by name today; refusing the rest is owed work.

## DOES NOT SURVIVE (not promised; where the store notices, it says so and stops)

- **two-failures-at-once.** A kill that fails while the cgroup also cannot be read. A failed escalation while a second
  kill finishes the same run.
- **cgroup-folder-that-cannot-be-listed.** Linux does not do this for our own user's units: 0 of 66 folders under
  `user.slice` failed to list, and every `cgroup.procs` under our `user@1000.service` was readable [measured 2026-11-19].
  If one ever could not be listed, the kill's walk skips it and reads its processes as none: a folder made
  unlistable on purpose read `empty` (finding 16 of RIMMANDRAKE_FIX_SLICE_REVIEW_TWENTY_FINDINGS_QUEUE_FIRST, 2026-11-19).
- **hand-command-in-a-run's-own-second.** A `pipe void` typed in the instant between a judge's start and its
  reservation. The held look is freed when that judge's process ends.
- **deliberate-bypass.** An agent that calls `systemd-run` by hand. The store is not a security wall.
- **launch-code-in-a-new-shape.** The census of launch sites finds a list whose first word is `systemd-run`; one
  built another way is not seen.
- **corrupt-or-lost-store.** It is not repaired. Nothing launches (a promise below) and `pipe doctor` names the fix.
- **a-store-locked-over-3-seconds.** The command says it could not look and exits 3. A unit kill does not wait.
- **a-unit-launched-with-its-suffix.** A `spec["unit"]` ending in `.service`. `pipe stop` strips the suffix, so
  the stop order is written for the bare name and that run's hook never sees it (finding 14 of
  RIMMANDRAKE_FIX_SLICE_REVIEW_TWENTY_FINDINGS_QUEUE_FIRST, run on real systemd 2026-11-19). No launcher writes one:
  every `launch_unit` call site builds a bare name, and 0 of 170 runs in the live store carry the suffix
  [measured 2026-11-19].
- **an-old-counter-journal.** The old `pipeline_control` journal (`control.jsonl` in its control folder) changed
  after its import, unreadable at `pipe init --import`, or holding a `pc_` count act that `pipe undo` is asked to
  reverse. Then a changed count is imported on top of the first import, a failed import still exits 0, and the `pc_`
  undo reports success while the store's count is unchanged (findings 9, 10 and 11 of RIMMANDRAKE_FIX_SLICE_REVIEW_TWENTY_FINDINGS_QUEUE_FIRST, each reproduced on a
  throwaway store 2026-11-19). No such journal exists on this machine, and the only code that writes one is that
  `pc_` undo [measured 2026-11-19].
- **a-permit-sync-overtaken-by-off-all.** A permit sync that read ON, then `pipe off all` commits and removes the
  permit, then the first sync writes it back; two syncs at once may also share one temp file (finding 12 of RIMMANDRAKE_FIX_SLICE_REVIEW_TWENTY_FINDINGS_QUEUE_FIRST,
  forced by a hook on a throwaway store 2026-11-19). Admission still refuses in the store: only a drop-in-gated
  unit could start in that instant.

Rare failures the code handles today but does not promise to (owner card 2026-11-19, `standing_rulings.md` §A
boundary page before pipeline code, Decision 4: a rare failure is listed here, not fixed and not reviewed):

- **a-fork-while-a-kill-fails.** `systemctl kill` fails and a child forks before the fallback kill (review claim 2.4).
  Today the fallback reads the cgroup again (be673ed895).
- **a-lock-while-a-killed-run-ends.** A kill made on a locked store is booked later, and the run ended in between
  (claim 3.2). Today it is booked by run id (53cb713db1).
- **a-keyed-kill-repeated-on-a-locked-store.** `stop --idem` sent again while the store is locked (claim 3.3). Today
  the replay is read before the kill (53cb713db1); a second SIGKILL to a dead run changes nothing.
- **two-timers-in-one-second.** Two escalation timers of one run come due in the same second (claim 3.5). Today the
  run is reaped once (53cb713db1, 9a8593dc91).
- **a-child-cgroup.** No pipeline unit sets `Delegate=`, so no unit has a child cgroup [measured 2026-11-19, grep of
  `src`]. Today the kill reads the whole subtree (53cb713db1; claim 3.8).
- **a-path-with-a-space.** Outside plain-paths (claim 3.10). Today hook paths are quoted (53cb713db1).
- **a-permit-write-that-fails-after-admission.** The permit's folder cannot be written in the instant after a run is
  admitted. The launch raises and its run waits for `reconcile`, which closes it abandoned.
- **two-threads-one-name.** Outside one-name-one-run (claim 2.1). Today each admission gets its own run id
  (be673ed895).
- **a-crash-between-the-hold-and-its-mirror.** The process dies after the store commits his hold, lift or allowance
  and before the file is rewritten. The store binds; the file is stale until the next mirror; `pipe doctor` prints the
  drift and its fix (`mod_owner_hold.py mirror`). No alarm is raised.
- **a-forged-conductor-window.** A process that sets `AGENT_SEAT=BENCH` and clears `RM_ROLE_UNIT` itself passes
  conductor-lift-only-from-its-window. The seat is a mark, not authentication; no launcher in this estate writes that
  pair into a run [measured 2026-11-19: `detached_helper.py` and `role_clones.py` set `RM_ROLE_UNIT` on every launch].
  No fix (owner 2026-11-19: a rare failure gets none).
- **a-crash-between-the-digest-note-and-the-lift.** The process dies after the Conductor's `delegated: scope` note
  is written and before the store lifts. His digest shows a lift that did not happen; the mod stays held, and the
  next lift notes again and lifts. No fix (a split-second crash).
- **a-run-record-unreadable-right-after-its-kill-mark.** `reap_detached` reads the detached run's record just after
  `mark_killed` wrote it in the same call; if that read fails, the `-return` unit gets this machine's dispatcher state
  dir and seat BENCH instead of the record's (could-not-look lint read, 2026-11-19,
  `RIMMANDRAKE_READ_ONLY_FILES_THAT_FAILED_PILOT_FOUND_ZERO`). No fix (owner by card 2026-11-19: a rare failure gets none).

## PROMISES (each one is owed a test of the same name)

- **off-blocks-starts.** After `pipe off` returns, nothing that had not begun can begin. Tested by `t_race`.
- **one-admission-point.** Every pipeline launch site goes through `launch_unit`, and a site that does not turns the
  selftest red. Tested by `t_sites`.
- **his-hold-refuses-launch.** A launch that names a mod he holds is refused, with his words, until he or the Conductor lifts it.
  `pipe on all` never lifts it. A new hold after a lift holds again. Tested by `t_owner_import`, `t_scope`.
- **three-named-stops.** `pipe stop` is `--write-now`, `--at-easy-spot` or `--kill`. With none named it uses
  at-easy-spot and says so. A live write-now order becomes a kill at its deadline. Tested by `t_stop`.
- **stop-reaches-the-agent.** A writing stop order is shown to the running agent after its next tool call, from the
  run's own clone. Tested by `t_stop_reaches_the_agent`, `t_stop`, `t_hooks_in_run_clone`. Drilled on a real
  `claude -p` (sonnet) in a throwaway unit by `control_agent_drill.py`: it heard `--at-easy-spot` 3.1 s and
  `--write-now` 3.8 s after the order, wrote its note and ended by itself 10-11 s after it [measured 2026-11-19].
- **kill-verified-dead.** `--kill` sends SIGKILL to the run's whole process group and its claude scope at once. It
  reports "killed" only after every process is seen gone. A survivor is reported and nothing is recorded killed. (His
  words, 11:28 AM.) Tested by `t_kill_verified_dead`, `t_stop`, `t_stop_review_fixes`.
- **kill-works-without-the-store.** `pipe stop <unit> --kill` kills by unit name when the store is locked or
  unreadable. Tested by `t_review_claims_round_two`.
- **killed-run-needs-no-hand-step.** A killed detached run's record is closed and its clone returned by the command.
  Tested by `t_killed_run_needs_no_hand_step`, `t_kill_bookkeeping`.
- **stopped-run-spends-no-trial.** A stopped or voided run charges nothing, in the store and in the dispatch books.
  Tested by `t_stopped_run_spends_no_trial`, `t_stop_review_fixes`, `t_void_books_by_run_id`.
- **look-charged-only-on-a-verdict.** A granted look is held before its judge runs and charged only on a valid
  verdict. Of two judges racing for the last look, one gets it. A judge that dies gives it back. Tested by `t_look`,
  `t_coverage_look`.
- **void-gives-back-once.** A voided run's charges come back exactly once. Tested by `t_look`.
- **void-never-moves-a-stage.** A void moves no stage. `pipe show` flags a stage that advanced on a voided run, and
  flags no other run. Tested by `t_void_stage`.
- **unreadable-store-launches-nothing.** With the store missing, corrupt or locked, nothing launches. `pipe show`
  says `CONTROL UNREADABLE` with the cause, or `STORE LOCKED` before the last saved state. Tested by `t_unreadable`.
- **probe-never-lies.** A failed `systemctl` call, an unreadable store or an unreadable `cgroup.procs` file is
  reported as "could not look". It never reads as "nothing there". `pipe doctor` on a store whose write lock is held says locked and exits 3,
  never ok (slice review 17). Tested by `t_probe_never_lies`,
  `t_review_round_four_p1`.
- **same-command-twice.** A void, a settlement, an import or a keyed command sent twice has the effect of once.
  Tested by `t_same_command_twice`, `t_look`, `t_scope`, `t_owner_import`.
- **every-change-is-an-act.** Each change is one record: who, when (Pacific), why, before, after. A write prints at
  most 3 lines. `pipe undo` reverses an act or refuses with the later acts in its way. Tested by
  `t_every_change_is_an_act`, `t_verbs`, `t_accounts`.
- **before-is-read.** `pipe log` prints each act's before beside its after. `pipe undo` of an OFF puts back the switch
  row its before held: an off laid over an earlier off undoes to that earlier off (its why and act), not to ON. A
  count, limit or grant is undone by a compensating act, never by writing its before back: that before is a snapshot,
  and writing it back would erase what was counted since. Added 2026-11-19 by
  `RIMMANDRAKE_USE_OR_DROP_ACT_BEFORE_VALUE_NOBODY_READS` (the before was written and read by nothing). Tested by
  `t_before_is_read`.
- **binds-at-once-from-any-clone.** An act binds when its command returns. It needs no git, publish or tick. Tested
  by `t_clones`.
- **verbs-answer-in-a-second.** A `pipe` verb usually answers in under 1 second on this machine: "usually" is each
  verb's own 95th-percentile time over its calls in `t_verbs` (`p95_of`), not every call. Tested by `t_verbs`.
- **queue-order-is-the-store's.** `pipe queue` sets the order the tick advances mods in, and every view of the
  queue reads it (`pipeline_control.py show` too: slice review 18). Tested by `t_queue`.
- **counts-and-limits-are-adjustments.** `pipe set`, `add`, `reset` and `limit` write a change at a moment; a run
  that finishes afterwards still counts. A look count binds at admission as it reads: a look `pipe set|add` gives
  back can be reserved, and an undone look grant reports the balance admission reads (slice review 7, 8).
  `subjects(res)` lists exactly the accounts holding a live adjustment of `res`, for a reader that judges many in one
  read (`testpilot_route.routed`). Tested by `t_accounts`.
- **a-test-never-touches-the-live-store.** Tested by `t_stop_review_fixes`.
- **a-test-process-starts-no-real-unit.** A test process is defined in one place, `rimflow/test_process.py`: a
  program named `selftest*.py` or `run_selftests.py`, a process with `RM_UNDER_SELFTEST`, or any descendant of one.
  `launch_unit` from a test process, with no runner of its own, is refused before `systemd-run`. A unit of the `probe`
  family (a drill's throwaway) and a launch that passes `runner=` go through. On 2026-11-21 a selftest's helper with a
  clean environment reached the real launcher: two real runs and real items on a fixture mod.
- **a-test-process-never-writes-the-real-ledger.** `model.append` from a test process refuses a write into the ledger
  of the checkout that the code is in, before any byte. A ledger of the test's own (a path, `RIMFLOW_LEDGER`, a
  rebound `model.EVENTS`) takes the event.
- **ended-run-is-recorded-ended.** A unit that ends by itself is recorded ended: its start check and end receipt run
  the first `control.py` still on disk (the run's clone, the launcher's, then the seat clones'), so a clone returned
  before the receipt does not leave its run `started`. A run whose receipt still never ran (systemd reads its unit gone)
  is ended by `pipe doctor`, its stop orders done; a unit systemd cannot read is left started and named UNREADABLE.
  `ops_watch` reads `flow.ghost_runs` every run and alarms on any (`RIMMANDRAKE_END_GHOST_RUN_RECEIPT_NEVER_RAN_LUVL`). Added 2026-11-19 by
  `RIMMANDRAKE_END_GHOST_RUNS_STORE_SAYS_STARTED_SYSTEMD_GONE` (4 runs stayed started for good). Tested by
  `t_end_receipt_outlives_its_clone`.
- **permit-never-ghosts.** The containment permit beside the store follows every `all` switch, from `pipe`, `pipe stop
  all`, `pipe undo` or any caller of `switch()` (slice review 13), and every admitted launch re-writes it, so a timed all-off that lapsed by itself never leaves a
  drop-in-gated unit skipped while its run sits `admitted`. Added 2026-11-19 by
  `RIMMANDRAKE_FORECAST_ON_SHARED_PLANNER_DROPIN_MIRROR_DEADMAN`. Tested by `t_permit_never_ghosts`.
- **reused-name-runs-again.** A `reuse_name` launch is admitted again once its earlier run is over, and refused while
  that run is live. Tested by `t_reused_name_runs_again`.
- **deadline-is-wall-clock.** A write-now order's escalation timer is due at the wall-clock deadline the order
  states (`--on-calendar`, UTC, rounded up to the second), never after a monotonic count: on this WSL2 VM the wall
  clock jumps ahead of the monotonic one, and a 2-minute `--on-active` deadline fired 105 s late, a 30 s one 58.8 s
  late [measured 2026-11-19]. Added by `RIMMANDRAKE_DRILL_REAL_AGENT_WRITING_STOP_ONLY_STANDIN_TESTED`. Tested by
  `t_deadline_is_wall_clock`.
- **undo-disarms-escalation.** `pipe undo` of a write-now stop withdraws its order and disarms that order's timer,
  including when creation of the timer crosses the undo. Other orders keep their timers. If stopping the timer
  fails, the command reports it and the withdrawn order stays ineligible for escalation.
- **next-fits-a-screen.** `pipe next` prints fewer than 1,500 characters: each start with its time and rule (five at
  most, then a count), one line per reason the other mods wait naming every mod, and each UNMEASURED part and role cut
  to one short line. `pipe next --full` prints the dispatch tree's text whole. An unreadable forecast is a failure
  named. Added 2026-11-19 by `RIMMANDRAKE_DRILL_REAL_AGENT_WRITING_STOP_ONLY_STANDIN_TESTED` (the default printed 3,894
  characters). Tested by `t_next_fits_a_screen`.

- **hold-file-mirrors-the-store.** `mod_owner_hold.py hold`, `lift` and `allow-design` write the store first, then
  rewrite `mod_owner_hold.json` from the store's rows of his hold (his order kept, his lifts recorded with his
  words, the Conductor's with `lifted_by CONDUCTOR`). A mirror never drops a row the store lacks: it learns it first. A second mirror changes no byte. `pipe
  doctor` says whether the file is in step. Tested by `t_hold_file_mirrors_the_store`.
- **his-hold-lifts-by-him-or-the-conductor.** Only `mod_owner_hold.py lift <Mod>` lifts his hold: with his words
  (`--said "<his words>"`) or as the Conductor's lift (`--per-ruling RIMMANDRAKE_ENACT_CONDUCTOR_MAY_LIFT_HOLD_NOT_HIM_ALONE
  --why "<reason>"`; owner, by card 2026-11-19: *"yes... but Conductor should also be able to lift a Hold. We work
  together, don't use me as a bottleneck alone."*). `pipe on <Mod>`, `pipe on all`, `pipe undo` of the hold, a lift
  with no or blank words, one citing another ruling, one with no or a blank reason, one carrying both his words and
  the ruling, a hand edit deleting the file's row and an import of that edited file each leave the mod held. A lifted
  mod still does not run while its readiness list is not READY (No mod runs forward on a broken pipeline, owner
  2026-11-19). Tested by `t_his_hold_lifts_by_him_or_the_conductor`.
- **conductor-lift-only-from-its-window.** The Conductor's lift is taken only from the Conductor window: seat BENCH
  (`AGENT_SEAT`, else `RIMFLOW_SEAT`) and no `RM_ROLE_UNIT`. From a launched run (a detached helper, a role run),
  another seat or no seat it is refused, writes no note, and the mod stays held. The Dispatch tick never calls a lift.
  Tested by `t_conductor_lift_only_from_its_window`.
- **conductors-lift-is-its-own-act.** The Conductor's lift is recorded as the Conductor's act, never as his words:
  the store act carries `per_ruling` the ruling's item and no `owner_said`; the mirror's `lifted` row says `lifted_by
  CONDUCTOR` with its reason and no `lifted_said`; a BENCH ledger note whose why starts `delegated: scope:` is written
  first, so his daily digest (`delegated_digest.py`, class scope) shows it. A lift whose note cannot be written lifts
  nothing. Tested by `t_conductors_lift_is_its_own_act`.
- **mirror-failure-is-an-alarm.** A mirror that cannot be written raises the alarm `control:owner_hold_mirror`, says
  ALARM and exits 5. It lifts nothing: a new hold holds from the store, the file is left whole, a lift lifts only the
  mod he named. The next mirror that is written clears the alarm. Tested by `t_mirror_failure_is_an_alarm`.
- **an-unseeded-mod-can-be-switched-off.** `pipe off <Mod>` on a mod with a shipping folder but no concept folder and
  no place on the advancing list writes its OFF row, which every hold reader (`mod_owner_hold.load`) and every launch
  check honours at once; `pipe on <Mod>` then lifts it. A name with neither a concept nor a shipping folder is still
  refused with the nearest names, and `pipe queue` and `pipe grant` still refuse an unseeded mod. Added 2026-11-19 by
  `RIMMANDRAKE_HOLD_NEW_CONCEPT_DISABLED_DESIGNER_CHAINS`. Tested by `t_an_unseeded_mod_can_be_switched_off`.
- **held-stays-held-across-the-mirror.** The shipped hold file, learned into an empty store and mirrored back, holds
  the same mods with the same words, dates and allowances, row for row. Tested by
  `t_held_stays_held_across_the_mirror`.

## LIFE CYCLES (a move not listed here is a defect)

- **run:** admitted → started → ended or killed. admitted → cancelled (an off came first), refused (at its start
  check), failed-to-launch, or abandoned (its launcher died). ended → killed only when a kill and the run's own end
  crossed. A name that never ran, or a `reuse_name` name whose run is over, may be admitted again under a new run id.
- **held look:** held → charged or released. charged → voided.
- **stop order:** pending → seen → done or escalated. escalated → back to pending or seen when the kill failed.
  On withdrawal, pending → withdrawn and seen → withdrawn_owed → withdrawn once the run's hook tells it.
- **switch:** on ↔ off, one row per scope and layer (ours, his). His layer moves only with his words, through
  `mod_owner_hold.py`, and each move rewrites his file's mirror. A timed off
  (`maturation_dispatch.py pause --until`) turns on by itself at its time, with no new act.

The acts' copy in git (`infrastructure/state/control/acts.jsonl`, written by a timer) has its own page:
`design/specs/2026-11-19-control-acts-export/boundary.md`.

Later lists beside this page: `polish.md` (outside claims, not fixed) and `next_version.md` (what 0.2.0 might add).
