# Selftest regressions 2026-10-07
1. FeverWood broodcampaign: _sub/BEHAVIOURS pointed at pre-kernel text. Re-pointed to call sites in RM_CompCapturedSpecimen.cs/RM_BroodRansom.cs plus kernel rules in Source/Kernel/*.cs (reader now scans Source/Kernel); 5 kernel mutations added. 0 failures.
2. TheForge: validation.py _phases() read enum ForgeCyclePhase from RM_GameCondition_ForgeCycle.cs; enum moved to Source/Kernel/RM_CycleKernel.cs (phases 0 -> every parse-dependent break failed). Fixed validation.py path. All 64 breaks pass.
3. suite_corrections Droidworks trade: mock lacked jawa/static_call (DroidworksProofs.MakeTrader). Added OK reply; shifted-steel PASS and no-shift FAIL properties unchanged. SELFTEST OK.
Full run: 261/263; failing: selftest_leaningscrub_fuzz.py, selftest_thesump_fuzz.py (others' mods).
