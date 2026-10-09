# Findings batch 2 2026-10-09

(items below)
- GELATINOUSSLIME_SEEKER_MARK_FAILS_1, LEANINGSCRUB_BLOOM_TOGGLE_OFF_STILL_FIRES_1, RUSTCATHEDRAL_SETTINGS_CROSSBIOME_ROUNDTRIP_1, MIASMA_MOTHERS_PRICE_RETURN_SITE_1: already fixed in 220d7a754 (see Transient/acc_biomes_fixes_20261008.md); ledger not updated; marked implemented. Live re-run owed.
- LINKED_GRAPHIC_ICON_NRE_1: all 9 of our linked graphicDatas resolve in source; def unidentifiable offline, left open (needs live/log).
- CAULDRON_YIELD_HARVEST_ORDER_FAIL_1: HARNESS (queued Harvest behind GoForWalk); queue=False; selftest 63/63; 09d32ba8f. Live rerun owed.
- SCARLANDS_CHATRAK_SNAP_STAGE_02_1: HARNESS (" armed 1" is map-wide count, read 3) -> >=1; "no free colonist" -> UNMEASURED; e0732bd98. py_compile only.
- CREATUREBEHAVIORS_TRACKGRID_BRIDGE_TIMEOUT_1: already fixed 2d63ed4cd (per-walker PrintsBy tally); implemented.
- WASTELAND_TOXIC_BUILDUP_NEVER_APPLIES_1: harness (dose interval 3451 ticks), fixed 220d7a754; implemented. WASTELAND_LIVE_SUITE_FAILS_ACC_BIOMES_1 left open: tipping/middenshell toggle rows, gripper/brine timeouts need live.
- CONTAGION_LIVE_SUITE_FAILS_ACC_BIOMES_1, OWNER_SAID_GUARD_MIDTURN_BLIND_1, STILLSAND_* : not touched (live-bound / hook / other agent).
