# RIMMANDRAKE_ROUTE_SPENT_LIVE_FIXER_PILOT_BY_HAND

Filed 2026-11-17 by the hand-act fold run (Conductor brief: fold the 13 open hand acts behind OPS_MATURATION_HAND_ACT_UNFOLDED).

## spec

MEASURED 2026-11-17 (`rimflow show RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES`; `grep -n -i testpilot` over `maturation_dispatch.py` and `detached_helper.py` finds nothing): the Maturation tick has no Test Pilot step.

Explosive Knockback's walk-raid road-back item ended LEFT OPEN three times on live measurement: 02:13Z, 12:05Z, and 13:29Z on 2026-11-16. The Conductor then launched two Test Pilot sittings on it by hand:
- `run-...-fix-walk-raid-six-failed-row-1794835988`, which was killed;
- `run-...-1794837119`, which found the MOD cause, fixed it and closed the item at 773b9baea3.

These were the hand acts on 2026-11-16 at 13:33:08Z and 13:51:59Z.

Relentless already routes this case (TEST_PILOT_WIRE_INTO_THE_PIPELINE_EARLY: `pilot_count` / `rules.pilot_after_live_fails` in `relentless.py`). The tick's fixer and pilot-holder launches never do. The owner's standing word (2026-11-04) asked for Test Pilots "in the Pipeline too, not just Relentless".

Make the tick's next run on a road-back item a Test Pilot sitting (`rm-testpilot`, its model per `relentless.py` `pilot_model`) once that item has the Relentless count of live non-pass endings since its last sitting. Reuse that count; add no new key to `relentless_rules.json` (Relentless freeze 2026-11-06). Count a killed sitting as no sitting: it is retried under the existing killed-run rule.

## refs

file: src/RimMandrake/rimflow/maturation_dispatch.py
file: src/RimMandrake/rimflow/relentless.py

## verify

Acceptance test: a new case in `selftest_maturation_dispatch` must be red on the base and green after the fix. The case: a pilot road-back item with N LEFT OPEN live endings and no sitting since. The tick's next launch on it must be a Test Pilot sitting, and the earlier endings (fewer than N) must still go to a fixer.

Run it with `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_maturation_dispatch`.

## criteria

- The tick launches the sitting itself; no Test Pilot on a road-back item is launched by hand.
- A sitting's endings reset the count, as in Relentless.
