# CRACKEDLANDS_SWALE_CAMPAIGN_LOCK_1 — 2026-10-06 offline pass
Result: NO FILES BUILT. Spec ambiguous / trigger absent; shipping the lock half alone would permanently brick RM_Swale in the campaign.
Findings:
- Item has no prose file; spec = CRACKEDLANDS_MECHANICS_BUILD_1 s1 (WorldComponent flag OR hidden research, world-level, travels with ship).
- RM_Swale: src/RimMandrake/FlowWorks/Defs/Canals/ThingDefs/FlowWorks_ThingDefs.xml (BuildingBase, no researchPrerequisites).
- No existing "campaign lock" implementation anywhere (grep). Nearest precedents: RM_CapstanTurret research (requiredAnalyzed), RM_AcousticSounding, Antiquities unbuildable-bench trick.
- Discovery trigger (first completed survey) does not exist: no survey code in FloodedCanyon/RimUtinni.
Open questions:
1. Mechanism: hidden ResearchProjectDef + researchPrerequisites patch on RM_Swale (vanilla-native, persists in save, travels with ship) vs custom WorldComponent + place worker?
2. If research: which tab/bench to hide it (Antiquities-style unbuildable bench needs a dependency), and who finishes it (Find.ResearchManager.FinishProject on survey)?
3. Survey item must be built first (CRACKEDLANDS_MECHANICS_BUILD_1 s2).
Intended patch home: src/RimUtinni/UtinniPatches/Patches/ (FindMod mandrake.rm.flowworks).
