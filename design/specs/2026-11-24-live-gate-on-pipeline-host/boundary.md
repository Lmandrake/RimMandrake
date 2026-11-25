# BOUNDARY: the close gate's live check on the pipeline host, Design Version 0.1.0

Code: `check_where_run` and `pipeline_host_answers` in `src/RimMandrake/rimflow/live_line.py`, and the two close gates
in `src/RimMandrake/rimflow/cli.py` (`_live_gate`, `_check_close_live`) that call it. Item:
`RESTART_JOIN_BUILD_EVERY_GOODBYE_ENDS` (a SteveDesktop helper's close of an Archmagi promise was refused: rm-metronome.timer
"not-found" on SteveDesktop, 2026-11-24). This page covers these two functions only, not the rest of live_line.py. Each
promise has a test of its name in `src/RimMandrake/rimflow/selftest_live_where_run.py`. No state is kept between calls.

## ACCEPTS

- A live line (`live_line.parse`), a `not_before` epoch, and a runner with the shape of `subprocess.run`.
- The pipeline host is the machine whose systemd has `rm-deadman.timer` enabled: the deadman is the judge that rechecks
  every promise, so where it runs, the local reading is the truth. Its ssh target is `RIMFLOW_LIVE_SSH` (default
  `mandrake@archmagi-wsl`, the pattern of `testq/retest.py`; empty means stay local). Its clone is `RIMFLOW_LIVE_CLONE`
  (default `~/rm/dispatch`, the deadman's WorkingDirectory).

## DOES NOT SURVIVE

- A pipeline host whose `~/rm/dispatch` is behind origin: it judges with its own `live_line.py`, as the deadman does.
- An ssh that hangs past its timeout reads as COULD NOT LOOK, and the close is refused, never passed.

## PROMISES

- **local-holds-first.** A line that holds on this machine holds; no remote is asked.
- **pipeline-host-is-final.** On the pipeline host (local `rm-deadman.timer` enabled), a local failure is the answer;
  no remote is asked.
- **off-host-asks-the-host.** Off the pipeline host, a local failure is checked again on the pipeline host, read-only
  (`python3 -B`, the host's own `live_line.check`), and the host's answer is the answer; a NotYet stays a NotYet.
- **blind-never-passes.** An ssh that fails, times out or prints no verdict returns a reason naming the host; it never
  returns None.
- **stay-local-when-empty.** `RIMFLOW_LIVE_SSH` set empty keeps the local answer.
