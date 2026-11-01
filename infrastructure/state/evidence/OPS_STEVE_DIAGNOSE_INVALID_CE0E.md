# OPS_STEVE_DIAGNOSE_INVALID_CE0E: the streak of 2026-10-29

**Verdict: diagnosed; the cause is fixed and has not come back.** The fix shipped under another item, so this item
changes no lane code. It adds a read-only census, `src/RimMandrake/Utils/testq/invalid_census.py`.

## The streak

| job | finished | cause | what happened |
|---|---|---|---|
| J20261029T154735Z-75e3dd | 15:57Z | CANARY | `droid_dig_live` ran, then `canary RED: no live colonist` |
| J20261029T155741Z-323412 | 16:00Z | CANARY | reused the kept game (load 1 s), red at the first line |
| J20261029T181522Z-6dc94b | 18:22Z | CANARY | `droid_dig_live` ran again, canary red again |

Read from `/mnt/d/ClaudeWork/rimmandrake/steve_canary/logs/<job>.a1/modcheck.log` and the done records.

## Root cause

`droid_dig_live` vanished every player pawn, then its own colonist and droid. The vanilla canary runs after the drivers,
so it found no colonist and voided the job. The worker kept that game, so the next job started on the same dead colony.
These were harness failures: no mod row ran, and the mod got no verdict.

Fixed at 59ba780056 (STEVE_LANE_FIX_DEAD_COLONY_CANARY_RED): the driver leaves a colonist, `ensure_live_colony` restores
a map and names the breaker, and a red canary stops the kept game. Proof job J20261029T201848Z-9f6088 was DONE with a
green canary. The auditor called the fix SOUND on 2026-10-30.

## It has not come back

From 2026-10-29T20:27Z to 2026-10-31T23:26Z the lane finished 228 jobs: 211 DONE, 17 INVALID. None of the 17 carry
`no live colonist` and none are CANARY (HARNESS 15, DEPLOY 1, GAME_DIED 1). `droid_dig` went DONE 5 times.

Rerun (the first line shows the instrument can see the streak):

    python3 src/RimMandrake/Utils/testq/invalid_census.py --since 2026-10-29T15:50Z --until 2026-10-29T18:23Z --require-all 'no live colonist' --min 3
    python3 src/RimMandrake/Utils/testq/invalid_census.py --since 2026-10-29T20:27Z --forbid 'no live colonist'

## Not proven

`trench_cover_and_raiders` went canary red the same way on 10-27, 10-28 and 10-29 (162505, 35527f, ac97fa). It has not
finished a job since the fix: its two runs died on unrelated harness faults (28a21e, 78564c). Whether its driver also
kills the colony is unmeasured. Filed: TRENCH_COVER_PROVE_COLONY_SURVIVES_UNSEEN. `ensure_live_colony` should contain
that case either way, because it runs after every driver.

## The later alarms had different causes

The alarm crossed again on 10-30 and 10-31. Those are not this streak:

| jobs | cause | owner |
|---|---|---|
| 5f50de, 77e9fd, 86ef58, f0c31c, 28a21e (10-30) | kept game stopped answering the bridge | OPS_STEVE_DIAGNOSE_INVALID_630C, STEVE_LANE_FIX_WEDGED_KEPT_GAME |
| 1fe7ea, 00238b, dd60e2 (10-31) | game died, then a wounded game was reused (`no_game`) | STEVE_WORKER_UNSTICK_WOUNDED_GAME_KEPT_UP; alarm item OPS_STEVE_DIAGNOSE_INVALID_577B still open |
| 1e76b1, 74d756, d766a0 (10-31) | modcheck exit 5 with no sheet | MODCHECK_DIAGNOSE_EXIT_FIVE_NO_SHEET |
| e1966f (10-31) | `relpath` ValueError on the UNC clone | removed from `status.py` (the comment at the `os.walk` loop says why) |
| 74f811 (`embedded null character`), 78564c (exit 9) (10-31) | modcheck crashes in the Python runner; the path text was corrupt or the process died | no item names these two; they may be the same family as exit 5 (a guess, unmeasured) |
| bf55c0, c153aa (10-29, 10-31) | `companion_handshake`: UNKNOWN-outcome marker | not traced here; a handshake item closed in ledger commit 0c76b7306a, after both jobs |
| b101b5 (10-29) | deploy refused: `RSW_Stygium` alias had no deployed definer | not traced here |

For the next alarm, start with `invalid_census.py --since <streak start>`: the streaks so far had different causes, so
do not assume this one.
