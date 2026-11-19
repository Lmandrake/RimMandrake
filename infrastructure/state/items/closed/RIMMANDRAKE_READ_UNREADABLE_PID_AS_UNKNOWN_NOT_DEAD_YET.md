## spec
seat_restart._proc_stat (55722bc0f9) falls back to `ps -o state= -o lstart=` whenever /proc/<pid>/stat cannot be
opened. On Linux that re-reads a pid's birth in epoch seconds against a start saved in clock ticks, so proc_alive reads
a running process as dead; and with ps also failing (timeout) it returns None, which proc_alive spells dead too.
Measured 2026-11-18 with a live child: ticks 64169956 -> 1795026013, alive False; ps timeout -> None, alive False. The
same verdict held before 55722bc0f9 (None on any OSError), so this is a pre-existing collapse the fallback did not
close, not a Linux regression. Callers that act on "dead": execute() (kill), old_alive()/intile_claim (relaunch
beside a living window), reconciliation. Also: selftest_seat_restart R4's Mac branch prints "the reuse refusal was
measured" while kill_pid returns the platform refusal before checking the start. Found by the Codex review of
55722bc0f9 (D:\ClaudeWork\rimmandrake\conductor\remote_landings_20261118\codex\55722bc0f9.review.md).

## verify
python3 src/RimMandrake/rimflow/acceptance/seat_restart_unreadable_proc_accept.py   # exit 0 (Linux)
Watched failing on c32e228e91: rc 1, 2 of 2 "proc_alive(live child) -> False". Expected: 1 pass.

## criteria
- A live pid whose reading fails is never answered dead; Linux readings keep one unit; R4 says only what it measured.
