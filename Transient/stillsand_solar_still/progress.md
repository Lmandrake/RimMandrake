# STILLSAND_SOLAR_STILL_1 progress (FOUNDRY offline agent, 2026-10-11)

## state found
Built 72a77c044: RM_SolarStill, RM_WringingStill, RM_CompSolarStill, RM_StilledWater, RM_Brine, 3 settings.
Missing per 2026-10-07 reconcile: no RM_Brine source; no RUT "drawing" thought; all colonists got the penalty.

## built this pass
- RM_BrineDippingSpot + RM_DipBrine (5 brine / 400 work, PROVISIONAL) + RM_DoBillsDipBrine (Hauling)
- RM_PlaceWorker_BesideTerrain + RM_BesideTerrainExtension (dry cell beside RM_WaterBrineShallow/Deep)
- setting brineDippingEnabled (hides RM_DipBrine)
- RM_WaterLedgerDef.deadDistilledBelieverThought + IsBeliever; witness split via RM_SunKernel.WitnessKind (fuzzed)
- RUT_Thought_DeadDrawn (+2, PROVISIONAL) wired on RUT_SunDebt
- winbuild Stillsand OK (0 warn/0 err); validate_patch 0 errors except a false positive (vanilla CraftingSpot texPath is in Core resources.assets, validator only scans mod Textures/)
- Stillsand selftest 109/109, fuzz PASS, lint PASS. run_selftests 335/407 PASS, 5 FAIL: 4 pre-existing elsewhere (Scarlands texture gaps, art_checks thresholds, walklint, bridgetools tool metadata) + utinnipatches_dump on RUT_Thought_DeadDrawn not in load-14 dump (clears once committed: it skips defs committed after the dump)
- art queued: RM_Brine_v1, RM_StilledWater_v1, RM_WringingStill_v1 (defs still point at tinted stand-ins until install repoints texPath)

## owed live
- L2: still completes a cycle in full sun, stops in the gale; pearl lens doubles rate
- L2: brine dipping spot places only beside RM_WaterBrineShallow/Deep, bill yields 5 RM_Brine
- L2: wringing still: outsiders get RM_Thought_DeadDistilled, Sun-Debt believers get RUT_Thought_DeadDrawn
