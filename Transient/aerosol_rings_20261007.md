# Aerosol rings build 2026-10-07 (WARSCAR_AEROSOL_SCREEN_1 parts 6, 8, research half of 4)
Root: D:\Luke\dev\RimMandrake\src\RimMandrake\Scarlands (work in /home/mandrake/rm/foundry). Uncommitted.
New: Source/RM_WarscarRings.cs, Defs/ThingDefs_Buildings/RM_WarscarProjectors.xml, Defs/ResearchProjectDefs/RM_AerosolScreenResearch.xml, Defs/GenStepDefs/RM_WarscarRings.xml
Edited: RM_Warscar.csproj (Compile), RM_WarscarMod.cs (hummingRingsPerMap=2, shipWakesLine=true; Scribe + UI), BiomeDefs/RM_Warscar.xml (extraGenSteps), RM_AerosolScreen.xml (researchPrerequisites)
Build: winbuild RM_Warscar.csproj -> 0 warnings, 0 errors, DLL+srchash rewritten (dirty source stamp).
XML: validate_patch over Scarlands/Defs: 0 errors in new files; 3 pre-existing texPath errors (CloakLacquer, FilthBone, ChatrakPlate), no --defs run.
Non-consumption: vanilla CompAnalyzable.OnAnalyzed (RimSage) destroys parent only if Props.destroyedOnAnalyzed; defs set false (as Biotech chips do).
Design: dead+live share analysisID 740100005; RM_CompRingAnalyzable refuses interaction while ring not live. Dead ring live = shipWakesLine && GravEngine within 40 cells (rare-tick cache, 250 ticks). GenStep order 536, ring at wall-centroid outer radius +2..6, first ring always live, others 40%.
Unverified: never run in game; ThingDefOf.GravEngine used as engine def; requiredAnalyzed resolution with subclassed comp (same pattern as inscribed panels); live ring is Damageable/destroyable (deconstructible=false, salvage is spec 7, not built); art is placeholder.
