# Decision strings — ExplosiveGrowth + biome fixes live verification, 2026-09-26

Full mod list load (629 mods after this session's ModsConfig edit). Written BEFORE
launch per rimworld-load-round §2/§3.

## New assembly: RimMandrake.ExplosiveGrowth.dll (mandrake.rm.explosivegrowth)
PROVE  Player.log contains a startup line from RM ExplosiveGrowth naming how many
       plant defs soak (roster resolution count).
EXPECT `[RM ExplosiveGrowth]` line present, N > 0 plant defs (some donor-plant
       roster names may not resolve — expected, not a failure, per build report).
LIES   Silence could mean the mod didn't load (check ModsConfig activeMods has it)
       OR that the log line was never written for this build (grep the source for
       the exact log call before treating absence as a startup failure).

## Load order: ExplosiveGrowth before PlantGrowth
PROVE  `mandrake.rm.explosivegrowth` (index 585) appears before `mandrake.rut.plantgrowth`
       (index 586) in ModsConfig.xml, and PlantGrowth's own ExplosiveGrowth/ subfolder
       (RUT_BloomBurst IncidentDef, RUT_ExplosiveGrowthRoster.xml) resolves with no
       cross-reference errors.
EXPECT No "Could not resolve cross-reference" for RUT_BloomBurst or the roster's
       plant defNames.
LIES   A patch that matches nothing logs nothing — absence of an error is not proof
       the roster actually populated; cross-check jawa/get_defs on RUT_BloomBurst.

## Modified assembly: RimMandrake.EnvironmentalHazards.dll (Scarlands/Sump/Miasma fixes)
PROVE  `RUT_SentinelGraveWard` GenStepDef (RUT_ScarlandsGraveWardScatter) present with
       no config errors; RM_JobDefs_DisarmLotteryTrap / RM_WorkGiverDefs_DisarmLotteryTrap
       load clean.
EXPECT Zero "Config error in RUT_SentinelGraveWard" / zero errors naming
       RimMandrake.EnvironmentalHazards.
LIES   A GenStep with no errors can still never fire at map-gen time (wrong biome gate,
       wrong commonality) — config-clean is not "it scattered". Needs the live Scarlands
       map spot-check (step 5), not just log silence.

## Modified assembly: RimMandrake.FloodedCanyon.dll (not enabled in ModsConfig this session)
PROVE  N/A this load — mandrake.rm.floodedcanyon is deployed but NOT in ModsConfig
       (confirmed absent). Its content rides no risk this load.
EXPECT No entries at all for FloodedCanyon in the log (mod inactive).
LIES   N/A.

## Batching rationale
Three assemblies (ExplosiveGrowth new, EnvironmentalHazards modified, PlantGrowth
modified) ride together. Per rimworld-load-round §3 this is affordable only because
their failure signatures are distinguishable (own log line / own defName / own
GenStepDef), which is why each is written above before the log exists.

## Baseline
`harvest_log.py` baseline config/crossref/patch-failure counts on this same 629-mod
stack have not been separately re-baselined for this session's additions; standing
baseline is "zero errors naming any of our four touched mods."
