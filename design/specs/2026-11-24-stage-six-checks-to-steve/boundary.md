# BOUNDARY: a Stage 6 check goes to a Steve game by its own script, Design Version 0.1.0

Code: `src/RimMandrake/Utils/testq/stage6_checks.py` (the routes and the runner), `stage6_site.py` (the site, Windows
python), `proof_build.py`, `visit_rows.py`, and the parts that name them in `testq_blocks.py`, `schema.py`, `testq.py`,
`visit_feed.py`, `ingest.py` and `infrastructure/stevedesktop/worker.py`.
Items: `RIMMANDRAKE_SEND_STAGE_SIX_CHECKS_TO_STEVE_GAMES_NONE_CARRY_A_BLOCK`,
`RIMMANDRAKE_COUNT_LANE_RESULTS_WHERE_VISITS_DECIDE`, `RIMMANDRAKE_ROUTE_TESTQ_PROOF_BUILD_JOBS_TO_STEVE`.
Each promise has a test of its name in `src/RimMandrake/Utils/testq/selftest_stage6_checks.py`.

## The failure this guards

- **Measured 2026-11-24, 1:29 AM PST.** 0 of 206 Gimme Some Slack checks and 0 of 56 Explosive Knockback checks, and 10
  of 30 FlowWorks checks, carried a testq block. The block rule knew one route only: a modcheck chain. These checks are
  scripts. Both Steve games reran guards while four mods waited for an Archmagi game.

## ACCEPTS (the only inputs this is built for)

- **the-test-table.** A stage-6 entry of `version/test_table.json` with `kind`, `file`, `entry`, `command`, `tier`.
- **a-checks-job.** `selector {"checks": [ids]}`, profile `tier:<name>`, lane `stevedesktop`, `mod` the mod's folder.
- **the-worker-result.** A `testq.result/1` whose `checks` block holds the identity and each check's site.

## DOES NOT SURVIVE (not promised)

- **the-host-lacks-a-mod.** Whether SteveDesktop holds each mod of a tier is learned at the load. The job then reads
  INVALID/LOAD, which is could not look (`RIMMANDRAKE_ASK_LANE_IN_ONE_LINE_AFTER_HOST_FACTS` reads it before).
- **the-idle-alarm.** `steve.idle_with_takeable_min` reads chain checks only.
- **a-chain-job-counting.** A modcheck chain job runs on modcheck's own composed list, which is no tier's list, so its
  visit row reads COULD NOT LOOK and never replaces a row that counts.

## PROMISES (each one is owed a test of the same name)

- **each-check-is-placed-once.** Each stage-6 check is one of: takeable, not the lane's (his full list, a look, a check
  bound to an Archmagi game, a paused raid), or could not look. The three counts sum to the checks. Each check that is
  not takeable names its cause.
- **the-four-mods-are-takeable.** On the committed tables, each of FlowWorks, Pyrelands, Explosive Knockback and Gimme
  Some Slack has more than zero takeable checks, and the count equals the number of committed blocks.
- **a-full-list-check-is-never-sent.** A `live_full` check, or one with `why_full_list`, gets no block.
- **no-entry-point-is-could-not-look.** A check whose entry is absent, whose script is not on disk, or whose script has
  no program verdict, reads could not look with that cause.
- **a-paused-raid-is-never-sent.** A scene that carries `stages_raid` gets no block while raid tests are paused.
- **the-verdict-is-the-checks-own-row.** Each check of a run is a row of its own name. Only the script's own PASS or
  FAIL is a verdict. A crash, a timeout, no output, INVALID, ERROR, a site that was not verified, and a row that is
  missing read UNMEASURED with the cause.
- **one-run-serves-all-its-checks.** Checks that one command decides run that command once.
- **the-job-form-is-checked.** A checks job without a tier, on another lane, or with a second selector key is refused.
- **the-worker-publishes-each-check.** The worker runs the runner on the exact tier, publishes one row per check, and
  publishes INVALID/LOAD with every row UNMEASURED when the load is not the tier.
- **the-feed-sends-one-tier-at-a-time.** The visit feed queues one job whose checks share one tier and one build. A
  check that ran since the visit opened with PASS or FAIL is not sent again. A check that could not look waits and
  doubles its wait.
- **a-visit-row-is-written-once.** A finished visit job adds one row per check to the open visit's `rows.jsonl`, once,
  with the game's name, the job and the build identity. A visit that moved on or closed gets no row.
- **a-lane-row-never-opens-a-visit.** A visit folder that holds only the lane's rows reads as no visit: its live driver
  is still owed (`maturation.lane_rows_only`). Measured 2026-11-24: 3 rows of Steve1 in FlowWorks `visit_10` read as a
  visit that ended without its exit block, so the Dispatch step paused FlowWorks. A row of another writer, a torn row or
  another file beside them is a record, as before.
- **could-not-look-never-replaces-a-row.** An UNMEASURED row, a job that did not end DONE, and a row with no readable
  identity read COULD NOT LOOK. So does a row whose mod list is not its tier's list on an Archmagi install: the feed then
  sends the check again after its wait. A FAIL reads UNRESOLVED until someone classes it.
- **the-proof-build-never-touches-the-clone.** A job with `proof_build` builds with `-p:RmProofs=true` into the Windows
  stage, copies the DLL into the game only, and leaves the clone's `Assemblies` byte-identical. A build that fails is
  INVALID/DEPLOY, never a verdict. The next job without it deploys the release DLL again.
- **the-filler-does-not-repeat-a-chain-in-flight.** The filler leaves out the chains of the mod that a job runs or
  waits to run. Measured 2026-11-24: the filler gave Steve1 the four Pyrelands chains that Steve2 was still running
  (J20261124T051635Z, J20261124T053209Z), four times since 2026-11-22.

Later lists beside this page: `polish.md`.
