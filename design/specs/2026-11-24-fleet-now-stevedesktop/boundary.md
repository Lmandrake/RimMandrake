# BOUNDARY: the SteveDesktop reading for the fleet page, Design Version 0.2.0

Code: `src/RimMandrake/Utils/steve_reading.py` (all of it), run by `rm-steve-reading.timer` each minute.
It writes `D:\ClaudeWork\rimmandrake\conductor\running_steve.json`. The reader is Augur's fleet page,
`D:\ClaudeWork\augur\dashboard\FLEET_NOW.md` (config `remote_hosts` in `D:\ClaudeWork\augur\config\dashboard.json`).
Items: `RIMMANDRAKE_RESTORE_STEVEDESKTOP_ON_FLEET_NOW_OLD_PAGE_HAD_IT`, and
`RIMMANDRAKE_REMOVE_RELENTLESS_NOW_PAGE_CONSOLIDATE_MONITORS_HE_SAID_SLEEK`, which removed the page that once drew this
reading. The owner, 2026-11-24 about 1:30 PM PST: *"FLEET_NOW.md should also show Steve Desktop. The old Relentless one
did. We need it back. Machine stats, the jobs its running, just like Archmagi supports. Use GPT."* And 2026-11-24:
*"remove RELENTLESS_NOW.md as distraction, keep only the part that makes SteveDesktop reading."* Each promise has a test
of its name in `src/RimMandrake/Utils/selftest_steve_reading.py`.

## ACCEPTS (the only inputs this is built for)

- **the-probe.** One ssh to SteveDesktop's WSL, at most every `PROBE_EVERY` (180 s). It reads the machine figures, the
  game and driver readings and the running services.
- **the-test-lane-folder.** `testq/running/` and `testq/pending/` on Archmagi, written by the lane.

## DOES NOT SURVIVE (not promised)

- **a-runner-clone-that-is-gone.** The game and driver readings come from SteveDesktop's `~/rm/runner` clone. Without it
  they are unknown with the cause. The machine figures do not need it.
- **the-steward-words.** The steward's state, the jobs done in 24 h and its age are not in this file. The `steve` family
  of `D:\ClaudeWork\rimmandrake\ops_watch\digest.md` holds them.

## PROMISES (each one is owed a test of the same name)

- **steve-games-up-and-driver.** Steve1 and Steve2 each read up or down, who drives it and for what, from SteveDesktop's
  own process list and driver locks in the one ssh probe. A job id in a lock's purpose is shown with the job's mod and
  what it runs, from `testq/running/`.
- **steve-jobs-by-name.** The view names each job of this host that runs or is queued: its mod, its purpose, its chains,
  its place and its start time. Another machine's running job is not in this host's view.
- **steve-services-in-view.** `services` lists each running service of SteveDesktop that is not a lane job or dbus; a list
  that cannot be read is null and `services_why` names the cause. A list that was read and is empty is `[]`.
- **steve-claude-runs-by-unit-and-item.** `claude_runs` lists each running `rm-detached-*` unit of SteveDesktop with the
  item, seat and model from its claude argv and its launch time from the unit name; a part the line lacks is null. A
  list that was read with no such unit is `{"observed_at", "rows": []}`; an unread list is `{"unknown": cause}`.
- **steve-every-reading-has-its-time.** The write, the machine figures, the games and the jobs each carry the time of
  their reading.
- **steve-unread-is-unknown-with-cause.** A missing, broken or old source is `{"unknown": cause}`, a null list with its
  cause, or a figure left out and named in `issues`. It is never 0, down, free or an empty list. A machine reading older
  than `STEVE_STALE` is unknown with the failure and the last good time. A failed ssh keeps the last good numbers in
  the file and turns its route off; the next good ssh clears the failure.
- **steve-one-ssh-per-probe.** No second ssh inside `PROBE_EVERY`; the machine, game, lock and service readings share it.
- **steve-view-for-augur.** Each probe writes the decoded `view` block (schema `augur.remote_host/1`). A view that cannot
  be decoded is written as unknown with the cause, and the probe still writes its file.
- **steve-check-tells-old-unread-and-decoded-apart.** `--check` prints the file's age and its verdict: 0 for fresh and
  decoded, 1 for absent, unreadable, old, or a machine that is unknown, each with its own words.

## LIMITS

- **STEVE_STALE, 1800 s.** Danger: an old figure reads as current. Measured need: the probe writes each 180 s; ten missed probes.

## LIFE CYCLES (a move not listed here is a defect)

- **a run:** read the file → inside `PROBE_EVERY` of the last probe: stop → one ssh → decode the view → write the file whole.
