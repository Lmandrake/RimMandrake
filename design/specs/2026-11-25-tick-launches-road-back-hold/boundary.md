# Boundary: the tick launches the holder bundle on a road-back hold

Code: `build_facts` and `ledger_waits` in `src/RimMandrake/rimflow/maturation.py`; `decide` (its `owed == "blocked"`
branch, `road_back_decide`), `pilot_holders`, `pilot_refusal` and `holder_spent` in `src/RimMandrake/rimflow/maturation_dispatch.py`;
`resolve` and `road_back_ids` in `src/RimMandrake/rimflow/work_bundle.py`. Tests: each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_dispatch_road_back_hold.py`. Item: `RIMMANDRAKE_LAUNCH_ROAD_BACK_BUNDLE_BY_TICK_READS_BLOCKED`.

The failure, 2026-11-25 from 3:52 to 4:00 PM PST: Explosive Knockback 0.2.0 stood at the offline build on its road back
from in-game visit 1. The tick read `blocked (paused): refused by road_back_items, not build work`, with both games free
and nothing live on the mod, and launched nothing. The road-back hold
(`design/specs/2026-11-25-road-back-holds-stage-exit/boundary.md`) named one open item that the stage can work. Also,
`./pipe bundle ExplosiveKnockback` answered `NO BUNDLE: no ready member`, because the two open road-back tickets had no
home.

## How the two readers of road-back items agree (the choice)

The one reader is `maturation.road_back_hold`. The tick takes its `open` list (the items that the stage can work) as the
holder's items, through `build_facts`. The hand bundle (`./pipe bundle <Mod>`) adds the same `open` list to the mod's
homed tickets, through `work_bundle.road_back_ids`. No ticket is re-homed. This is the smallest change: the hold already
finds the items by `caused_by` and by the names in the move's why, so both readers ask it.

## ACCEPTS (the only inputs this is built for)

- **a-road-back-hold.** `road_back_hold(...)` as `evaluate` reads it: `open`, `stage6`, `unread`, `move`.
- **a-dated-wait.** The ledger's `wait` event (`until`, `reason`) and `unwait` event on a road-back item.
- **a-decide-row.** A row of `decide` at the offline build whose `owed` is `blocked`.

## DOES NOT SURVIVE (not promised)

- **a-road-back-hold-at-another-stage.** `build_facts` reads the offline build only. A road-back hold on a mod at the
  blind challenge or in-game acceptance is not read by this path.
- **a-wait-date-that-cannot-be-read.** An item whose wait date cannot be read is left out of the holder's items, and the
  line says so. It is never worked as free.
- **a-hand-bundle-on-the-same-set.** A bundle launched by hand (`./pipe bundle`) is not booked in `holder_road_back`. The
  tick's `holder_spent` does not count it. Its one-live-bundle rule (`work_bundle.holder_bundle`) still refuses a second
  bundle while it is live.

## LIMITS

None.

## PROMISES (each one is owed a test of the same name)

- **a-road-back-only-refusal-launches-the-holder.** At the offline build, when `road_back_items` is the only non-build
  exit refusal, its hold reads, and an open item that the stage can work is not on a dated wait, the tick launches the
  mod's one holder bundle (`pilot_holders`, decision `launch`, `holder_items` = those open items). `build_facts` carries
  the hold as `road_back_hold`: `open`, `stage6`, `unread`, the move's time and the dated waits.
- **a-hold-among-the-refusals-reads-held.** A `hold` among the refusals still reads `held` and launches nothing. Another
  non-build refusal beside `road_back_items` still reads `blocked`.
- **an-unread-road-back-says-could-not-look.** A hold with an `unread` source, or a `road_back_items` refusal with no hold
  reading, reads `blind`, says "could not look", and launches nothing.
- **a-spent-holder-on-the-same-set-launches-nothing.** A holder run booked since the move, on a set that the open set has
  not shrunk from, reads `holder_spent` and launches no second run. A holder run from before the move does not count.
- **a-live-run-on-the-mod-is-a-wait.** A live run on the mod reads `live` and launches nothing.
- **an-item-on-a-dated-wait-is-left-out.** An open item on a dated wait is left out of `holder_items`. When every open
  item is on a dated wait, the row reads `road_back_wait` (a named wait in `maturation_autonomy.WAIT`) and launches
  nothing, and `waits_on` names each item, its date and its reason, and the Stage 6 items.
- **a-non-pilot-names-the-hand-route.** A mod that `pilot_ledger` refuses launches nothing. Its line names
  `./pipe bundle <Mod> --why ...` and why it was refused, in words (`pilot_refusal`): not a ledger pilot, or a pilot whose
  mod ledger is not ready, with the readiness test's last line.
- **a-road-back-item-with-no-home-is-a-bundle-member.** `work_bundle.resolve` of a mod takes the open items of the
  mod's road-back hold beside its homed tickets; a closed one is no member; a hold that cannot be read keeps the homed
  tickets and its why says "could not look". The tick's holder bundle holds a road-back item that has no home.

Later lists beside this page: `polish.md` (none yet); `next_version.md` (none yet).
