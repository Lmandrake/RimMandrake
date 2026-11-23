# BOUNDARY: the SteveDesktop lane drives Steve1 and Steve2 at once, Design Version 0.1.0

Code: `src/RimMandrake/Utils/testq/testq.py` (`STEVE2`, `on_steve`, `steve2_on`, `steve_lanes`, `games_reading`, `remote` with `host`, `worker_for`, `admit` with `host`, `lane_running`, the tick's Steve2 step, `fill_plan`'s busy rule), `infrastructure/stevedesktop/worker.py` (`STEVE_LANE`, `staged_companion`, the kept environment of `spawn`, `proof_verdict`), `src/RimMandrake/Utils/testq/visit_feed.py` (the in-flight rule of `step`), `src/RimMandrake/Utils/testq/fault_monitor.py` (`gate`, `worker_busy`, the not-quarantined count), `src/RimMandrake/Utils/testq/ingest.py` (`env_window`, `ingest_group`'s config), `infrastructure/stevedesktop/sync_test_mods.py` (`site_saves`' extra targets, `--also-saves`), `testq.py`'s `site_stage_argv`.
Item: `RIMMANDRAKE_FILL_BOTH_STEVEDESKTOP_GAMES_HE_SAYS_IT_HOLDS_TWO`, written 2026-11-23. The owner's words that night:
*"Fill up Steve Desktop please... it can support two live games at a time."* Each promise has a test of its name in
`src/RimMandrake/Utils/testq/selftest_testq_steve2.py`. This page covers only these parts of the files named; the rest
of each file has its own page or none.

Game names: Steve1 is lock key `stevedesktop` (testq host `stevedesktop`), Steve2 is lock key `stevedesktop.b` (testq
host `stevedesktop.b`); the map is `src/RimMandrake/rimflow/game_names.py`.

## ACCEPTS (the only inputs this is built for)

- **steve2-on-switch.** `QHOME/steve2.on` exists: the dispatcher drives Steve2. `QHOME/steve2.stop` beside it stops
  Steve2 again. Neither file: Steve2 takes nothing, and the lane is one game as before.
- **steve2-on-the-machine.** On SteveDesktop, Steve2 has its own install (`game_instance.py install b`), its own runner
  clone (`TESTQ_REMOTE_RUNNER_B`, default `~/rm/runner_b`) and its own worker home (`TESTQ_STEVE2_HOME`, default
  `/mnt/d/RimTest/testq.b`). The worker for Steve2 runs with `game_instance.py env b` in its environment.
- **a-job-of-lane-stevedesktop-or-any.** A pending job whose lane is `stevedesktop` or `any`. Lane `stevedesktop`
  names the machine: either game may take it.

## DOES NOT SURVIVE (not promised)

- **a-full-list-on-both-games.** Every SteveDesktop list is a tier of at most the 100 mods on that machine; two such
  games fit in its memory (127.9 GB, 106.5 GB free with Steve1 up at 4.5 GB private, measured 2026-11-23 02:20 PST).
  A list near Archmagi's full 316 mods on both games is not measured.
- **a-third-party-mod-updated-after-steve2s-copy.** Steve2's `Mods` copy of a third-party mod is the copy of the day
  `install b` ran (`install b --refresh` adds and updates). `sync_test_mods.py` writes Steve1's folders only.
- **a-stale-steve2-runner-clone-code.** Steve2's worker pulls `runner_b` before each attempt, as Steve1's does; a
  runner_b that cannot pull refuses the job (REFUSED/SYNC), which pauses Steve2 only.

## PROMISES (each one is owed a test of the same name)

- **steve2-off-by-default.** With no `steve2.on`, a tick sends no command to Steve2's worker, and two waiting jobs
  run one after the other on Steve1.
- **two-jobs-run-at-once-one-per-game.** With `steve2.on` and two ready jobs, one tick admits one job to Steve1 and
  one to Steve2; both attempts are alive at the same time, and each result lands in `done/` with its own host
  (`stevedesktop.b` for Steve2's).
- **steve2-respects-the-machine-pause-and-its-own.** Steve2 admits nothing while `paused.json` (the machine's pause:
  a fault window, a reboot, a hand pause) stands, or while its own `stevedesktop.b_paused.json` stands. Steve2's own
  pause does not stop Steve1. `testq.py resume --lane stevedesktop.b` lifts Steve2's own pause.
- **steve2-stop-file-wins.** `steve2.stop` beside `steve2.on` stops new admissions to Steve2; a running Steve2 job
  is still reconciled to `done/`.
- **steve2-command-carries-its-game.** The remote command for Steve2 runs in `runner_b`, evaluates
  `game_instance.py env b` and fails closed (`&&`) when that fails, and exports Steve2's own TESTQ_HOME, the host
  `stevedesktop.b` and Steve1's companion inbox.
- **filler-fills-an-idle-game.** `fill_plan` reads the lane busy only while a ready job is pending or every live
  Steve game runs a job; with Steve1 running and Steve2 idle it picks.
- **visit-feed-one-mod-per-game.** The visit feed queues a second visit job while one runs, for a different mod,
  when two Steve games are live; never a second job for a mod already in flight, never one while a visit job is
  pending.
- **steve2-results-are-steve-results.** A done record from Steve2 is inside SteveDesktop's fault windows: the fault
  gate quarantines it like Steve1's, ingest's environment check reads the windows for it, and ingest verifies it
  under config `steve-<profile>`.
- **fault-drain-waits-for-both-workers.** `fault_monitor.worker_busy` is True while either worker is busy, so a
  drain-and-reboot never takes Steve2's game mid-job.
- **steve2-worker-is-a-steve-lane.** A worker with `TESTQ_WORKER_HOST=stevedesktop.b` takes the SteveDesktop paths
  (the list reset repair, the kept-game probe, the dump), not the Archmagi ones; it reads its staged companion from
  `TESTQ_COMPANION_INBOX` when that is set; and its detached attempt keeps the `GABP_` port and token of its game.
- **site-saves-reach-steve2.** `sync_test_mods.site_saves` pushes each registered site save into every target Saves
  folder it is given (`--also-saves`), and the tick's copy names Steve2's Saves
  (`/mnt/d/ClaudeWork/rimmandrake/instances/b/Saves`) while Steve2 is switched on. (A Pyrelands job on a game with no
  site save polls 420 s and reads UNMEASURED SITE: RIMMANDRAKE_ROUTE_PYRE_TESTQ_OFF_STEVE_NO_SITE_THERE.)
- **a-tick-with-both-games-busy-writes-the-reading.** Each tick that reached SteveDesktop writes `QHOME/steve_games.json`
  (each game: off, paused, idle or the job it runs; `both_busy`). Only a tick in which both games run a job writes
  `QHOME/steve_both_busy.json` (the two jobs), so its age is the time since both games were last busy together: the
  item's `--live` promise reads it.
- **a-proof-that-crashes-is-unmeasured-not-fail.** A live-proof line that exits 1 with its output ending in an uncaught
  Python exception (a traceback, then an unindented `SomethingError: ...` line, with no PASS or FAIL word after it; an
  exit hook's line such as `[bridge split] ...` may follow) reads UNMEASURED ("crashed: could not look"), never FAIL;
  a FAIL line printed after a quoted traceback stays FAIL. (2026-11-23: the Rot giants' proof died on
  `ModuleNotFoundError: numpy` under SteveDesktop's Windows python and was recorded FAIL, J20261123T115429Z-9dd04f.)
