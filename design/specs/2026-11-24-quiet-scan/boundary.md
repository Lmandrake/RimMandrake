# BOUNDARY: the standing scan of quiet files (quiet_scan.py), Design Version 0.1.0

Code: `src/RimMandrake/rimflow/quiet_scan.py`, `src/RimMandrake/rimflow/quiet_scan.json`,
`src/RimMandrake/rimflow/roles/quiet_scan.md`, `src/RimMandrake/Utils/systemd/rm-quiet-scan.service`,
`src/RimMandrake/Utils/systemd/rm-quiet-scan.timer`, and `detached_helper.run_wakes`.
Item: `RIMMANDRAKE_BUILD_STANDING_SCAN_OF_QUIET_FILES_ON_SONNET`, the owner's card of 2026-11-19 5:54 PM PST
(`design/RimMandrake/standing_rulings.md` §Code is clean when its promises are tested). Each promise has a test of its
name in `src/RimMandrake/rimflow/selftest_quiet_scan.py`. `acceptance/quiet_scan_running_accept.py` reads the live job.

## ACCEPTS (the only inputs this is built for)

- **a-tracked-code-file.** A `.cs`, `.xml` or `.py` file under `src/` that git tracks. Mod content is a file whose
  `src/<tier>/<Mod>/` folder holds `About/About.xml`.
- **one-scan-run-at-a-time.** The scan run is a detached run (`detached_helper.py launch`, sonnet) on the closed item
  `RIMMANDRAKE_RESTART_QUIET_FILE_SCAN_3580_NEVER_READ`, so it opens and closes no item of its own.
- **the-maturation-reading.** `<state>/maturation/reading.json`, written by the mod pipeline's tick about each minute,
  and the detached-run records. They say if a mod step is live.

## DOES NOT SURVIVE (not promised)

- **a-mod-step-that-starts-inside-a-read.** The scan run asks between files, not inside one. A file that it reads when a
  mod step starts is finished first.
- **two-scan-timers.** The tick holds a file lock; a tick with another state directory is not seen.
- **an-outcome-the-run-misjudged.** The program checks that the outcome is recorded, not that the read was good.

## PROMISES (each one is owed a test of the same name)

- **a-file-changed-in-the-last-seven-days-is-never-picked.** The last 7 days of commits on origin/main decide it. When git
  cannot answer, nothing is picked.
- **mod-content-first.** The mods' C# first, then the mods' XML, then the rest. A test program inside a mod is in the rest, because
  the game never loads it. In each group a file that was never read comes before a file whose recorded read is out of
  date.
- **a-file-that-needs-no-read-is-not-picked.** A READ-CLEAN file (its record matches its bytes), a FLAGGED file, a file
  with an outcome on these bytes, and a file of a mod that is held or off are never picked. Flags or holds that cannot
  be read pick nothing.
- **a-picked-file-ends-clean-flagged-or-with-a-noted-reason.** `end` takes `clean` only when the record says so and
  has landed, `flagged` only when the flag has landed, and `noted` only with a reason. A refusal names its repair. A
  file that a run left with no outcome is noted with that run's end.
- **a-system-death-releases-the-file.** A run that was killed or never started notes nothing: its file is picked
  again later, after `system_wait_s` and behind every file picked fewer times, so one file that kills its runs never
  holds the queue.
- **the-job-yields-to-a-live-mod-step.** While a mod step is live or is about to start, `tick` launches nothing and `next`
  answers YIELD. A reading that is absent or older than `reading_max_age_s` is `blind`: nothing launches.
- **the-gates-launch-nothing.** Disabled, `pipe off` (all, `family:quiet_scan`, `family:detached`), the pipeline's pause,
  an account hold, a full clone pool and a live scan run each read their own decision and launch nothing. `next` answers YIELD
  under the first three. `--hand` skips only the mod-step gate.
- **a-run-that-ends-no-file-stops-the-scan.** A run that ended on its merits with no outcome for any file stops the scan and says
  it once to the Conductor. `clear` starts it again.
- **the-run-is-sonnet-and-knows-the-method.** The launch is sonnet, and its brief names the review method, the fresh reader
  and the three outcomes.
- **a-scan-run-does-not-wake-the-conductor.** The end of a scan run writes its record and log line, and posts no wake. Every other
  run of the Conductor's seat still wakes the window.
- **a-dry-tick-writes-nothing.** A tick without `--apply` writes no state and launches nothing.
- **each-limit-names-its-danger.** Each number in `quiet_scan.json` has a `_<name>_doc`.

Later lists beside this page: `polish.md` (none yet).
