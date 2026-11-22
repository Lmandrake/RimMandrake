# BOUNDARY: maturation.py `gate_step` (the stage-record part of `next_step`) when the stage moves during its read, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation.py` (`gate_step`; `next_step` is `mod_next.next_for`, page
`design/specs/2026-11-22-mod-next/boundary.md`). Item `RIMMANDRAKE_GUARD_NEXT_STEP_STAGE_MOVED_MID_READ`.
Each promise has a test of its name in `src/RimMandrake/rimflow/selftest_next_step_stage_moved.py`.

`gate_step` loads the stage record, then `ingame_facts` or `blind_facts` loads it again. When a move lands between the
two loads (2026-11-21 4:33 AM PST: the Conductor advanced GimmeSomeSlack to Stage 7 while the Dispatch tick built a
Stage 6 steward brief), the second load sees another stage and returns no `visit` or `cycle`. Before this page,
the function (then named `next_step`) raised `KeyError: 'visit'`, and the steward brief carried "maturation.py next failed: 'visit'".

## ACCEPTS

- **a-record-that-moves-at-most-once-per-read.** A move written by another process between the two loads.

## DOES NOT SURVIVE (not handled)

- **a-record-that-moves-on-every-read.** `gate_step` reads again once. When the stage moves again during that second
  read, it returns stage UNMEASURED with the reason, and gives no reading of either stage.

## PROMISES (each one is owed a test of the same name)

- **stage-moved-mid-read-reads-again.** When the stage that `ingame_facts` or `blind_facts` reads is not the stage that
  `gate_step` loaded, `gate_step` raises nothing. It reads the record again and returns the reading of the stage that
  it now holds.
- **stage-moving-twice-is-unmeasured.** When the stage moves during the second read too, `gate_step` raises nothing. It
  returns stage UNMEASURED, a `next` line that says that the stage moved during the read, and no refusals.
