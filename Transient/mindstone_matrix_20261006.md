# MINDSTONE_MATRIX_KINDLED_BUILD_1 progress 2026-10-06

## recon
- Harness: RSW_DW_ReassemblyHarness (Droidworks Buildings_ShopBenches.xml); assembly = RSW_DW_AssembleDroid + Recipe_AssembleDroid.cs + DroidAssembly.KindForHeadDef.
- Head item RSW_DW_Head_Mindstone already exists (Heads_Droidworks.xml), excluded from filter + KindForHeadDef.
- Wipe = Recipe_DWMemoryWipe.cs; spike = CompDWDataSpike.TryReprogram; format = Recipe_DWFormat.cs; head drop = CompDWHeadDropper.cs.
- No "head casing" def exists; casing = any salvaged droid head (8 family heads + generic RSW_DW_DroidHead). PROVISIONAL reading.
- Art: artpipe find -> RUT_Mindstone only (sanity hit, 6). Nothing for MindstoneMatrix / Head_Mindstone.

## build (uncommitted)
- NEW src/RimUtinni/UtinniPatches/Defs/ThingDefs_Items/RUT_MindstoneMatrix.xml (RUT_MindstoneMatrix; stats PROVISIONAL)
- NEW src/RimUtinni/UtinniPatches/Defs/RecipeDefs/RUT_MindstoneMatrix_Recipes.xml: RUT_CutMindstoneMatrix (mindstone -> matrix),
  RUT_CaseMindstoneHead (matrix + processor + databank + any salvaged head as casing -> RSW_DW_Head_Mindstone); both at
  RSW_DW_ReassemblyHarness, root MayRequire mandrake.rsw.droidworks; work/skill PROVISIONAL.
- Droidworks: RSW_DW_AssembleDroid filter accepts RSW_DW_Head_Mindstone; KindForHeadDef -> RSW_DW_OuterRim_ProtocolDroid (PROVISIONAL);
  new marker HediffDef RSW_DW_MindstoneMind; Recipe_AssembleDroid kindles (marker + SAPIENT); wipe / spike / format fail with text;
  CompDWHeadDropper drops the mindstone head for a mindstone mind. Head def header prose corrected (was "unruled / no mechanic").
- validation.py: Droidworks chain mindstone_head_wiring (offline), UtinniPatches chain mindstone_matrix_recipes (offline + live def read).

## validation
- winbuild Droidworks: 0 warn 0 err; DLL + new .srchash.
- validate_patch (5 files, --defs game+workshop+src): 0 errors, 1 pre-existing warning (Mechlink vanilla texPath).
- offline probe: both new chains PASS. UtinniPatches defs_vs_dump_static FAILs on exactly the 3 new defs (not yet in the dump: needs deploy + refresh).
  Droidworks' older live chains FAIL under the probe because they are not _live-gated (pre-existing, unrelated).

## art owed (none generated)
- RUT_MindstoneMatrix (placeholder = RUT_Mindstone texture at 0.65).
- RSW_DW_Head_Mindstone (placeholder = vanilla Mechlink).

## left
- Open for BENCH/owner: ruled stat numbers; which pawnkind the Kindled assemble as; what the "head casing" is.
- Live: deploy both mods, refresh dump, run both bills + an assembly, then try a wipe and a spike.
- Commit (explicit paths incl. Droidworks.dll.srchash); code review records.
