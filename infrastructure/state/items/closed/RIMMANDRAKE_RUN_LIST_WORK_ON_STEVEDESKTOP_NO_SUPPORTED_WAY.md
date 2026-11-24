# RIMMANDRAKE_RUN_LIST_WORK_ON_STEVEDESKTOP_NO_SUPPORTED_WAY

No supported way runs list work on SteveDesktop's Claude sessions. Build one, so its idle capacity works open non-mod tickets.

The owner, 2026-11-24, 8:12 AM PST: *"I'd like to have SteveDesktop working 100% on closing out non-mod work today please."*

## Finding

Measured 2026-11-24, 8:17 to 8:30 AM PST:

- SteveDesktop has 18 cores, 61 GB free memory and 878 GB free disk. Its load was 0.9 with both games running a lane job.
- Claude Code 2.1.331 is installed there. `claude-account status` read live account lukas, with steven and system also
  enrolled; each has about 28 days left. `seat-runner` stood idle at an empty prompt. `seat-server` was connected.
- `detached_helper.py`, `list_dispatch.py`, `role_launch.py` and `account_pick.py` hold no ssh and no host. A detached run
  starts only as a systemd user unit on this machine. `./pipe`, the run records and the wakes read this machine's units.
- `seat-runner` stands in `~/rm/runner`, the clone that the test lane pins. A session that writes there pauses the lane
  (`STEVE_RUNNER_CLONE_ENFORCE_NO_LLM_WRITES`). So typing a brief into that window is not a way.
- `infrastructure/stevedesktop/RUNBOOK.md` still says the machine is "a token-free runner, not a second agent farm". The
  owner's order above changes that. Correct the RUNBOOK in the same change.
- The live account on SteveDesktop is the machine's own. The Dispatcher picks for Archmagi. A run there must use the
  account that the Dispatcher picks, and must not move the account order or a leave line.

## spec

- `run_host.py`: `plan` and `stop_argv`, with the contract at the head of the acceptance script.
- `detached_helper.py launch --host SteveDesktop`: the run is a systemd user unit on SteveDesktop, in its own clone under
  `~/rm/list/`, never `~/rm/runner` or `~/rm/runner_b`. Its record on Archmagi carries the host.
- Status, stop, spend stop, finish, wake and clone return work for a run on that host. A host that cannot be read is
  COULD NOT LOOK, never "ended".
- `list_dispatch.py` sends a list item there when `max_live` on Archmagi is full. A host has its own `max_live`.
- The run on SteveDesktop lands with `./publish` through its write deploy key (`github-rimmandrake-write`).
- Write the boundary page first.

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/list_run_on_steve_accept.py` prints `12/12`, exit 0. Seen
failing on the base 2026-11-24, 8:27 AM PST: `0/12`, exit 1.

Then one live run: one open non-mod ticket is worked on SteveDesktop, its record on Archmagi reads the host and the end, and
`./pipe stop` of a second run ends its unit there.

## refs

file: src/RimMandrake/rimflow/detached_helper.py
file: src/RimMandrake/rimflow/list_dispatch.py
file: infrastructure/stevedesktop/RUNBOOK.md
