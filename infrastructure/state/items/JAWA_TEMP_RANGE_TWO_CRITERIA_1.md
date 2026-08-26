# JAWA_TEMP_RANGE_TWO_CRITERIA_1 — two rows of one item name different PASS values

`LIVE_HALF_OF_LOAD_1` grades the Jawa's `ComfortableTemperatureRange` twice and the two
criteria disagree:

* **T2** — *"`Jawa` ≈ **−40…+65**"*
* **N1** — *"PASS = **−50…+55** … Jawa at −60…+65 = the LARGE tier came back"*

Both cannot be the pass condition for the same stat on the same pawn.

## What the live game says about the inputs

Read off a spawned instance with `jawa/pawn_genes` (never the def): `MandrakeJawa` carries
**`MinTemp_SmallDecrease`** and **`MaxTemp_SmallIncrease`** — one Small step each way off the
−40…+45 baseline, and **no Large tier gene at all**. That is N1's number, not T2's.

⛔ **I did not substitute my own criterion.** An observer who picks the criterion after looking
has not tested anything (`CHECK.md > Intake`). This needs the owner of the design to say which
range is intended; then T2 or N1 is corrected in `LIVE_HALF_OF_LOAD_1` and the row is graded.

⚠️ Grading is blocked on `PAWN_STAT_READ_HAS_NO_TOOL_1` regardless — the stat itself cannot be
read from outside the game today.

Evidence: `infrastructure/state/evidence/live_half_of_load_2026-08-26_CHECK.md`
