## spec
Live 2026-11-03 (TITANIC_BODYSIZE_TEST_RACE_1 gen 7, 3 runs, Transient/modcheck/titan_test_races_a2_gen7c.json): TitanValidationHooks.RoofWallProbe(RM_TestTitanT2|125,125) -> roofAfter=none (thin roof holed) but wallHpBefore=195 wallHpAfter=195 wallDestroyed=False. RM_CrushRules.xml RM_Crush_Walls is crushable, minTier T2, so a T2 stepping into the roofed wall cell should damage or break the wood wall. The control left both, as expected.
Diagnose: wake crush path vs the probe (does the probe step INTO the wall cell; is the wall matched by RM_Crush_Walls; does the crush run on the Position setter or later).
## criteria
A1: row t2_holes_thin_roofs_and_crushes_walls of src/RimMandrake/HugeThings/northstar/titan_test_races_live.py reads PASS live, or the probe is shown wrong and fixed.
