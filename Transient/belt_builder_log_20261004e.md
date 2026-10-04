# FOUNDRY offline builder log, round 5, 2026-10-04

- 03:06 start
- 03:09 brief's TwilightSea <li> claim FALSE (0 li in 349 patch files, probe 4 rows); real load error = RSW_VentStalker wildBiomes+RUT_Cauldron wildAnimals double-registration (same-key throw), fixed
- 03:11 c7b82aa89 pushed. BURROW_TIMER_SAVE_LOAD_1 already filed (fix needs Pyrelands DLL rebuild, held this round)
- 03:12 filed LUMINOUS_PIGMENT_STARTUP_NRE_1 (startup NRE, Find.Maps w/o game). queue: 53 offline proposed, mostly multi-day builds
- 03:12 taking ART_OVERRIDE_FAMILY_SCRIPT_1 (offline slice: static family script; live run left)
- 03:14 art_override_family.py written, testing
- 03:15 f23bdb2d5 ART_OVERRIDE_FAMILY_SCRIPT_1 static layer (kept open for live); filed MYCOID_ART_OVERRIDE_DEAD_1, MANTISTANIS_DONOR_ABSENT_1
- 03:16 MANTISTANIS traced: dead donor, override should be retired at next deploy window
- 03:16 closed CUT_BY_NOBODY_SOURCE_1 (already done at 3a88ebb6b)
- 03:17 NORTHSTAR_PARTIAL_GAPS_FILL_1: ScarlandsLadder static R25 ban scan added
- 03:18 TrophyCraft static trade bars committed (red-probed)
- 03:22 StarWarsRaces rulepack bar + SandP fix committed; filed AQUALISH_NAME_WORDLISTS_1
- 03:23 b80d5967b AQUALISH_NAME_WORDLISTS_1 closed; PARTIAL_GAPS note
- 03:26 selftests 171/172 (known parallel-only fail). stopping: remaining queue is multi-day builds or DLL work on mods deployed this session
