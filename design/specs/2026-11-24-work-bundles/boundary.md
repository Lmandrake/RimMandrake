# BOUNDARY: work bundles (work_bundle.py and its hooks in the two pipelines), Design Version 0.1.0

Item: `RIMMANDRAKE_BATCH_ONE_MODS_OPEN_WORK_INTO_ONE_RUN_PIPELINE_SPLITS_PER_TICKET`. Design: `design.md` beside this page
(section 7 holds the owner's four decisions). Why: both pipelines launched one run per ticket, and each run loaded the
same system again (design section 1).

Code: `src/RimMandrake/rimflow/work_bundle.py` (all of it), `src/RimMandrake/rimflow/roles/builder.md` (its Work Bundle setting),
`src/RimMandrake/rimflow/roles/list_onboard.md` (the onboarding run), the
bundle hooks in `list_dispatch.py` (`gather`: `work_bundle.overlay`; `decide`: the `in_bundle` and `bundle_refused`
rows and `work_bundle.group`; `execute`: a lead row launches its bundle), the bundle branch of
`left_open_continue.py` (`plan`, `recheck`, `resume_choice`, `header`, `run`, `at_finish`), the `bundle` verb of
`control.py` (`./pipe bundle`), the bundle step of `maturation_autonomy.py` and the bundle section of the Maturation
Pipeline page. Each promise has a test of its name in `src/RimMandrake/rimflow/selftest_work_bundle.py`.

Words. A **system** is one home of `list_home.py` (`pipeline:<part>`, `game:<need>`, `machine:<name>`), one mod
(`mod:<folder>`). A ticket that has no home takes its parent's home (`caused_by`, one hop, never a `mod:` home), else
`cause:<parent>`, else it is `item:<ID>`. A **bundle** is one record that a program writes at
launch: its system, its members, the runs it took, each member's outcome so far, the step. A **member** keeps its own
identity, its own test and its own close. An **outcome** is one of: `fixed` (closed `done` after the bundle began),
`already_fixed` (closed by the reality sort), `dropped` (closed `dropped` or `superseded`), `refused` (a note on the member
since the bundle began whose text starts `REFUSED BY BUNDLE:` (the role's words; `BUNDLE REFUSED:` is read too) and gives a reason), `waits` (a dated wait put on it since the
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
- **a-remote-bundle-whose-host-never-answers.** A marker of a bundle on a host that cannot be read stays live until no
  ledger event has cited it for `REMOTE_QUIET_S` (5 h); a dead remote bundle holds its system that long.
- **a-member-whose-system-moves.** The members are fixed at launch. A ticket re-homed into the system later joins the
  next bundle, not the live one.
- **a-bare-systemctl-stop.** A unit stopped with `systemctl stop` and no `pipe` act reads `killed: signal`, the same
  as a death, so the bundle restarts. Stop a bundle with `./pipe stop` or `pipe off`.
- **two-launchers-at-once.** The store lock is per machine; a launch from another machine is not seen.

## PROMISES (each one is owed a test of the same name)

- **sort-runs-each-members-test-and-closes-only-green.** `sort` runs each open member's test once on the current build.
  `holds` closes the member as already fixed, as the pipeline's act, with the commit the test ran on named in the close
  (`--no-code "already fixed: ... on the build <sha>"` and `--evidence`; that build is often ledger-only, which `--sha`
  refuses); a close that a gate of the ticket refuses is reported with the gate's words and the member is kept; `fails` keeps it; `unmeasured` keeps it and says why; a member with no
  runnable test is listed `no test` and is never closed. No model and no tokens. A named script that holds counts only when git
  shows it added with its ticket (from 6 h before the filing on); one that was there before is `holds_unproven` and is
  kept for the worker, because it was never seen failing on this ticket. A section that reads `Acceptance test: none` is
  no test, whatever script it names (measured 2026-11-24: `RIMMANDRAKE_KILL_LIVE_HOLDER_RESUME_AFTER_FIRST_SESSION` names
  its offline twin there, ALL PASS, and its live half is not done).
- **sort-dry-closes-nothing.** `sort --dry` prints what it would close and writes nothing.
- **members-are-one-system.** A target names one system. Ticket ids whose systems differ are refused, and the refusal
  names each id's system (two systems are never in one bundle). A `mod:` system is never launched by the Workshop
  Pipeline (`list_dispatch` leaves mod work to the Maturation Pipeline, as before).
- **five-tickets-two-fixed-one-run.** The item's acceptance: on five open tickets of one mod, two already fixed, the
  batch command (`work_bundle.bundle_command`, behind `./pipe bundle`) closes the two with the commit named and launches
  exactly one run whose brief lists the other three.
- **each-limit-names-its-danger.** Each number in `work_bundle.py` names the danger it guards beside it.
- **ready-members-only.** A hand launch takes the open members that are ready: not under another live lease, no dated
  wait ahead, not blocked, not waiting on an open item, not refused since its last other event, not held by the owner.
  Each member left out is listed with its reason.
- **one-live-bundle-per-system.** A launch for a system that has a `live` or `restarting` bundle is refused and names
  that bundle. In the lane, a ready item of a system whose bundle is live reads `bundle_live`; a member of the live
  bundle reads `in_bundle`.
- **the-lane-launches-one-bundle-per-system.** In a `list_dispatch` tick, the launch rows of one system become one
  bundle: the first is the lead and takes the slot; the others, and rows of the same system that read `slots_full`
  (before or after the lead), read `bundled` and launch nothing of their own. The lead's bundle also takes each ready open ticket of its system
  that has no lane row (no check: `list_dispatch.join_candidates`; not leased, blocked, waiting, off, held, refused or
  in a live bundle); such a ticket never leads. A home with one ready ticket still gets its run. An `item:<ID>` ticket
  is a bundle of one. `group` bundles no Shape row; the onboarding step after it does (old-tickets-are-onboarded-by-home):
  a Shape row of a home of an on class is a member of that home's onboarding run, and a Shape row of any other home is
  its own Shape run. Test: `t_the_lane_bundles_a_home_not_a_ticket`.
- **a-bundle-on-another-host-launches-there.** A lane lead row whose room is another host (`list_dispatch.host_room`)
  leads a bundle that runs ON that host: `ssh <door> 'cd ~/rm/bench && ./sync && ./pipe bundle <ids> --why ...'`
  (`work_bundle.launch_remote`), so the host's store holds its record and its restarts, and its sort reads a current
  ledger. This store writes a marker (the host's bundle id, `host`, the members the host took, its unit) that reads
  live at once, so no second bundle of the system starts before its worker's first ledger act. Each tick,
  `refresh_remote` copies the host's own record (state, step, restarts, units, outcomes) into the marker; when the
  host's record ends, the marker ends, and each member's attempt reads ended (`overlay`), never unseen. A host that
  refuses (its own live bundle of the system) reads `bundle_live` and spends no attempt; only the members the host
  took get the attempt. The page shows the bundle with its host. Test: `t_a_bundle_on_another_host_launches_there`.
- **a-bundle-on-another-machine-is-live-here.** A bundle that another machine's store holds (`./pipe bundle` run on
  SteveDesktop) is live in this lane while a ledger event cites its id within `REMOTE_QUIET_S`; its system gets no
  second bundle.
- **the-record-is-written-at-launch.** A launch writes the record before it starts the run: system, members, lead, why,
  the state file path, `state` `live`, and the run unit when the launch returns one. A launch that started nothing
  sets `state` `launch_failed` with its output, and no member reads `in_bundle`. A launch that raises (a hung
  launch's timeout, a `ledger_open` fault in the holder) also leaves `launch_failed`, never `launching`, which is live
  and would block the system.
- **the-brief-names-every-member-and-the-role.** The brief lists each member with its title and its test, names the
  role file `roles/builder.md` and its setting Work Bundle, the state file and the bundle id, and states no spend, cap or remainder.
- **the-brief-carries-the-polish-of-its-files.** The brief and the holder's note carry `POLISH_RULE` (the bundle does the
  polish of each file that it changes, and takes each open polish line that names one). A mod bundle's brief lists the
  open lines of `design/concepts/<Mod>/version/polish.md`; any other bundle's brief points at the polish.md beside the
  boundary page of each file that it changes.
- **context-reads-the-own-session.** `work_bundle.py context` prints the session's context tokens, the model's window
  (the newest `contextWindow` in the run's result files, else UNMEASURED) and one verdict: `GO ON`, `SAVE AND RESTART`
  (above half of the window) or `UNMEASURED` with its cause, never a guessed window.
- **outcomes-are-read-from-the-ledger.** Each member's outcome is read from the ledger as the Words above say; the
  record keeps what was read and when.
- **restart-until-each-member-has-an-outcome.** When a bundle run ends (success, a spend stop, or a failure) and a
  member is still open, `left_open_continue` restarts the bundle in a FRESH session, never a resume, from its state
  file and its first brief, on the first open member. A full context, a cap or a death is never a reason to stop. A death by
  signal (`killed: signal`, `killed: unknown`) restarts too. A run stopped by hand (`pipe stop --kill`, whose result is
  `killed: <its reason>`) is not restarted and the bundle reads `stopped`. A voided run, a pipeline pause, an owner hold
  and a `pipe off` refuse the restart, as for any run: the bundle reads `gated`, and its open members are the lane's
  again, owed one more run once the gate lifts.
- **a-restart-that-ended-no-member-raises.** A restart (not the first run) that ended no member since it began is not
  restarted again: the bundle reads `raised`, and one ALARM line in the Conductor log names the bundle, the open
  members and the units. The 3-a-day count of single runs does not apply to a bundle; this guard on progress does.
- **a-restart-cut-short-from-outside-is-restarted.** A restart that ended no member, but whose end was not the work's
  own, is restarted and does not count for the guard on progress. `failure_class.of_run` reads the end, with the stop
  order the run obeyed (`control.run_stop`: delivered by its hook, not a warning, not withdrawn): an account end's
  save order, a `pipe stop` that carries the work on, a kill by a signal, a timeout, a launch that never started. A
  stop by hand (`killed: <its reason>`) keeps act `none`; a stop with `--end` keeps the guard. Seen 2026-11-26 3:35 AM
  PST: an account end's order stopped a restart of bundle `WB-mod-FlowWorks-20261126-052154` at an easy spot, and the
  guard raised.
- **a-restart-that-ended-by-itself-with-no-member-ended-raises.** A restart that ended by itself and ended no member
  raises, with the alarm text above. An order the run never read, a warning and a withdrawn order are not its end, and
  a control store that cannot be read sees no stop (the alarm says so). After a restart cut short from outside is
  restarted, the first restart that ends by itself with no member ended raises.
- **the-real-restart-path-keeps-the-progress-guard.** The count of members ended when a restart begins travels from the
  plan that `finish` writes to the restart's unit on the record, so the guard on progress reads it on the real path, not
  only in a pure call (found by the fresh reader, 2026-11-25: it was always 0, and a restart that ended none restarted
  again for good).
- **a-restart-that-never-starts-leaves-the-bundle-gated.** A planned restart that no step starts (the kick refused, the
  step's own recheck refused, the launch refused) moves the bundle from `restarting` to `gated`, with one Conductor line;
  `restarting` is a live state and would hold its members for good.
- **the-conductor-ends-a-dead-bundle.** `work_bundle.py end <bundle> --why "..."` marks a bundle ended by hand, with its
  reason and one Conductor line: the way out for a run whose finish never ran.
- **a-bundle-with-every-outcome-ends.** When every member has an outcome, the bundle reads `ended`. Each `refused`
  member's reason goes to the Conductor log, once.
- **a-refused-member-is-stopped-with-its-reason.** In the lane, an open member refused in an ended bundle reads
  `stopped`, and its Needs Conductor line quotes the refusal.
- **live-pass-takes-a-free-game-or-says-unrun.** `work_bundle.py live <id> --for "..." -- CMD` asks `game_lock.py
  query` for ArchBig, then ArchSmall, and runs CMD under `game_lock.py run` on the first free one. When no game is free
  (held, his hold, `pipe off`, or could not look), it runs nothing and records `UNRUN` with the exact command and each
  game's answer, in the record and on stdout.
- **a-test-never-writes-the-real-store.** A process under a selftest with no `RM_WORK_BUNDLE_DIR` is refused by name
  (measured 2026-11-25: a holder selftest wrote `WB-mod-WreckedMachines` into the real store).
- **the-page-shows-each-live-bundle.** The Maturation Pipeline page has one short line per live bundle, by meaning:
  the system in plain words (the mod's name, or the pipeline part), the state in plain words, how many of its tickets
  are done, the local start time, a step note that names no ticket, the restarts and a call for help. No ticket name,
  bundle id or unit name is on the page (the records keep them). Bundles that ended or failed to launch are one count
  line. A store that cannot be read is one UNMEASURED line, never an empty block.
- **the-maturation-road-back-is-one-bundle.** On a pilot mod's road back, the holder run (`maturation_dispatch.
  road_back_holder`, which already took every open road-back item in one run) is that mod's one bundle: its record,
  `RM_WORK_BUNDLE` in its env, the bundle named in its brief, and the mod's ready tickets that carry a test joined to it
  (`work_bundle.mod_members`). An old ticket of the mod (no test, no route) joins too while `onboard_classes` puts `mod`
  on (the-mods-own-bundle-onboards-its-old-tickets); a newer ticket with no test stays out. A store that cannot be read
  leaves the holder as before, its line saying
  `work bundle UNMEASURED`. A mod that the owner holds, a mod whose readiness
  list is not READY, and a mod with a live bundle launch no bundle. The mod's version, bars and stage records are not
  written by this step.

### Onboarding old tickets by home (item RIMMANDRAKE_ONBOARD_OLD_TICKETS_BY_HOME_SHAPED_SINGLY_TODAY)

Why: on 2026-11-25 117 of 119 old pipeline and machine tickets had no name for Shape, so the lane launched nothing and
SteveDesktop sat idle; 21 of 28 bundle records held one member; the first 5 hand-named Shape runs each read the repo
again for one ticket and changed no code. Words: an **old ticket** is an open ticket with no outcome check, no routed
part and no shaped split (`list_shape.needs_shape_run`) that is at least `shape_grace_h` old (younger, its filer may
still close it). An **onboarding run** is a bundle record with `onboard` set; its brief is
`src/RimMandrake/rimflow/roles/list_onboard.md` (the reality sort, then the checks, then the work). Code: part 8 of
`work_bundle.py` (`is_old`, `onboard_class`, `onboard_homes`, `onboard_pick`, `onboard_brief`), `onboard_step` and the
onboarding lines of `gather` in `list_dispatch.py`, `onboard_classes` in `list_dispatch.json`.

- **old-tickets-are-onboarded-by-home.** The item's acceptance. In a lane tick with room on a host or on Archmagi, a
  home of a class that `onboard_classes` puts `on`, with open old tickets and no live bundle, gets ONE onboarding run
  whose members are all its ready old tickets, launched by the program; no hand names a ticket. On the base commit
  the lane decided none. A home whose lead or Shape row already holds room starts first (it takes no new room); then
  the home with the most open old tickets takes the next room. Which home holds a ticket that blocks a switched-on mod
  is not readable by program (a readiness list is one prose line of `./pipe why`), so that order is not built. Each home
  is one run: two homes are never in one run, and one home never gets two. Test: `t_old_tickets_are_onboarded_by_home`.
- **an-onboarding-member-is-ready-or-left-out-with-its-reason.** A ticket that is blocked, waits on an open item, has a
  dated wait ahead, is under a live lease, has a live run, is `pipe off`, is held by the owner, is in a live bundle or
  was refused by a bundle since its last other event (a verify, a run's result, is not one) is left out, and the tick's reading names it with its reason.
  A home whose old tickets are all left out starts nothing and says why.
- **the-onboard-classes-are-data.** `onboard_classes` in `list_dispatch.json` says which classes of home the program may
  start: `pipeline` and `machine` on; `game` off (the owner held the sort of the old game-needs tickets on 2026-11-23);
  `mod` on means the mod's own bundle takes them (the-mods-own-bundle-onboards-its-old-tickets): the lane never starts a
  `mod:` home. A ticket with no home of its own (`item:`, `cause:`) is never started. A home of a class that is off or
  has no setting starts nothing, and the reading says which setting holds it. The code path is the same for every class.
- **one-onboarding-beside-no-live-bundle.** A home with a live bundle (here, on a host, or cited on the ledger) starts no
  onboarding run, and the reading names that bundle.
- **an-onboarding-that-could-not-look-starts-nothing.** When the old tickets, their homes or the bundle store could not be
  read, no onboarding run starts and the reading says `could not look` with the cause (one blind row, counted by
  `blind_hold`).
- **a-home-lead-takes-its-old-tickets.** When the tick already has a bundle lead for a home of an on class (a ticket with
  a check), that lead's bundle takes the home's ready old tickets and is the home's onboarding run. A Shape row of such a
  home (a hand-named ticket) is a member and reads `bundled`; when no lead exists, the first Shape row of the home leads
  the onboarding run in the room it already has. A Shape run that is live is not stopped.
- **the-onboarding-brief-sorts-before-it-checks.** The brief of an onboarding run names its role file
  `roles/list_onboard.md`, the bundle id and state file, each member with its title, step A (the reality sort, before
  any check is written), step B (group, write each check red with its `fooled_by` line), step C (the work, by the role
  `roles/builder.md`, setting Work Bundle), the two tests of `fixer_rule.py`, the polish rule, and the rule that old work
  is filtered before any process takes it. It states no spend, cap or remainder.
- **a-routed-member-has-an-outcome.** A member that the run routes (`rimflow shape --parts` with a routed part, since the
  bundle began) reads the outcome `routed`; it is not open, so the bundle does not restart for it.
- **an-onboarding-on-a-host-keeps-its-old-tickets.** An onboarding run whose room is a host launches there with
  `./pipe bundle <ids> --onboard`. `--onboard` keeps an old ticket that the age filter (`age_refusal`) would leave out
  UNVETTED: the run's own step A and step B are that filter, and no member is worked before its check is seen red
  today. Without `--onboard` the age filter stands as before.
- **the-page-shows-each-onboarding-run.** The page line of a live onboarding run says it onboards old tickets, its home,
  the count of its members and the count of each outcome so far; the count line counts the onboarding runs that ended.
- **the-mods-own-bundle-onboards-its-old-tickets.** `mod_members` with `mod` on takes each ready old ticket of the mod
  (no test) into the mod's bundle, and the holder's note sends those members through `roles/list_onboard.md`. With
  `mod` off, a ticket with no test stays out.

## PLANNED (built part by part; each moves up to PROMISES, with its test, when its part lands)

(none)

Later lists beside this page: `polish.md`.
