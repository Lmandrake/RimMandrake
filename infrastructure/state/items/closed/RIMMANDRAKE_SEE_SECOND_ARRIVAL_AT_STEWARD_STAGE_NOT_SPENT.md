# RIMMANDRAKE_SEE_SECOND_ARRIVAL_AT_STEWARD_STAGE_NOT_SPENT

Filed by Operations (incident `maturation-20261121225203`, `maturation.paused` 1). Fixed in the same run.

## spec

- The tick keys the steward of a steward stage (Preflight, Stage 2; Walk brief, Stage 7) as `<version>|<stage>`. The
  key has no arrival. A mod that reaches the stage again at the same version reads the first arrival's steward as
  "ended and the state has not moved" (`steward_spent`), and the mod PAUSES.
- Measured 2026-11-22 06:03Z: GimmeSomeSlack 0.1.1 reached Stage 7 at 2026-11-21 04:33 PST. Its steward
  (`rm-detached-bench-rimmandrake-steward-gimmesomeslack-pre-h-1795265290`, booked 12:47Z) wrote `arrival_1` and
  advanced the mod to his walk at 04:58 PST. The mod went back to Stage 6 (856026c2ee) and arrived at Stage 7 again
  at 21:40 PST (5c9e5a68c5, `pre_human_arrivals` 2). The tick then read PAUSED steward_spent.
- Fix: `maturation_autonomy._arrival_key`. When the booked run's `at` is older than the mod's latest arrival at the
  stage (`facts["arrived"]`, `maturation_dispatch.arrivals`), the key grows `|arrived:<epoch>`. A booking at or after
  the arrival keeps its key, so no mod that is truly spent on this arrival gets a second steward.

## verify

- `python3 src/RimMandrake/rimflow/selftest_maturation_autonomy.py` → `rearrival_checks`: 4 FAIL on the parent
  (a later arrival read paused/steward_spent), ALL PASS on the fix.
- Live: `maturation_dispatch.py next` read `WILL START … GimmeSomeSlack steward … Walk brief (Stage 7)` with the fix.

## criteria

- A second arrival at a steward stage at the same version gets exactly one steward run.
- That steward, ended on an unmoved state, is spent as before; never a third without a new arrival or new work.
- `maturation.paused` no longer counts GimmeSomeSlack for this cause.

## refs

- file: `src/RimMandrake/rimflow/maturation_autonomy.py`
- file: `src/RimMandrake/rimflow/selftest_maturation_autonomy.py`
