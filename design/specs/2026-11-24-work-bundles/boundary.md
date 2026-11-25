# BOUNDARY: work bundles (work_bundle.py and its hooks in the two pipelines), Design Version 0.1.0

Item: `RIMMANDRAKE_BATCH_ONE_MODS_OPEN_WORK_INTO_ONE_RUN_PIPELINE_SPLITS_PER_TICKET`. Design: `design.md` beside this page
(section 7 holds the owner's four decisions). Why: both pipelines launched one run per ticket, and each run loaded the
same system again (design section 1).

Code: `src/RimMandrake/rimflow/work_bundle.py` (all of it), `src/RimMandrake/rimflow/roles/bundle_worker.md`, the
bundle hooks in `list_dispatch.py` (`gather`: `work_bundle.overlay`; `decide`: the `in_bundle` and `bundle_refused`
rows and `work_bundle.group`; `execute`: a lead row launches its bundle), the bundle branch of
`left_open_continue.py` (`plan`, `recheck`, `resume_choice`, `header`, `run`, `at_finish`), the `bundle` verb of
`control.py` (`./pipe bundle`), the bundle step of `maturation_autonomy.py` and the bundle section of the Maturation
Pipeline page. Each promise has a test of its name in `src/RimMandrake/rimflow/selftest_work_bundle.py`.

Words. A **system** is one home of `list_home.py` (`pipeline:<part>`, `game:<need>`, `machine:<name>`), one mod
(`mod:<folder>`), or `item:<ID>` for a ticket that has no home. A **bundle** is one record that a program writes at
launch: its system, its members, the runs it took, each member's outcome so far, the step. A **member** keeps its own
identity, its own test and its own close. An **outcome** is one of: `fixed` (closed `done` after the bundle began),
`already_fixed` (closed by the reality sort), `dropped` (closed `dropped` or `superseded`), `refused` (a note on the member
since the bundle began whose text starts `BUNDLE REFUSED:` and gives a reason), `waits` (a dated wait put on it since the
bundle began). A member with none of these is **open**.

## ACCEPTS (the only inputs this is built for)

- **a-target.** For the sort and a hand launch: one home (`pipeline:ledger`), one mod name (`FlowWorks` or
  `mod:FlowWorks`), or ticket ids that share one system.
- **the-ledger.** `model.replay()` in the clone that the command runs in: each item's state, `effect`, `home`, notes,
  wait and lease. `mod_work.reading` says which mod a ticket belongs to.
- **a-ticket-test.** The ticket's outcome check (`effect`, run by `list_effect.run`), else the first
  `python3 <repo path>.py` in its `## verify`, `## criteria` or `## acceptance` prose whose file exists (run with no
  arguments, exit 0 holds, 1 fails, any other exit unmeasured).
- **the-run-records.** `detached_helper` records: a bundle run carries `RM_WORK_BUNDLE=<bundle id>` in its env, and so
  does each restart, because a continuation carries the env of the run before it.
- **the-store.** `<RM_DISPATCHER_STATE>/work_bundle/bundles/<id>.json` (`RM_WORK_BUNDLE_DIR` overrides), written whole.

## DOES NOT SURVIVE (not promised)

- **a-test-that-passes-for-the-wrong-reason.** The sort trusts a green test and closes the ticket. A test that holds
  vacuously (`true`, `echo`) is unmeasured (`list_effect.VACUOUS`), nothing more.
- **a-run-whose-finish-never-ran.** A restart is planned in `finish` (the unit's ExecStopPost), which runs on every
  end, a kill included. A unit whose ExecStopPost never ran leaves its bundle `live` with a dead unit; the page shows
  the bundle as `dead, no finish` and the members stay in it until the Conductor ends it (`work_bundle.py end`).
- **a-bundle-on-another-host.** A bundle runs on this machine: its record and its restart are here. A lane bundle whose
  only room is another host waits for a local slot.
- **a-member-whose-system-moves.** The members are fixed at launch. A ticket re-homed into the system later joins the
  next bundle, not the live one.
- **two-launchers-at-once.** The store lock is per machine; a launch from another machine is not seen.

## PROMISES (each one is owed a test of the same name)

- **sort-runs-each-members-test-and-closes-only-green.** `sort` runs each open member's test once on the current build.
  `holds` closes the member as already fixed, as the pipeline's act, with the commit the test ran on named in the close
  (`--sha <origin/main sha>` and `--evidence`); `fails` keeps it; `unmeasured` keeps it and says why; a member with no
  runnable test is listed `no test` and is never closed. No model and no tokens. A named script that holds counts only when git
  shows it added with its ticket (from 6 h before the filing on); one that was there before is `holds_unproven` and is
  kept for the worker, because it was never seen failing on this ticket. A section that reads `Acceptance test: none` is
  no test, whatever script it names (measured 2026-11-24: `RIMMANDRAKE_KILL_LIVE_HOLDER_RESUME_AFTER_FIRST_SESSION` names
  its offline twin there, ALL PASS, and its live half is not done).
- **sort-dry-closes-nothing.** `sort --dry` prints what it would close and writes nothing.
- **members-are-one-system.** A target names one system. Ticket ids whose systems differ are refused, and the refusal
  names each id's system (two systems are never in one bundle). A `mod:` system is never launched by the Workshop
  Pipeline (`list_dispatch` leaves mod work to the Maturation Pipeline, as before).
- **each-limit-names-its-danger.** Each number in `work_bundle.py` names the danger it guards beside it.

## PLANNED (built part by part; each moves up to PROMISES, with its test, when its part lands)

- *ready-members-only.* A hand launch takes the open members that are ready: not under another live lease, no dated
  wait ahead, not blocked, not waiting on an open item, not refused since its last other event, not held by the owner.
  Each member left out is listed with its reason.
- *one-live-bundle-per-system.* A launch for a system that has a `live` or `restarting` bundle is refused and names
  that bundle. In the lane, a ready item of a system whose bundle is live reads `bundle_live`; a member of the live
  bundle reads `in_bundle`.
- *the-lane-launches-one-bundle-per-system.* In a `list_dispatch` tick, the launch rows of one system become one
  bundle: the first is the lead and takes the slot; the others, and rows of the same system that read `slots_full`,
  read `bundled` and launch nothing of their own. A ticket with no home is a bundle of one (`item:<ID>`). Shape runs are
  not bundled.
- *the-record-is-written-at-launch.* A launch writes the record before it starts the run: system, members, lead, why,
  the state file path, `state` `live`, and the run unit when the launch returns one. A launch that started nothing
  sets `state` `launch_failed` with its output, and no member reads `in_bundle`.
- *the-brief-names-every-member-and-the-role.* The brief lists each member with its title and its test, names the
  role file `roles/bundle_worker.md`, the state file and the bundle id, and states no spend, cap or remainder.
- *outcomes-are-read-from-the-ledger.* Each member's outcome is read from the ledger as the Words above say; the
  record keeps what was read and when.
- *restart-until-each-member-has-an-outcome.* When a bundle run ends (success, a spend stop, or a failure) and a
  member is still open, `left_open_continue` restarts the bundle in a FRESH session, never a resume, from its state
  file and its first brief, on the first open member. A full context, a cap or a death is never a reason to stop. A run
  ended by hand (`killed`), a voided run, a pipeline pause, an owner hold and a `pipe off` stop it, as for any run.
- *a-restart-that-ended-no-member-raises.* A restart (not the first run) that ended no member since it began is not
  restarted again: the bundle reads `raised`, and one ALARM line in the Conductor log names the bundle, the open
  members and the units. The 3-a-day count of single runs does not apply to a bundle; this guard on progress does.
- *a-bundle-with-every-outcome-ends.* When every member has an outcome, the bundle reads `ended`. Each `refused`
  member's reason goes to the Conductor log, once.
- *a-refused-member-is-stopped-with-its-reason.* In the lane, an open member refused in an ended bundle reads
  `stopped`, and its Needs Conductor line quotes the refusal.
- *context-reads-the-own-session.* `work_bundle.py context` prints the session's context tokens, the model's window
  (the newest `contextWindow` in the run's result files, else UNMEASURED) and one verdict: `GO ON`, `SAVE AND RESTART`
  (above half of the window) or `UNMEASURED` with its cause, never a guessed window.
- *live-pass-takes-a-free-game-or-says-unrun.* `work_bundle.py live <id> --for "..." -- CMD` asks `game_lock.py
  query` for ArchBig, then ArchSmall, and runs CMD under `game_lock.py run` on the first free one. When no game is free
  (held, his hold, `pipe off`, or could not look), it runs nothing and records `UNRUN` with the exact command and each
  game's answer, in the record and on stdout.
- *the-maturation-road-back-is-one-bundle.* On a mod's road back, the open road-back items and the ready tickets with
  that mod's home are one bundle of that mod, not one fixer run each. A mod that the owner holds, a mod whose readiness
  list is not READY, and a mod with a live bundle launch no bundle. The mod's version, bars and stage records are not
  written by this step.
- *the-page-shows-each-live-bundle.* The Maturation Pipeline page has one block per bundle that is not ended: system,
  step, restarts, each member with its outcome, and the state; a store that cannot be read is one UNMEASURED line,
  never an empty block.

Later lists beside this page: `polish.md`.
