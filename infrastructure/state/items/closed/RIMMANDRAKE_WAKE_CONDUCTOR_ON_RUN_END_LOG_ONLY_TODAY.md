## spec
When a detached run launched for the Conductor seat ends (any terminal state: success, failure, timeout, killed), the
live Conductor window learns of it within a minute without the owner typing and without a hand-armed Monitor: the wake
path the Dispatcher already uses for a seat (seat_restart / the Stop or prompt hook that injects pending lines), or a
standing watcher the window arms at wake from its role file. The full result path travels with it, not a 300-character
cut. If no window is alive, nothing is lost: the line stays in the Conductor log and the run's follow-up is an `owed`
ticket (RIMMANDRAKE_FILE_OWED_WHERE_RUNS_PARK_FOR_THE_CONDUCTOR). Prefer extending what exists over a new daemon.
No ceremony: this protects against one measured loss, a finished result sitting unread while a window is alive and he
is quiet (Gimme Some Slack blind cycle 3, 2026-11-15 4:47 PM PST, unread until the next window's wake).

## verify
Acceptance test: `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/rimflow/selftest_detached_wake.py`
exits 0. The builder writes that selftest first: a fake ended run for seat CONDUCTOR with a live-window marker must
produce exactly one pending wake line carrying the run id, terminal state and full result path; with no live window it
must produce none and leave the log line. On the filing base the selftest file does not exist (watched 2026-11-15:
the path is absent, so the command cannot pass). Live half, UNRUN: launch a 30-second detached run and see the line
arrive in the window with nobody typing.
