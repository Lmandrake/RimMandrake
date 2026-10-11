# FLOWWORKS_FORCED_PIT_FALL_ROW_1 - FlowWorks forced-entry pit fall row

Filed 2026-10-07 from the GREEN-MIN / L2 sweeps (Transient/*_20261007.md).

## spec
FlowWorks validation_v2 row P3 (walk into a pit, held, one descent, fall damage) now asserts the REFUSAL, because FLOWWORKS_PIT_FALL_ONLY_FORCED_1 (owner 2026-10-06) forbids careless pathing into a pit (path veto 790fd4e8d, RM_PitTrapMath.cs:244-269). The forced-entry half is therefore unmeasured: add a row where a pawn is forced in (flyer landing counted by RM_Patch_PawnFlyer_LandInPit, or explosive knockback) into a D=4 pit with no ladder and falls with damage and is held. Evidence: Transient/flowworks_regression_20261007.md H1 / P3.

## verify
src/RimMandrake/FlowWorks/northstar/validation_v2.py on a FlowWorks quicktest; check whether a bridge tool can force a flyer landing or an explosion (else pair with a bridge-tool item).

## criteria
A1: a new row (e.g. P3_forced_entry_falls) exists in validation_v2 and can FAIL (control: same pawn walking in is refused).
A2: a live run records the row PASS: pawn ends in the D=4 cell, one fall wound, held until a ladder is built; P4/P5n rows that cascaded from P3 are re-checked.

## live check
New mechanism never seen: a forced (flyer or knockback) entry into a D=4 pit has never been observed live.

NEXT: claim this item and start with criterion A1.
