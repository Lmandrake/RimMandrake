## spec
jawa/static_call's Thing-arg resolver (StaticCallResolveThing, src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchCompanionProbeTools.cs ~185) splits a ThingID into prefix + trailing digits. A defName that ends in a digit (RM_TestTitanT2, any *2/*3 def) loses its last digit to the number: 'RM_TestTitanT253196' parses as #253196, matches nothing, and the call fails "No thing with ThingID ... on any map" while the pawn is alive (measured live 2026-11-03, TITANIC_BODYSIZE_TEST_RACE_1 gen 7: jawa/set_pawn_age found the same pawn).
Fix: match t.ThingID == a directly (or try every digit split), keep the bare-number branch.
## criteria
A1: a selftest/offline pin that a ThingID whose defName ends in a digit resolves; live: static_call OccupiedRect(<RM_TestTitanT2 ThingID>) succeeds.
Workaround in use: pass the bare thingIDNumber (test_titan_footprint_live.py).
