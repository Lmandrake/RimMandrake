# BOUNDARY: maturation.py `next_step` when the stage moves during its read, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation.py` (`next_step`). Item `RIMMANDRAKE_GUARD_NEXT_STEP_STAGE_MOVED_MID_READ`.
Each promise has a test of its name in `src/RimMandrake/rimflow/selftest_next_step_stage_moved.py`.

`next_step` loads the stage record, then `ingame_facts` or `blind_facts` loads it again. When a move lands between the
two loads (2026-11-21 4:33 AM PST: the Conductor advanced GimmeSomeSlack to Stage 7 while the Dispatch tick built a
Stage 6 steward brief), the second load sees another stage and returns no `visit` or `cycle`. Before this page,
`next_step` then raised `KeyError: 'visit'`, and the steward brief carried "maturation.py next failed: 'visit'".

## ACCEPTS

- **a-record-that-moves-at-most-once-per-read.** A move written by another process between the two loads.

## DOES NOT SURVIVE (not handled)

- **a-record-that-moves-on-every-read.** `next_step` reads again once. When the stage moves again during that second
  read, it returns stage UNMEASURED with the reason, and gives no reading of either stage.

## PROMISES (each one is owed a test of the same name)

- **stage-moved-mid-read-reads-again.** When the stage that `ingame_facts` or `blind_facts` reads is not the stage that
  `next_step` loaded, `next_step` raises nothing. It reads the record again and returns the reading of the stage that
  it now holds.
- **stage-moving-twice-is-unmeasured.** When the stage moves during the second read too, `next_step` raises nothing. It
  returns stage UNMEASURED, a `next` line that says that the stage moved during the read, and no refusals.
