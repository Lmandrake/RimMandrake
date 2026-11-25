# BOUNDARY: every stop of the SteveDesktop lane names its end, Design Version 0.1.0

Code: `src/RimMandrake/Utils/testq/lane_stop.py`, and its callers in `testq.py` (`finish`, `admit`, `steve_lanes`,
`fill_plan`, `cmd_pause`, the tick's `LS.step`), `steward.py` (`lane_state`) and `ingest.py` (`ingest_one`).
Item: `RIMMANDRAKE_CLEAN_STEVEDESKTOP_TICKETS_FIX_THE_FORM_NOT_EACH_COMPLAINT`. Forms page:
`design/specs/2026-11-23-stevedesktop-work-to-code/forms.md`. Each promise has a test of its name in
`src/RimMandrake/Utils/testq/selftest_lane_stop.py`.

A **stop** is one game's stop after two equal endings. A **pause** is the machine's pause (`paused.json`) or one game's
pause. An **equal ending** is the same outcome, the same cause and the same note, with paths and numbers taken out.

## ACCEPTS

- A finished job's result (`testq.result/1`) and the host that ran it.
- `testq.py pause --reason R` with `--hours H`, with `--until-unit UNIT`, or with neither.

## DOES NOT SURVIVE

- A refusal whose note differs each time in words: two such endings are not equal, so nothing stops.
- A unit name that never ran on Archmagi: systemd reads it as not active, so the pause ends at the next tick.

## PROMISES

- **two-equal-refusals-stop-that-game.** Two jobs in a row on one game that end equally and not DONE stop that game: it
  admits nothing, the other game goes on.
- **a-done-job-or-a-different-ending-counts-from-one.** A DONE job, or a different ending, between them: no stop.
- **one-mods-harness-fault-does-not-stop-the-game.** Two equal INVALID/HARNESS endings of one mod are the mod's
  (`repeat_guard.py` holds its chain); the game goes on.
- **a-cancelled-or-selection-refusal-never-stops.** A cancelled job, GUARD_HELD, BLOCKED_SELECTION, SCHEMA and CANARY never count.
- **a-stop-retries-by-itself.** After the stop's end one job is admitted; the same ending again stops the game again at
  once; a DONE clears the stop.
- **one-ticket-for-one-cause.** The job that made the stop carries its cause to ingest, which files one
  HARNESS_REPAIR_CAUSE item for it and notes later ones on that item.
- **every-pause-has-an-end.** A hand pause with no end gets the default end and says so; an auto pause ends by itself for
  a retry; the tick lifts each pause at its end and logs why.
- **a-unit-pause-waits-for-its-unit.** `--until-unit` keeps the pause while the unit runs. systemd unreadable: the pause
  stays, and the log says that it could not look.
- **a-hand-pause-is-extended-not-refused.** A second hand pause replaces the end of the first.
- **the-steward-reads-a-stop-as-a-pause.** Every live game stopped reads PAUSED until the end, and is a fault only after
  `ESCALATE_S`.
- **a-fill-stop-names-its-end.** A hand-written `fill.stop` with an `until: <ISO time>` line reads PAUSED and is a
  fault only at that time. With no readable `until` line, it is a fault 60 min after its mtime (`MANUAL_PAUSE_S`).

## LIMITS

- `RETRY_S` 30 min. Danger: a stop that never ends (one pause with no end lasted 49 h, 2026-11-15). Evidence for the
  other side: 47 equal refusals in 11 h on 2026-11-23, one each 14 min. A retry costs one refused job.
- `DEFAULT_PAUSE_H` 2 h, for a hand pause that names no end. Danger: the same 49 h pause.
- `ESCALATE_S` 60 min, then the steward files. Danger: a broken game that only retries for days.
