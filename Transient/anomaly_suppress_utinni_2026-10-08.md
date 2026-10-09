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
