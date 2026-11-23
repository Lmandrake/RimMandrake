# BOUNDARY: the Steve lane idle while in-game checks wait for it, Design Version 0.1.0

Code: `ingame_testq` in `src/RimMandrake/rimflow/maturation_dispatch.py` (the `ingame_testq` block of the dispatch
reading) and `c_steve_takeable` in `src/RimMandrake/Utils/ops_watch.py` (the `steve.idle_with_takeable_min` point of
the steve family). Item: `RIMMANDRAKE_WATCH_STEVE_LANE_IDLE_WHILE_VISIT_CHECKS_WAIT`, written Sun 2026-11-22, 7:40 PM
PST. Each promise has a test of its name in `src/RimMandrake/Utils/selftest_steve_idle_takeable.py`.

The routing (section ROUTING PROMISES below): `src/RimMandrake/Utils/testq/visit_feed.py` (`testq.visit_feed_step`,
the first step of every testq tick), the advancing-first order of `coverage.fill_order`, and `testq.site_stage_step`
with `sync_test_mods.site_saves`. Items: `RIMMANDRAKE_ROUTE_VISIT_TESTQ_CHECKS_AHEAD_OF_FILLER` and
`RIMMANDRAKE_ROUTE_PYRE_TESTQ_OFF_STEVE_NO_SITE_THERE`, written Sun 2026-11-22, 11 PM PST. Each routing promise has a
test of its name in `src/RimMandrake/Utils/selftest_steve_visit_feed.py`; the site copy's own cases are in
`infrastructure/stevedesktop/selftest_sync_test_mods.py`.

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

- **routing.** This reading says that work waits; it does not send the work. The visit feed sends it (ROUTING
  PROMISES below). The feed drains a check only on a PASS or FAIL row; this reading drains it on any DONE run. So a DONE
  run that read only UNMEASURED rows reads `quiet` here while the feed sends the check again, at most twice more.
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

## ROUTING PROMISES (each one is owed a test of the same name in selftest_steve_visit_feed.py)

- **a-waiting-check-is-queued-ahead-of-filler.** With a takeable check waiting and the lane idle or on a filler job on
  another mod, one tick's feed step queues ONE ready job on the SteveDesktop lane for that mod and chain. The job is
  requested by `BENCH.visit` at priority 40, above the filler's 20. Then `c_steve_takeable` reads `busy` and
  `fill_plan` reads `busy`, so no filler job is queued. While a visit job is pending or running, the step reads `busy`
  and queues nothing.
- **a-visit-opening-with-an-offset-reads.** A visit opening in local time with its offset (the form maturation writes)
  reads. An opening that cannot be read is named (`unmeasured`), never `quiet`.
- **the-owners-hold-and-gate-still-stop-a-check.** A mod on his hold (the reading's flag, or the live hold list at
  submit), a blocked visit, a visit whose exit is met, and a chain whose job waits on his gate are never sent.
- **nothing-waits-nothing-is-sent.** A check is drained when each of its chains ran DONE for the mod since the visit
  opened, with a PASS or FAIL row. A run before the opening drains nothing. A chain that measured nothing twice since
  the opening (not DONE, or DONE with only UNMEASURED rows) is named in `spent` and not sent again. `fill.stop` and a
  pause stop the feed.
- **a-lane-refusal-does-not-spend-a-check.** A run the lane refused before the chain ran (REFUSED for a cause in
  `testq.ARCH_BOUNCE` or SYNC) is not one of those failures: two of them still leave the chain sent. A chain refused so
  within the last 10 min (`BOUNCE_BACKOFF_S`) is held back, named in `backoff`; with nothing else waiting the step reads
  `backoff`, never `quiet`. A refusal for a cause about the job (PREFLIGHT) still counts.
- **could-not-look-sends-nothing.** A missing, stale (over 30 min) or blockless dispatch reading sends nothing and
  says why. A queue that is not the live one reads no dispatch reading unless one is named for it
  (`RM_MATURATION_DISPATCH_DIR`).
- **the-feed-runs-after-reconcile-before-admission.** In each tick the feed step runs after reconcile and the outbox
  (so a visit job that just finished reads done, not running) and before admission (so the tick admits what it
  queued). With SteveDesktop unreachable it still runs, and the site copy does not.
- **mods-take-turns.** The earliest-opened visit goes first. After that, the mod whose last visit job was submitted
  longest ago goes first.
- **filler-prefers-advancing-mods.** The filler walks the advancing mods (`maturation_dispatch.json` `advancing`) first,
  rotated among themselves, then every other mod.
- **site-saves-ship-when-the-registry-changes.** The tick copies every registered test-site save
  (`test_site_saves.json`) that SteveDesktop lacks, or holds in another version (sha256), when the registry changed
  since the last good copy. A failed copy is tried again after 30 min (`SITE_RETRY_S`), never every tick.

## ROUTING LIMITS

- `PRIORITY` 40: above the filler (20), under a hand commission (50).
- `FAILS_TO_STOP` 2: the danger is a lane spun by a chain it cannot run. The evidence is the filler brake's two
  not-DONE runs in a row, and 20 h of lane lost on 2026-10-25.
- `BOUNCE_BACKOFF_S` 600: the danger is a check resent into the same refusal every tick. It is longer than the 1-4 min
  one refusal cycle took on Steve2 on 2026-11-23 (done records) and under the 30 min line above.
- `READING_MAX_AGE_S` 1800: the same line as `MATURATION_READING_MAX_AGE_S` above.
- `SITE_RETRY_S` 1800: the danger is up to ~100 MB of saves sent over ssh every 60 s while a cause persists.
- Chains per visit job: the filler's `TESTQ_FILL_CHAINS` (4). It is not a new limit.

Later lists beside this page: `polish.md`.
