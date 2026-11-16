# RIMMANDRAKE_FIX_PYRELANDS_BURN_COST_TEST_RED_TWICE_TODAY

## spec

T_BURN_COST (src/RimMandrake/Utils/selftest_pyrelands_burn_cost.py), a supporting test of four Pyrelands bars
(scorchfruit_born_of_fire, ashwallow_dives_unharmed, inv_burn_line_fire_clock, inv_burrowers_heat_dome), is red on
build 9c5c455550074ca74390 at both certificate stamps of 2026-11-16 (04:06Z and 15:34Z):

    FAIL the Postfix no longer rolls through FirstLegalFruitSpot + TakeFruitRollAt
    FAIL the 3x3 scan is no longer gated on the fire not having rolled yet
    FAIL the roll gate is no longer exactly rolledFires != null && !rolledFires.Contains(__instance.thingIDNumber)
    FAIL FirstLegalFruitSpot (the 9 probes) runs outside the not-yet-rolled block

FireEcologyHook.cs now takes `rolledFires` from MapComponent_PyrelandsAshField.For(map)?.RolledFruitFires before
RM_FireEcoKernel.RollSetFor (line ~457). Unknown which side is wrong: either the fire-tick postfix lost the
closure-free, not-yet-rolled-gated fruit scan (FIRE_SCAN_DIAGNOSE_BIG_BURN_COST, 0069f25843), a MOD defect, or the
test's text pins are stale against a legitimate rework, a TEST defect. Read the postfix against the four claims; fix
whichever is wrong. It is not a decider of any bar, so the certificate stays OK while it is red.

Found by RIMMANDRAKE_AUTOBUILD_PYRELANDS_ZERO_LEFT (maturation.py certificate Pyrelands --run, 2026-11-16).

## Acceptance test

`python3 src/RimMandrake/Utils/selftest_pyrelands_burn_cost.py` exits 0 (expected: no FAIL line). Watched it fail at
filing (exit 1, 4 FAIL, the lines above). If the fix is to the test, its mutants must still go red on a postfix that
scans outside the not-yet-rolled block.
