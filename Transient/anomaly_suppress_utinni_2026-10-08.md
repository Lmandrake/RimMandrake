# Anomaly suppress Utinni 2026-10-08
## Mechanism
40 ScenPart_DisableIncident parts in RUT_Jawa_UtinniStart, one per concrete Anomaly IncidentDef (enumerated from Data/Anomaly/Defs/**, abstracts skipped).
## Evidence
- IncidentWorker.cs:99 checks scenario.parts for ScenPart_DisableIncident with matching incident.
- AnomalyPlaystyleDef is a Difficulty setting (Difficulty.cs); Scenario only has standardAnomalyPlaystyleOnly (forces Standard, the opposite). StorytellerComp.cs:62 blocks Anomaly incidents only when playstyle disables content; scenario cannot set that.
## Files
src/RimUtinni/UtinniPatches/Defs/ScenarioDefs/Scenario_Utinni.xml
## Not covered
Incidents added by future updates; monolith generation, Anomaly quests not routed via those incidents, Anomaly-derived map gen, entity research.
Deploy plan also touches RUT_Desert.xml and AcousticPayload_UtinniBiomes.xml, so not applied.

## Phase 2 (monolith + quests) - decision taken by question card 2026-10-08 22:05
Engine evidence (RimSage, 1.6 decompile):
- GenStep_Monolith.GenerateMonolith(IntVec3, Map) is the single static that spawns the monolith (called by GenStep_Monolith.ScatterAt and ScenPart_MonolithGeneration:62). Harmony prefix skips it when the scenario is RUT_Jawa_UtinniStart.
- Every Anomaly QuestScriptDef except EndGame_VoidMonolith / EndGame_VoidAwakening (both spawned only by Building_VoidMonolith) is rooted in an Anomaly IncidentDef already disabled in phase 1 (Creepjoiner, DistressCall, MonolithMigration, Mysterious cargo, Sightstealer, RefugeePodCrash_Ghoul, UnnaturalDarkness). No monolith => no monolith quests.
- Rejected: postfix GameComponent_Anomaly.GenerateMonolith => false; every gate `level < min && GenerateMonolith` (Designator_Build, CompStudiable, IncidentWorker:117) would then UNLOCK Anomaly content. Skipping the spawn keeps those gated forever.
Home: src/RimUtinni/EmpirePursuit (existing RUT_ assembly with Harmony PatchAll).
