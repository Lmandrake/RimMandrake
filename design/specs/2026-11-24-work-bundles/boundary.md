# BOUNDARY: work bundles (work_bundle.py and its hooks in the two pipelines), Design Version 0.1.0

Item: `RIMMANDRAKE_BATCH_ONE_MODS_OPEN_WORK_INTO_ONE_RUN_PIPELINE_SPLITS_PER_TICKET`. Design: `design.md` beside this page
(section 7 holds the owner's four decisions). Why: both pipelines launched one run per ticket, and each run loaded the
same system again (design section 1).

Code: `src/RimMandrake/rimflow/work_bundle.py` (all of it), `src/RimMandrake/rimflow/roles/builder.md` (its Work Bundle setting),
`src/RimMandrake/rimflow/roles/list_onboard.md` (the onboarding run), `src/RimMandrake/rimflow/bundle_replay.py` (the
offline simulation of the lane's bundling), the
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
bundle began), `routed` and `rehomed` (see their promises). A member with none of these is **open**.

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
- **a-member-whose-system-moves.** The members are fixed at launch, until a restart takes the home's new tickets
  (a-live-bundle-takes-its-homes-new-tickets-at-restart). A ticket re-homed into the system while the bundle's last run
  works joins the next bundle. A ticket that leaves the system stays a member.
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
  took get the attempt. A host whose sort leaves every member out reads `no_bundle`; the lead's row names its own
  reason from the host, as each other member's `host_left_out` row does. The page shows the bundle with its host.
  Test: `t_a_bundle_on_another_host_launches_there`.
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
  members and the unit of the restart that ended none. The 3-a-day count of single runs does not apply to a bundle; this guard on progress does.
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
- **a-code-bundle-gets-one-fresh-read.** When a bundle ends (finish, in its run's clone; or `end` by hand), its
  commits are read: those on origin/main since it began whose message names a member or the bundle. When they change
  code (not the ledger, the bundle state files, design prose or media), and a file of it still owes a read
  (`fresh_reader.owed_paths`: READ-CLEAN or FLAGGED owes none; a file that an open reader ticket names owes none), the end files one `fresh_reader` ticket per fix sha,
  each over the files whose newest bundle commit is that sha, and the ticket lane launches the reader. A reader ticket
  that exists already for that fix and those files (the worker filed it, `fresh_reader.resolve`) counts as filed: no
  second filing and no "by hand" line. The bundle records `reader` (with `tickets`, one per fix sha); a second end files none. A bundle with no code
  change, or one already read, files none. Commits that cannot be read file nothing, record nothing, and reach the
  Conductor log. Measured 2026-11-26: three bundle fixes ended unread (c7dd53c26a, 062867f85d, e283fe2c2d62).
- **a-refused-member-is-stopped-with-its-reason.** In the lane, an open member refused in an ended bundle reads
  `stopped`, and its Needs Conductor line quotes the refusal.
- **live-pass-takes-a-free-game-or-says-unrun.** `work_bundle.py live <id> --for "..." -- CMD` asks `game_lock.py
  query` for the games of the machine it runs on (ArchBig, then ArchSmall; on SteveDesktop, Steve1, then Steve2), and runs CMD under `game_lock.py run` on the first free one. When no game is free
  (held, his hold, `pipe off`, or could not look), it runs nothing and records `UNRUN` with the exact command and each
  game's answer, in the record and on stdout.
- **live-pass-asks-the-games-of-this-machine.** The games are the machine's own, from `game_names.GAMES`: on
  SteveDesktop, where the lane's bundles run, a live check takes Steve1 or Steve2. A game of another machine is never
  asked (measured 2026-11-27: SteveDesktop asked ArchBig and ArchSmall, both refused there, and every check read UNRUN).
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
- **an-archmagi-only-home-runs-on-archmagi.** A home that `archmagi_only_homes` in `list_dispatch.json` names (home ->
  the tools only Archmagi has) takes Archmagi's room for its onboarding run, never a host's, though a host has room;
  every other home still goes to a host first. Measured 2026-11-26: the onboarding run of `game:art-canon` went to
  SteveDesktop, where the art queue, art_eval and its observed inventory are absent. Test:
  `t_an_archmagi_only_home_runs_on_archmagi`.
- **an-onboarding-run-goes-where-its-members-can-be-worked.** A home with a member whose `needs` is not offline (a
  deploy, the game, a harvest) takes Archmagi's room for its onboarding run, never a host's: a host gives offline work
  only. A host whose work switch reads pipeline work only refuses a `game:` home, whose tickets build or fix mods.
  Measured 2026-11-26: `WB-game-research-tree-20261126-210323` went to SteveDesktop, a switched host, though its one
  member needs the bridge. Test: `t_an_onboarding_run_goes_where_its_members_can_be_worked`.
- **an-onboarding-member-is-ready-or-left-out-with-its-reason.** A ticket that is blocked, waits on an open item, has a
  dated wait ahead, is under a live lease, has a live run, is `pipe off`, is held by the owner, is in a live bundle or
  was refused by a bundle since its last other event (a verify, a run's result, is not one) is left out, and the tick's reading names it with its reason.
  A home whose old tickets are all left out starts nothing and says why.
- **the-onboard-classes-are-data.** `onboard_classes` in `list_dispatch.json` says which classes of home the program may
  start; the setting, not this page, says which class is on today (its `_onboard_classes_doc` says why: `game` is off since
  2026-11-26 7:35 PM PST by the owner's card answer, `RIMMANDRAKE_THROTTLE_GAME_WORK_WHEN_REPAIRS_END_ROOM_SHORT`);
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
- **a-rehomed-member-has-an-outcome.** A member whose home (`rimflow home`) moved to another system since the bundle
  began reads the outcome `rehomed`; it is not open, so no restart names it and the bundle can end without it. A re-home
  before the bundle began, or to the bundle's own system, changes nothing.
- **an-onboarding-on-a-host-keeps-its-old-tickets.** An onboarding run whose room is a host launches there with
  `./pipe bundle <ids> --onboard`. `--onboard` keeps an old ticket that the age filter (`age_refusal`) would leave out
  UNVETTED: the run's own step A and step B are that filter, and no member is worked before its check is seen red
  today. Without `--onboard` the age filter stands as before.
- **the-page-shows-each-onboarding-run.** The page line of a live onboarding run says it onboards old tickets, its home,
  the count of its members and the count of each outcome so far; the count line counts the onboarding runs that ended.
- **the-mods-own-bundle-onboards-its-old-tickets.** `mod_members` with `mod` on takes each ready old ticket of the mod
  (no test) into the mod's bundle, and the holder's note sends those members through `roles/list_onboard.md`. With
  `mod` off, a ticket with no test stays out.
- **a-mod-bundle-takes-an-old-ticket-past-a-block-with-no-end.** With `mod` on, an old ticket of the mod whose block has
  no end (`list_dispatch.block_end`) and is idle `block_idle_days` joins the mod's bundle (`ready_split` with `stale`);
  any other block still keeps a ticket out. The holder's note names each such member and asks the run to drop a stale or
  wrong ticket first, then type its block (`rimflow block --kind`) or lift it. Decision: the Conductor, 2026-11-26
  (`design/specs/2026-11-26-testless-tickets/conductor_decisions.md`, question 2): a mod's ticket never goes to a lane
  Shape run, so its own route settles the block.

### Large bundles by home (item RIMMANDRAKE_FILL_BUNDLES_BY_HOME_HOLD_MEDIAN_ONE_TODAY)

Why: the median ended bundle held 1 ticket on 2026-11-25, 26 and 27. Measured over the Archmagi store (SteveDesktop's
markers included), the bundles that ended on Nov 26 and 27 by the rule that made their size: lane `item:` 73 (73
singles; 71 of them fresh-reader tickets, which have no home and no cause), lane onboarding of `pipeline:` homes 39 (29),
of `game:` homes 39 (21), of `machine:` homes 4 (3), lane `cause:` 16 (12), lane `game:` 6 (3), lane `pipeline:` 6 (6),
the Maturation Pipeline's mod bundles 2 (0). Code: `list_home.reader_home`, the reader branch of
`work_bundle.system_of`, `work_bundle.hold_systems`, `urgent_why`, `readiness_blocks`, `read_fold`, `read_fold_text`
(in `brief`), the hold pass of `list_dispatch.decide` (`_decide` is one pass), the urgent facts of `gather`
(`readiness_texts`), `bundle_hold_h` and `bundle_full_n` in `list_dispatch.json`, and the offline simulation
`bundle_replay.py` over the fixture `arrivals_2026-11-23_to_27.json` beside this page. Tests: `selftest_bundle_hold.py`,
one function per promise below, by name. Offline simulation: yes, `bundle_replay.py` replays the real arrivals of Nov 23
to 27 through the real `system_of`, `group` and `hold_systems` with a fake clock; it does not model restarts, a run's own
closes, the checks (every arrival is ready) or the onboarding route's old-ticket filter. `replay_live` models the live
routes (the section below).

- **every-lane-ticket-has-a-real-home.** A fresh-reader ticket's system is the home of the area of its first file:
  `pipeline:read-rimflow`, `pipeline:read-utils`, else `pipeline:read-other` (`list_home.reader_home`), never
  `item:<ID>`. A ticket's own home and its mod still come first. The home is a rule that the lane reads at each tick, not
  a ledger write: the reader tickets that exist got it at once.
- **a-home-holds-until-five-or-the-hold-time.** In a lane tick, a lead bundle with fewer than `bundle_full_n` members, no
  urgent member, and an oldest member that has waited less than `bundle_hold_h`, does not start: each of its rows reads
  `bundle_hold`, with the size and the latest start. The hold is decided before the room gates (a pass of `_decide` on a
  copy of the state finds the held homes), so a held home takes no slot from another home. A ticket's wait counts from
  its first ready tick (`ready_at` in the lane's state; a wait for room or for the home's live bundle counts too).
- **the-replay-of-nov-27-reads-a-median-of-five.** The replay of Nov 27 reads a median under 5 in the parent's form (no
  hold, no reader home) and 5 or more at the shipped settings; with the hold at 0, or the reader home off, it reads under
  5 (each a planted fault).
- **no-ticket-waits-past-the-hold-time.** In the replay, no ticket is held for its bundle longer than `bundle_hold_h`.
  A wait for room (all slots live) is not a wait for the hold.
- **an-urgent-ticket-never-waits.** An Ops alarm item (`OPS_` or `RIMMANDRAKE_OPS_` id), a ticket whose live promise is
  broken, and a ticket that the newest readiness list of an advancing mod that the owner does not hold marks BLOCKS
  (`readiness_blocks`: a line that names the ticket and BLOCKS; a "No BLOCKS" line names none) is urgent. Its row goes
  first in the tick, its home is not held, and its bundle takes the home's ready tickets with it. In the replay a planted
  urgent ticket starts in the tick that first sees it, and with the rule off it waits for the hold. Readiness lists that
  cannot be read mark no ticket urgent, said on stderr: such a ticket waits the hold at most.
- **the-lane-holds-before-its-room-gates.** With one slot, a held home and a home past its hold: the slot goes to the
  home past its hold; each ready row keeps its first ready tick; an urgent row goes first.
- **fresh-reader-tickets-fold.** A bundle's brief lists each file that its reader members name ONCE, with the tickets
  that one read covers (`read_fold`); one read at the present bytes makes each covering ticket's check hold
  (`fresh_reader.holds` reads the present bytes). While the code review pause is on, the reader rows read `off` and no
  read bundle starts.
- **a-live-bundle-takes-its-homes-new-tickets-at-restart.** A ready ticket of a home whose bundle is live reads
  `bundle_live`, and so does a joining ticket with no lane row (`join_candidates`). Each applied lane tick writes them on
  the live bundle's record in this store (`waiting`, replaced each tick; `work_bundle.waiting_of`, `note_waiting`); a
  dry tick writes nothing, and a bundle whose record is on another host is not written. When a run of the bundle ends
  with a member open, the restart takes each waiting ticket whose outcome still reads open (`take_waiting`): the
  restart's brief names it, and the record's members take it when the restart starts (`note_restart`). A waiting ticket
  that closed meanwhile is not taken. A bundle that ends takes none: the home's next bundle starts it. The progress guard
  counts the old members only. Before 2026-11-28 each such ticket started a second bundle of the home on the same files.

### The live routes in the replay (item RIMMANDRAKE_BUNDLE_SHAPE_ROWS_BY_HOME_HOLD_HELD_NOTHING)

Why: the check of 2026-11-27 (`large_bundles_check_2026-11-27.md`) found that the hold acts on no live launch: a Shape
row is never held (`list_dispatch._decide`, the `not (judge or shape ...)` gate), an onboarding run reads no hold
(`onboard_step`), and a ticket of a `cause:` or `item:` home starts as a Shape run of its own. The replay above holds
every arrival, so its median of 5 came from the reader tickets that the code review pause holds. Code:
`bundle_replay.replay_live`, `live_route`, `RULES`, `build_live`, `live_lane`; the frozen fixture
`arrivals_live_2026-11-23_to_27.json` beside this page (1291 arrivals: each ticket filed 2026-11-23 to 27 PST, from the
ledger at 8b1c582d0f, with the times of its check, route, claim, home and close; plus 166 old tickets that an onboarding
run took; plus the live lane's own figures of each day). Offline simulation: yes, the real `system_of`, `urgent_why` and
`hold_systems` with a fake clock, as above; it does not model restarts, reruns of one ticket, judge and lane-cause runs,
tickets filed before 2026-11-23 that were not onboarded, or the load and account gates.

The measurement (MEASURED, 2026-11-27 11:55 PM PST; `python3 src/RimMandrake/rimflow/bundle_replay.py --live --sweep
--day <day>`). The code review tickets and the game work are left out, as the two pauses stand. Each run is one bundle;
a Shape run of its own is a bundle of 1.

| rule | hold | Nov 25 runs / median / singles | Nov 26 | Nov 27 | longest wait |
|---|---|---|---|---|---|
| `live` (the code of ed14a18611) | 4 h | 55 / 1 / 53 | 49 / 1 / 38 | 44 / 1 / 41 | 4.7 h |
| `no_item_hold` (an `item:` bundle is not held) | 4 h | 55 / 1 / 53 | 49 / 1 / 38 | 44 / 1 / 41 | 4.7 h |
| `shape_by_home` (the Shape rows of one home in one tick are one run; the hold applies to them and to an onboarding run; no `item:` hold) | 4 h | 49 / 1 / 45 | 45 / 1 / 33 | 39 / 1 / 31 | 4.2 h |
| `shape_by_home_cause` (also: a `cause:` home onboards its old tickets) | 4 h | 49 / 1 / 45 | 45 / 1 / 33 | 39 / 1 / 31 | 4.2 h |
| `shape_by_home_nohold` (Shape rows grouped, not held) | 4 h | 54 / 1 / 51 | 49 / 1 / 38 | 44 / 1 / 41 | 4.7 h |

Each rule at each hold from 0 to 24 h reads median 1 on each day. The replay reads close to the live lane: on Nov 27,
with the game work kept in (the game pause began that morning), the `live` rule reads 56 runs, median 1, 53 singles (95%);
the lane read 70 launches, median 1, 64 singles (91%). The lane's 14 more launches are reruns, judge and lane-cause runs
and tickets older than the fixture.

**The pick: no rule is built.** No rule raises the median above the present reading of 1, so none keeps the three
promises (an urgent ticket never waits; no ticket waits longer than the hold time; one home never has two bundles on the
same files) and gives more. The reason is the arrivals, not the rule. With one bundle per system for a whole day (the
largest any rule of one system per bundle can make), the arrivals read median 1: Nov 25 44 systems, 40 of them one
ticket; Nov 26 35 and 25; Nov 27 33 and 28. A home walked up the whole chain of causes (`list_home.rule_home`; the
system has one hop on purpose, above) still reads median 1: Nov 27 27 systems, 20 of one ticket. `shape_by_home` at 4 h
cuts the singles of Nov 27 from 41 to 31 and the runs from 44 to 39, but the median stays 1. The lever that the numbers
show is the code review pause (median 5 with the reader tickets, 1 without; `large_bundles_check_2026-11-27.md` §5), which
is his order.

The wait `shape_grace_h` (24 h) guards a danger that happens: a Shape run spent on a ticket that its filer is about to
close or claim. Of the 415 tickets that a window filed (no `role_unit`: the Conductor, his seat and programs outside a
helper) on 2026-11-23 to 27 with no check, 293 closed within 24 h and 217 were closed, claimed, checked or routed within
1 h (MEASURED from the ledger, the same fixture). So the wait stays for a ticket that the Conductor files; its doc in
`list_dispatch.json` names the danger and this evidence.

- **the-live-replay-models-the-live-routes.** `replay_live` makes a ticket with no check unseen for `shape_grace_h`, then
  a Shape row; under the rule `live` a Shape row and an onboarding run are never held, the old and Shape tickets of a
  `pipeline:` home are one onboarding run, a `cause:` or `item:` Shape row is a run of its own, an old ticket of a
  `cause:` home never starts, a checked bundle (an `item:` one too) waits the hold, and an `OPS_` ticket starts at once
  with its home's ready tickets. A ticket that its filer claimed or closed first never arrives; the code review switch
  leaves out a reader ticket. Under `shape_by_home` the Shape rows of one `cause:` home are one run held for the hold,
  and an `item:` ticket is never held. An empty tick starts nothing. Seen red on the parent (no `replay_live`) and on
  seven planted faults, each caught: no grace, the hold on onboarding, no urgent rule, an `item:` hold, no Shape grouping,
  a filer's claim ignored, the review switch ignored. Test: `t_the_live_replay_models_the_live_routes`.
- **the-live-replay-reads-close-to-the-lane.** On the frozen fixture, the `live` rule's replay of Nov 27 reads the live
  lane's median (1) and its share of singles within 10 points, and one bundle per system for a whole day reads median 1
  on Nov 25, 26 and 27. Test: `t_the_live_replay_reads_close_to_the_lane`.

The page's line on the size of the bundles (the median members and the singles of the last 24 h) is a promise of
`design/specs/2026-11-22-non-mod-pipeline-section/boundary.md`, the page of `maturation_nonmod.py`.

Later lists beside this page: `polish.md`.
