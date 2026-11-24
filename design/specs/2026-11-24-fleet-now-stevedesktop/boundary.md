# BOUNDARY: the SteveDesktop part of RELENTLESS_NOW.md, Design Version 0.1.0

Code: `src/RimMandrake/Utils/running_now.py`, only these parts: `STEVE_SCRIPT`, `probe_steve`, `collect_steve`,
`collect_steve_games`, `steve_jobs`, `steve_view_block`, `steve_svg`, `steve_text` and the SteveDesktop chips of `status_strip`.
`running_now.py` writes `RELENTLESS_NOW.md` each minute (`rm-running.timer`). Item:
`RIMMANDRAKE_RESTORE_STEVEDESKTOP_ON_FLEET_NOW_OLD_PAGE_HAD_IT`. The owner, 2026-11-24 about 1:30 PM PST: *"FLEET_NOW.md
should also show Steve Desktop. The old Relentless one did. We need it back. Machine stats, the jobs its running, just
like Archmagi supports. Use GPT."* Each promise has a test of its name in
`src/RimMandrake/Utils/selftest_fleet_now_steve.py`, which reads the checks named `<promise>: ...` of `selftest_running_now.py`.

## ACCEPTS (the only inputs this is built for)

- **the-probe-cache.** `conductor/running_steve.json`, written by `probe_steve` after the page is on disk (one ssh at most
  every 180 s). It holds the machine stats, the game and driver readings and the running services.
- **the-test-lane-folder.** `testq/running/`, `testq/pending/`, `testq/done/`, `testq/steward.json` on Archmagi, written by the lane.

## DOES NOT SURVIVE (not promised)

- **a-runner-clone-that-is-gone.** The game and driver readings come from SteveDesktop's `~/rm/runner` clone. Without it
  they read UNMEASURED with the cause. The machine stats do not need it.

## PROMISES (each one is owed a test of the same name)

- **steve-games-up-and-driver.** The panel has one line each for Steve1 and Steve2: up or down, who drives it and for what,
  read from SteveDesktop's own process list and driver locks in the one ssh probe. A job id in a lock's purpose is shown
  with the job's mod and what it runs, from `testq/running/`.
- **steve-jobs-by-name.** The panel names each job of the lane that runs and that is queued: its mod, its purpose, its
  chains, and how long it has run or waited; and each service that runs on SteveDesktop that is not a lane job. A list
  longer than the panel shows the first ones and a count of the rest.
- **steve-every-reading-has-its-age.** The machine stats, the games, the services, the lane folder and the steward line each
  show the age of their reading.
- **steve-unread-is-unmeasured-with-cause.** A missing, broken or old source shows UNMEASURED and the cause. It never shows
  a 0, "idle", "down", "free", "none" or an empty list. A machine reading older than STEVE_STALE shows UNMEASURED with its age
  and the failure, not the old figures. A source that was read and is empty says "none" or 0.
- **steve-no-second-connection.** The page is written before the one ssh; building it opens no connection. One ssh, not two.
- **steve-view-for-augur.** Each probe write also puts a decoded `view` block (schema `augur.remote_host/1`) in
  `running_steve.json`, for the Augur dashboard's FLEET_NOW.md: the machine figures as numbers with their reading time,
  each game up or down with its driver, purpose and job, and this host's running and queued jobs by name, place and start
  time. A part that cannot be read is `{"unknown": cause}` (the machine keeps its last good time) or a null list with its
  cause, never an empty list; a looked-at empty folder is an empty list. A view that cannot be decoded is written as
  unknown with the cause, and the probe still writes its file. Another machine's running job is not in this host's view.
- **steve-panel-names-the-games-right.** The panel and the strip say SteveDesktop, Steve1 and Steve2. No chip or line says
  only "Steve" for the machine.

## LIMITS

- **STEVE_STALE, 1800 s.** Danger: an old figure reads as current. Measured need: the probe writes each 180 s; ten missed probes.

## LIFE CYCLES (a move not listed here is a defect)

- **a run:** read the cache and the lane folder → draw (a source that is not readable: UNMEASURED and its cause) → write the
  page → if the cache is 180 s old, one ssh → write the cache.
