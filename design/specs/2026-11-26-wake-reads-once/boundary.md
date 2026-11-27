# BOUNDARY: a Conductor window's first turn prints the log tail, the owed list and the last reply once

Code: `src/RimMandrake/rimflow/seat_restart.py` (`cmd_wake`, `cmd_last_reply`, `_wake_log_tail`, `READ_ONCE`) and
`src/RimMandrake/Utils/handoff.py` (`wake`, `show_last_reply`, `owed_shown`).
Item: `RIMMANDRAKE_SLIM_RUN_END_WAKES_WINDOW_HIT_400K_IN_TWO_HOURS`. Tests: `src/RimMandrake/rimflow/selftest_wake_reads_once.py`.
The once-per-window rule of his words is on `design/specs/2026-11-23-wake-his-words/boundary.md`; this page uses the same
stamp (`wake_words.Wake.repeat`).

READING: the first turn of the Conductor window c95f9ab4 (2026-11-25 6:38 PM PST) printed the 12,855-character log tail
twice, the owed list twice (12,020 characters the second time), and the last reply and the top lines twice. With the
log tail of 2026-11-26 (18,563 characters) and an owed list of that size, the first-turn reads take 66,238 characters on
the parent code and 33,761 on this code `[measured 2026-11-26]`.

## ACCEPTS

- **a-conductor-window.** A window whose seat is a `conductor` kind in the restart schedule, with a session id.

## DOES NOT SURVIVE

- **a-window-with-no-session.** With no session id the stamp is not written, so a second read prints all again.
- **a-frozen-prompt.** A fleet prompt frozen in a Windows Terminal profile before this code still asks for the log tail.

## PROMISES

- **a-restart-wake-then-handoff-prints-once.** After `seat_restart.py wake`, `handoff.py --wake`'s last-reply read in the
  same window prints one line that names `--again` in place of the last reply, the top lines, his words, the owed list
  and the log tail. `--again` prints them whole.
- **handoff-first-then-restart-wake-prints-once.** After the last-reply read, `seat_restart.py wake` in the same window
  prints that line in their place, and the rest of its wake.
- **a-fleet-launch-reads-everything-once.** In a window no restart made, the last-reply read prints the last reply, the
  owed list and the log tail.
- **handoff-prints-no-second-owed.** `handoff.py --wake` prints its own owed list only when the last-reply read printed
  neither the owed list nor the line that says it was printed.
