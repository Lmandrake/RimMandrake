# BOUNDARY: the Dispatcher files no owed item by itself, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/dispatcher.py` (`execute`, the acts after the notes), `src/RimMandrake/rimflow/owed.py`
(its command line), `src/RimMandrake/rimflow/seat_restart.py` (the kill path, `execute` on a `restart_kill`).
Item: `RIMMANDRAKE_RETIRE_OR_REPAIR_OWED_SOURCES_KILLED_EVERY_TICK`, written 2026-11-23. Each promise has a test of its
name in `src/RimMandrake/rimflow/selftest_owed_sources.py`.

What was retired, and why. The Dispatcher step `owed_sources` ran `owed.py sync-sources` every 300 s in a child that the
step killed at 6 to 10 s. The child asked `maturation.next_step` of every versioned mod, held mods included. Measured 2026-11-23
at load 7.5: 127 s for 10 mods, of which FlowWorks 116 s (the in-game exit tests of one mod: 4379 subprocess runs) and
GimmeSomeSlack 9 s. The kill came on 210 of 210 passes on 2026-11-22 UTC and on 175 of 185 on 2026-11-23. The step filed
9 items in all, the last on 2026-11-20; all 9 are closed. The 10 s limit guarded the Dispatcher beat (the first live
pass cut the helper budget). The limit went with the step.

Where each thing that the step did is done now:

| what the step filed | its home now |
|---|---|
| a mod after three blind cycles (the Conductor decides) | the tick's decision `cycle_limit`, class paused: the `paused` list of `reading.json`, the alarm `OPS_MATURATION_MOD_PAUSED`, the mod's card on MATURATION_NOW, and "each mod now" in the Conductor's wake |
| a card for the owner | `maturation_autonomy.post_cards`: the card text in the Conductor log, once per card |
| a detached run that ended success with its item open | `left_open_continue.py` continues it once, then alarms; `detached_helper.owed_lines` is a line under Needs Conductor on MATURATION_NOW while the item stays open |
| a promise in the last reply of a Conductor window that was killed for its size (the queue `untracked_promises` and `seat_restart.py`'s writer of it) | the next window's wake prints that reply whole (`seat_restart.py wake`, the old window's LAST REPLY). The queue held 2 rows ever, both false, and none was filed |
| a mod that passed (whether to open the next version) | nobody needs an item: the tick reads it as rested, and the mod's Next line on MATURATION_NOW says it |

Kept: the `owed` view, banner, wake lines, pointer check and discharge rule of `owed.py`, and the per-prompt note of
`promise_scan.py` (`design/specs/2026-11-20-owner-words-not-refused/boundary.md`).

## ACCEPTS

- **an-old-state-file.** A Dispatcher `state.json` that still holds `owed_sources_at`: nothing reads it.
- **an-old-schedule.** A schedule that still holds `owed_sources_every_s`: nothing reads it.

## DOES NOT SURVIVE

- **a-status-page-that-nobody-builds.** When MATURATION_NOW is not built, a run left open is said only by
  `left_open_continue.py` and the Conductor log.

## PROMISES

- **no-step-in-the-dispatcher.** An applied Dispatcher pass starts no `owed.py` child and writes no `owed_sources` journal
  line, with the old schedule key present or absent. `dispatcher_schedule.json` does not hold the key. Tested by
  `t_no_step_in_the_dispatcher`.
- **old-command-is-refused.** `owed.py sync-sources` (a call from an older clone or a hand) exits 2 and names the
  commands that exist. It never prints a view and exits 0. Tested by `t_old_command_is_refused`.
- **a-size-kill-writes-no-queue.** A backstop kill of a Conductor window kills the window and writes no promise file; no
  code file under `src` or `.claude` names the old queue. Tested by `t_a_size_kill_writes_no_queue`.
- **cycle-limit-is-paused.** A row with the decision `cycle_limit` is class paused and is in the reading's `paused` list
  by its mod's name. Tested by `t_cycle_limit_is_paused`.
- **his-card-is-in-the-log.** A row of class owner with a card is written to the Conductor log once. Tested by
  `t_his_card_is_in_the_log`.
- **run-left-open-is-a-need.** A finished run whose record carries `owed_close` and whose item is open is a line under
  Needs Conductor; when the item closes, the line goes. Tested by `t_run_left_open_is_a_need`.

## LIFE CYCLES

- **a Dispatcher pass:** decide, act, note, publish. No filing of owed items.
