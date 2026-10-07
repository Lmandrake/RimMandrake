# TITANIC_BODYSIZE_TEST_RACE_1 - Titanic bodySize test race

Filed 2026-10-07 from the GREEN-MIN / L2 sweeps (Transient/*_20261007.md).

## spec
TitanicCreatures five `not_driven` rows (T2/T3 tiers, yield curve, roof, footprint) are UNMEASURED because no vanilla race has baseBodySize >= 8 (max 5.0: Dreadmeld, Moose) so no Titanic-tier creature can be spawned in a vanilla list. Options: (a) a tiny test race ThingDef with bodySize 8 and 20 in the harness-only test mod; (b) a JawaBench tool that overrides a live pawn's BodySize / tier. Prefer whichever is cheaper to keep honest; evidence Transient/titanic_harness_20261007.md and live_recheck2_20261007.md line 17.

## verify
Spawn the test creature on a quicktest map and run the TitanicCreatures validation script.

## criteria
A1: a test race (bodySize 8 and 20) or BodySize-override bridge tool exists and is documented in the rimbridge-companion tool list.
A2: the five not_driven rows run and each is PASS or a classified FAIL, with results JSON in Transient/modcheck/.

## live check
New mechanism never seen: the Titanic T2/T3 tier, yield, roof and footprint mechanics have never been observed running.

NEXT: claim this item and start with criterion A1.
