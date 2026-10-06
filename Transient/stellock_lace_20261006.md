# GREENTIDE_STELLOCK_LACE_BUILD_1 progress 2026-10-06

## status
started

## plan
- generic found-tech study in EnvironmentalHazards; stellock in Greentide

## findings
- totalBleedFactor exists on HediffStage (RimSage: HediffSet.CalculateBleedRate multiplies it) -> pure XML for bleed
- use shape: copy RSW_BactaPatch (CompUsable + Recipe_AdministerUsableItem wired via Patches)
- pawn cut = Destroy(KillFinalizeLeavingsOnly); RM_TreeFallUtility.FellTree = Destroy(Vanish)
- design: generic RM_CompFoundTechStudy+RM_FoundTechKnowledge in EnvironmentalHazards (gated via RM_MechanicGates); Forge classes become thin subclasses (names kept: walk TheForge.md cites RM_CompSpunstoneStudy)
- DONE RM_FoundTechStudy.cs (EnvHazards) + csproj; RM_TreeFallUtility.FellingNow
- DONE Forge port (RM_ForgeSpunstone.cs facade+legacy load, Flora project, gate reg)
- art already generated (artpipe done/RM_StellockBranch, RM_StellockLace) -> not installed here; placeholder vanilla texPaths; art install owed
- DONE defs: Defs/ThingDefs/RM_StellockLace_Items.xml, hediff in RM_Greentide_Hediffs.xml, Patches/RM_StellockLace_Patches.xml
- NOTE: a concurrent agent is editing Greentide (thurrock) + EnvHazards (TarLull) in this clone; it added the same EnvHazards csproj ref -> removed my duplicate
- DONE RM_StellockLace.cs, settings, gate; Greentide builds
- validate: tree patch ops simulated with lxml on Greentide XML: 14 then 15 matches (validate_patch cannot see Greentide in load set -> its 0-match ERROR is that artifact); recipe ops 1+1 match Core
- builds: EnvHazards, TheForge, Greentide all 0 errors
## status
built offline; live criteria unproven
