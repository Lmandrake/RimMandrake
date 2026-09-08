# Antiquities — validation walk
subject: src/RimUtinni/Antiquities
packageId: mandrake.rut.antiquities  (from About.xml, verbatim)
deps: none (only ludeon.rimworld/Core in modDependencies+loadAfter)
list: minimal     # no third-party modDependencies; RSW_Jawa is NOT required — the walk uses an existing map pawn, not a spawned one
status-hint: A five-stage research tree (LANGUAGE → RELIGION → CULTURE → CARTOGRAPHY → VOICE) advanced only by carrying antiquity items to a reading station and reading them — vanilla's own research-bench work can never touch these projects.

## must be true
- `RUT_ExamineAntiquity` (JobDef) exists, driven by `JobDriver_ExamineAntiquity`, and its WorkGiver (`RUT_ExamineAntiquity`, class `WorkGiver_ExamineAntiquity`) only proposes the job for an uncatalogued item whose defName is in `{RUT_Antiquity_Urn, RUT_Antiquity_Stele, RUT_Antiquity_Gravegood, RUT_Antiquity_Testament}`, a reachable `RUT_AntiquityReadingStation`, and while `AntiquityUtility.CurrentStage()` is non-null.
- The five `RUT_Antiq_*` ResearchProjectDefs form a strict linear prerequisite chain (Language → Religion → Culture → Cartography → Voice), each carrying an `AntiquityStageExtension` with `artifactsRequired` = 4/7/10/12/15 respectively.
- Every stage's `requiredResearchBuilding` (`RUT_AntiquityCipherBench`) is permanently unbuildable (`selectable=false`, no `designationCategory`, no recipe) — the ONLY way a stage gains progress is `JobDriver_ExamineAntiquity.CompleteReading` calling `Find.ResearchManager.AddProgress` directly, never a vanilla research bench.
- `RUT_AntiquityReadingStation` is a real, player-buildable `Production` building (costList Steel 40 + ComponentIndustrial 2).
- Reading an antiquity is non-destructive: `CompAntiquity.catalogued` flips true and the item is dropped back on the map intact, never consumed.
- `CompleteReading` grants `stage.baseCost / artifactsRequired` progress per read (doubled on a key-text roll, which only becomes possible once Language is finished), and always grants 40 XP each to Intellectual and Artistic on the reading pawn.
- Once all five stages are finished, `WorkGiver_ExamineAntiquity.ShouldSkip` returns true — no more antiquity-hauling jobs are offered.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rut.antiquities" and no XML error naming RUT_Antiquities_Buildings.xml, RUT_Antiquities_Research.xml, RUT_Antiquities_Items.xml, RUT_Antiquities_Jobs.xml or RUT_Antiquities_WorkGivers.xml
2. [D] def read-back: JobDef RUT_ExamineAntiquity; driverClass = RimMandrake.Utinni.Antiquities.JobDriver_ExamineAntiquity
3. [D] def read-back: ResearchProjectDef RUT_Antiq_Language; baseCost = 500; techLevel = Neolithic; requiredResearchBuilding = RUT_AntiquityCipherBench; modExtensions[AntiquityStageExtension].artifactsRequired = 4
4. [D] def read-back: ThingDef RUT_AntiquityCipherBench; selectable = false, thingClass = Building_ResearchBench (confirms the "never buildable" mechanism the design doc relies on)
5. [D] def read-back: ThingDef RUT_AntiquityReadingStation; designationCategory = Production; costList Steel=40, ComponentIndustrial=2
6. [B] jawa/build_batch ops='RUT_AntiquityReadingStation:X,Z' faction=player → station spawns; read back id
7. [B] rimworld/spawn_thing defName=RUT_Antiquity_Urn x=X z=Z+2 → urn spawns
8. [B] jawa/list_things defName=RUT_Antiquity_Urn,RUT_AntiquityReadingStation → both ThingIDs present, isCompleteList=true
9. [B] jawa/list_pawns faction=player → pick one existing colonist ThingID (no need to spawn a new pawn kind)
10. [B] jawa/ordered_job pawnId=<colonist id> jobDef=RUT_ExamineAntiquity targetAId=<urn id> targetBId=<station id> → accepted; curJob.def == RUT_ExamineAntiquity
11. [B] rimworld/step_game_ticks ticks=60000 (FullDayTicks — Language not yet finished, so the Wait toil runs the full day) → job completes
12. [B] jawa/inspect_string thingIds=<urn id> → inspect text contains the "RUT_Antiquity_Catalogued" translation ("Catalogued"), not "RUT_Antiquity_Uncatalogued" ("Not yet read")
13. [B] rimworld/list_letters → newest letter's label matches "RUT_Antiquity_LetterLabel" ("A page, read")
14. [B] jawa/research_availability project=RUT_Antiq_Language → project snapshot shows progress > 0 (expect 125 = 500/4, or 250 on a key-text roll)
15. [D] def read-back: WorkTypeDef RUT_ExamineAntiquities; relevantSkills = [Intellectual, Artistic] (feeds both auto-priority AND, per JobDriver_ExamineAntiquity's skillFactor lerp, read duration)
X. [S] (human pass) placeholder art — RUT_AntiquityReadingStation and all three item defs currently reuse the vanilla AIPersonaCore texture; the real reading-station art/animation is a later slice
