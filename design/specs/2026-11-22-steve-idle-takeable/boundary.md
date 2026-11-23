# BOUNDARY: the Steve lane idle while in-game checks wait for it, Design Version 0.1.0

Code: `ingame_testq` in `src/RimMandrake/rimflow/maturation_dispatch.py` (the `ingame_testq` block of the dispatch
reading) and `c_steve_takeable` in `src/RimMandrake/Utils/ops_watch.py` (the `steve.idle_with_takeable_min` point of
the steve family). Item: `RIMMANDRAKE_WATCH_STEVE_LANE_IDLE_WHILE_VISIT_CHECKS_WAIT`, written Sun 2026-11-22, 7:40 PM
PST. Each promise has a test of its name in `src/RimMandrake/Utils/selftest_steve_idle_takeable.py`.

## The danger the limits guard

- **The failure (measured 2026-11-22).** The SteveDesktop lane sat BRAKED on a filler day budget and then on filler
  work from 21:14Z to 02:45Z (5.5 h). Meanwhile 28 Pyrelands checks (visit 6) and 6 FlowWorks checks (visit 8) carried
  a testq block and could have run there. No reading fired: `queues.testq.stalled_min` reads only queued jobs and these
  checks were never queued; `steve.unowned_stall_min` reads only faults; `maturation.idle_owed_max_min` reads only the
  offline build; `seats.idle_with_work_min` reads only Claude seats.
- **The 30 min line.** The owner's brief for the Steve lane: "Steve lane stalled over 30 min" (the same line as
  `steve.unowned_stall_min`). The clock starts at the later of the visit's opening and the last finish of a lane job
  that was work: one not filler, or one on a waiting check's chain (the lane took that work, whatever its outcome). So
  a lane that just finished real work is not idle yet. A filler job on another mod does not stop the clock: filler is
  what the lane does when it has nothing to do (measured over 960 filler jobs: median 4.1 min, max 32.2 min).
- **The reading's age (30 min, `MATURATION_READING_MAX_AGE_S`).** The dispatch tick writes the block every 60 s; an
  older reading is a dead step and reads UNMEASURED, never 0.

## ACCEPTS (the only inputs this is built for)

- **the-dispatch-reading.** `reading.json` under `maturation_dispatch.sdir()`, written by the live tick, with its `at`.
- **the-testq-queue.** `TESTQ_QUEUE` with `running/`, `pending/` and `done/` records in the `testq.job/1` shape.
- **the-stage-records.** `design/concepts/*/version/stage_record.json` in the data clone (`RM_STREAMS_BENCH`).

## DOES NOT SURVIVE (not promised)

- **routing.** This reading says that work waits; it does not send the work. The routing (the visit's testq checks
  sent to the lane ahead of filler) is its own item: `RIMMANDRAKE_ROUTE_VISIT_TESTQ_CHECKS_AHEAD_OF_FILLER`.
- **the-arch-games.** An in-game visit owed with no Claude driver on ArchBig or ArchSmall is not read here (item
  `RIMMANDRAKE_WATCH_INGAME_VISIT_OWED_NO_DRIVER_UNSEEN`).
- **a-chain-that-ran-and-failed.** A check counts as drained only when each of its chains has a DONE record for the
  mod since the visit opened. An INVALID, INTERRUPTED or REFUSED run leaves it waiting.

## PROMISES (each one is owed a test of the same name)

- **the-dispatch-reading-names-each-waiting-check.** The tick's `ingame_testq` block names every in-game mod the tick
  read, with its visit, opening, owed word, owner hold, blocked state and the waiting checks with their chains: the
  checks the visit runs (`to_run`) that carry a testq block, less those with a row in the visit's own folder.
- **idle-or-filler-with-takeable-waiting-alarms.** With the lane idle, braked or on a filler job, and a takeable check
  waiting, the point reads MEASURED, the minutes since the clock start, state `waiting`, and the count per mod. Over 30
  min the rule raises its alarm.
- **nothing-takeable-is-quiet.** The point reads 0, state `quiet`, when no check waits: none carries a testq block, the
  mod is on the owner's hold, the visit is blocked or its exit is met, each chain ran DONE since the visit opened, or
  the only job for it is gated by the owner.
- **commissioned-or-takeable-work-is-busy.** The point reads 0, state `busy`, when the lane runs (or has ready in its
  queue) a job that is not filler, or any job on a waiting check's mod and chain.
- **could-not-look-is-unmeasured.** The point reads UNMEASURED when the dispatch reading is missing, stale or has no
  block, when the owner's hold could not be read, when a queue directory cannot be read, or when an in-game mod is
  missing from the reading and no other waiting check is known.
- **the-rule-alarms-to-the-conductor-log.** `ops_watch_rules.json` holds the target on `steve.idle_with_takeable_min`:
  over 30, an alarm with a fixed name, the Conductor log, and a why that names the danger and the 5.5 h.

Later lists beside this page: `polish.md`.
