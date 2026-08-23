# -*- coding: utf-8 -*-
"""The roster of RimWorld functionality a JawaBench [Tool] could expose.

🔴 THE OWNER CULLS THIS. Owner, 2026-08-18: *"Produce the FULL roster of RimWorld
functionality we could implement as companion [Tool] methods - not what is built,
what is POSSIBLE - then have the owner select down from it."* Format settled by him
2026-08-23 00:12: **posture is DEFAULT INCLUDE** (a row is a build target unless he
strikes it), cast wide across everything the engine exposes, and the tools that
already exist shown and marked BUILT so he can call one inadequate.

⚠️ EVERY `api` FIELD NAMES A TYPE OR METHOD THAT WAS FOUND, not one that was
remembered - read out of the decompiled 1.6.4871 source via rimsage, plus the
bridge skill's capability and silent-failure references. Where a row is inferred it
says so in `warn`.

⛔ `built=True` means a `jawa/` tool ships for it TODAY - 121 of them, counted from
src/RimMandrake/bridgetools/JawaBench.BridgeTools/*.cs by [Tool( attribute site, NOT
by scanning the DLL. A strings scan of a .NET assembly found 16 of 115 once and
reported it as a clean answer.

Columns: (name, effect, api, difficulty, built, warn)
"""

ROSTER = {
 "Pawn state & health": [
  ("read-health", "Downed/dead, pain, bleed rate, per-part HP", "Pawn_HealthTracker.State / HediffSet.PainTotal / GetPartHealth", "EASY", True, ""),
  ("add-hediff", "Put a disease, implant or injury on a named body part", "Pawn_HealthTracker.AddHediff(HediffDef, BodyPartRecord, DamageInfo?)", "EASY", True, ""),
  ("set-severity", "Force a condition's severity up or down", "HealthUtility.AdjustSeverity", "MEDIUM", False, "⚠️ needs CheckForStateChange afterwards or down/death is not re-evaluated"),
  ("restore-part", "Regrow a destroyed limb or organ", "Pawn_HealthTracker.RestorePart(BodyPartRecord, Hediff, bool)", "EASY", False, ""),
  ("install-bionic", "The full surgery path; cheap route is RestorePart + AddHediff", "Recipe_InstallArtificialBodyPart.ApplyOnPawn", "MEDIUM", False, ""),
  ("force-downed / force-dead", "Deterministic incapacitation with no combat", "HealthUtility.DamageUntilDowned / DamageUntilDead / Pawn.Kill", "EASY", False, ""),
  ("resurrect", "Corpse back on its feet, side effects optional", "ResurrectionUtility.TryResurrect(Pawn, ResurrectionParams)", "EASY", False, ""),
  ("set-age", "Biological age in ticks", "Pawn_AgeTracker.DebugSetAge", "MEDIUM", True, "⛔ FORWARD-ONLY and reports success going backwards"),
 ],
 "Skills, traits, relations & backstory": [
  ("set-skill", "Write a skill level and its passion", "SkillRecord.Level setter + .passion", "MEDIUM", True, "⛔ the Level GETTER adds aptitudes - read GetLevel(false) or the number lies"),
  ("grant-xp", "Real learn-rate path, or bypass it", "Pawn_SkillTracker.Learn(SkillDef, float, direct, ignoreLearnRate)", "EASY", False, ""),
  ("add/remove-trait", "With conflict suppression", "TraitSet.GainTrait(Trait, suppressConflicts) / RemoveTrait", "EASY", True, "⛔ no conflict check and no cap - it will happily build an impossible pawn"),
  ("add-relation", "Spouse, lover, parent, bond", "Pawn_RelationsTracker.AddDirectRelation", "EASY", True, "⛔ only 9 of 41 relation defs are storable this way"),
  ("read-opinion", "The number plus the human-readable breakdown", "Pawn_RelationsTracker.OpinionOf / OpinionExplanation / CompatibilityWith", "EASY", False, ""),
  ("set-backstory", "Swap childhood or adulthood", "Pawn_StoryTracker.Childhood / .Adulthood", "MEDIUM", True, "⚠️ needs 4 follow-up refreshes; RimWorld's OWN debug tool runs 1"),
  ("rename", "Name and the displayed title", "Pawn.Name (NameTriple) / Pawn_StoryTracker.Title", "EASY", True, ""),
  ("royal-title & favor", "Grant or revoke a title, set honor", "Pawn_RoyaltyTracker.SetTitle / SetFavor / GainFavor", "MEDIUM", False, "Royalty-gated"),
 ],
 "Needs, mood & mental state": [
  ("set-need", "Force food, rest, joy, comfort", "Need.CurLevel setter", "EASY", True, "clamped, fires nothing"),
  ("refresh-need-roster", "After a gene/trait/hediff edit changed which needs exist", "Pawn_NeedsTracker.AddOrRemoveNeedsAsAppropriate()", "EASY", False, ""),
  ("list-thoughts", "Every mood thought with its offset", "ThoughtHandler.GetAllMoodThoughts / TotalMoodOffset()", "EASY", False, ""),
  ("add/remove-memory", "Inject or clear a memory thought", "MemoryThoughtHandler.TryGainMemory(ThoughtDef, otherPawn, Precept)", "EASY", False, "⛔ a social thought with no otherPawn is dropped silently"),
  ("force-mental-state", "Any MentalStateDef, bypassing mood entirely", "MentalStateHandler.TryStartMentalState", "EASY", True, ""),
  ("force-mental-break", "A specific or random mood-caused break", "MentalBreaker.TryDoMentalBreak(reason, MentalBreakDef)", "EASY", False, ""),
  ("read-break-thresholds", "Minor/major/extreme thresholds and how close they are", "MentalBreaker.BreakThresholdMinor / Major / Extreme", "EASY", False, ""),
  ("dirty-situational", "Required after most mood pokes or the change does not show", "SituationalThoughtHandler.Notify_SituationalThoughtsDirty()", "EASY", False, ""),
 ],
 "Abilities, psycasts & inspiration": [
  ("grant-ability", "Give any AbilityDef", "Pawn_AbilityTracker.GainAbility(AbilityDef)", "EASY", False, "self-notifies"),
  ("set-entropy", "Add or clear neural heat", "Pawn_PsychicEntropyTracker.TryAddEntropy / RemoveAllEntropy()", "EASY", True, ""),
  ("set-psyfocus", "Offset, fill or retarget psyfocus", "OffsetPsyfocusDirectly / RechargePsyfocus / SetPsyfocusTarget", "EASY", True, ""),
  ("start-inspiration", "Force a named inspiration", "InspirationHandler.TryStartInspiration(InspirationDef, reason, sendLetter)", "EASY", False, ""),
  ("read-psychic-sensitivity", "The stat that scales everything above", "Pawn_PsychicEntropyTracker.PsychicSensitivity", "EASY", False, ""),
 ],
 "Genes & xenotypes": [
  ("set-xenotype", "Clear xenogenes and apply a def's whole gene list", "Pawn_GeneTracker.SetXenotype(XenotypeDef)", "EASY", True, ""),
  ("relabel-only", "Retag the xenotype without touching a single gene", "Pawn_GeneTracker.SetXenotypeDirect(XenotypeDef)", "EASY", False, ""),
  ("add/remove-gene", "Endogene or xenogene", "Pawn_GeneTracker.AddGene(GeneDef, bool xenogene) / RemoveGene(Gene)", "EASY", True, "⚠️ appearance genes need Drawer.renderer.SetAllGraphicsDirty()"),
  ("clear-xenogenes", "Wipe xenogenes, keep endogenes", "Pawn_GeneTracker.ClearXenogenes()", "EASY", False, ""),
  ("reimplant-xenogerm", "Copy one pawn's xenogenes onto another", "GeneUtility.ReimplantXenogerm(caster, recipient)", "MEDIUM", False, "pre-check PawnWouldDieFromReimplanting"),
  ("generate-random-geneset", "Seeded gene set plus auto-named xenotype, for fuzzing", "GeneUtility.GenerateGeneSet(int? seed)", "MEDIUM", False, ""),
  ("gene-resource-poke", "Hemogen and chemical genes", "GeneUtility.OffsetHemogen / SatisfyChemicalGenes", "EASY", False, ""),
 ],
 "Apparel, equipment & inventory": [
  ("wear / strip / destroy apparel", "Dress or undress a pawn", "Pawn_ApparelTracker.Wear(Apparel, dropReplaced, locked) / DropAll / DestroyAll", "EASY", True, ""),
  ("lock-apparel", "Pawn cannot remove it, the ideo/royalty way", "Pawn_ApparelTracker.Lock(Apparel) / LockAll()", "EASY", False, ""),
  ("equip-weapon", "Put a weapon in the primary slot", "Pawn_EquipmentTracker.AddEquipment + Notify_EquipmentAdded", "MEDIUM", True, "⛔ NO-OPS when a Primary already exists - MakeRoomFor first"),
  ("inventory add/remove", "Stuff the pack or take things out", "Pawn_InventoryTracker.TryAddAndUnforbid / RemoveCount(ThingDef, int, destroy)", "EASY", False, "⚠️ TryAddOrTransfer returns a COUNT, not a bool"),
  ("set-quality", "Awful to legendary on an existing item", "CompQuality.SetQuality(QualityCategory, ArtGenerationContext?)", "MEDIUM", True, "then clear the MaxHitPoints stat cache"),
  ("set-stuff retroactively", "Change what an existing item is made of", "Thing.SetStuffDirect(ThingDef)", "MEDIUM", False, "+ stat-cache clear + HitPoints fix"),
  ("split-stack", "Peel N off a stack and place it", "Thing.SplitOff(int) + GenPlace.TryPlaceThing", "EASY", False, ""),
 ],
 "Map things & buildings": [
  ("spawn-thing", "With stuff and rotation", "ThingMaker.MakeThing(def, stuff) + GenSpawn.Spawn", "EASY", True, "⛔ MakeThing RANDOMISES HitPoints in PostMake - set HP after, not before"),
  ("place-blueprint", "A real build order the colony will execute", "GenConstruct.PlaceBlueprintForBuild(BuildableDef, center, map, rot, faction, stuff)", "MEDIUM", False, ""),
  ("instant-finish-frame", "Complete a construction frame now", "Frame.CompleteConstruction(Pawn worker)", "MEDIUM", False, "⛔ hard-requires a non-null worker Pawn or it NREs"),
  ("minify", "Installed building becomes a carryable", "MinifyUtility.MakeMinified(Thing, DestroyMode) / Uninstall", "EASY", False, ""),
  ("copy/paste a map region", "Lift a rect of things and terrain and stamp it elsewhere", "PrefabUtility.CreatePrefab(CellRect, copyThings, copyTerrain) / SpawnPrefab", "MEDIUM", True, "⛔ CreatePrefab never sets size - unusable until you set it yourself"),
  ("start-fire / make-filth", "Set something alight, or dirty the floor", "FireUtility.TryStartFireIn / FilthMaker.TryMakeFilth", "EASY", True, ""),
  ("power-net query & force-power", "Read a grid's gain and store, or force a building on", "PowerNet.CurrentEnergyGainRate() / CurrentStoredEnergy() / CompPowerTrader.PowerOn", "MEDIUM", False, "⚠️ after a bulk spawn call UpdatePowerNetsAndConnections_First()"),
  ("rebuild-regions-rooms", "Make the map coherent again after bulk edits", "RegionAndRoomUpdater.TryRebuildDirtyRegionsAndRooms()", "MEDIUM", True, "inside map_commit"),
 ],
 "Terrain, roof & grids": [
  ("set-terrain / paint colour", "Change the floor, or just recolour it", "TerrainGrid.SetTerrain(IntVec3, TerrainDef) / SetTerrainColor(cell, ColorDef)", "EASY", True, ""),
  ("foundation & substructure", "Odyssey's under-floor layer", "TerrainGrid.SetFoundation / RemoveFoundation + SubstructureGrid.MarkDirty()", "MEDIUM", True, "⛔ refused SILENTLY on any cell that already has a floor"),
  ("strip-top-layer", "Reveal what is under the floor", "TerrainGrid.RemoveTopLayer(cell, doLeavings)", "EASY", True, ""),
  ("set-roof", "Any RoofDef; None clears it", "RoofGrid.SetRoof(IntVec3, RoofDef)", "EASY", True, ""),
  ("collapse-roof", "Drop it and crush whatever is underneath", "RoofCollapserImmediate.DropRoofInCells(cells, map, out crushed)", "EASY", False, ""),
  ("fog", "Unfog a cell, flood, clear the map, or re-fog a rect", "FogGrid.Unfog / FloodUnfogAdjacent / ClearAllFog / Refog(CellRect)", "EASY", True, ""),
  ("snow / sand depth", "Per-cell depth", "SnowGrid.SetDepth(cell, float) / SandGrid.SetDepth", "EASY", False, "sand is Odyssey"),
  ("room temperature & push-heat", "Warm or chill a room", "Room.Temperature setter / GenTemperature.PushHeat(cell, map, energy)", "MEDIUM", False, "⚠️ EqualizeTemperature drags it back toward ambient"),
 ],
 "Zones, stockpiles, bills & areas": [
  ("create-stockpile / growing zone", "Make a zone from nothing", "new Zone_Stockpile(preset, ZoneManager) + ZoneManager.RegisterZone", "MEDIUM", False, "read-only today via map_zones"),
  ("add/remove zone cells", "Grow or shrink a zone", "Zone.AddCell / RemoveCell + CheckContiguous", "MEDIUM", False, "⛔ AddCell REFUSES SILENTLY - a 6x6 stockpile took 11 of 36 cells"),
  ("set-crop", "What a growing zone plants", "Zone_Growing.SetPlantDefToGrow(ThingDef)", "EASY", False, "also Building_PlantGrower"),
  ("storage priority & filters", "What may be stored and at what priority", "StorageSettings.Priority / ThingFilter.SetAllow / SetDisallowAll", "MEDIUM", False, "⚠️ then Zone_Stockpile.Notify_SettingsChanged()"),
  ("add-production-bill", "Put a recipe on a workbench", "new Bill_Production(RecipeDef, Precept_ThingStyle) + BillStack.AddBill", "MEDIUM", False, "the whole production loop is unreachable today"),
  ("configure-bill", "Repeat mode, counts, store mode, quality band", "Bill_Production.repeatMode / .targetCount / SetStoreMode / .qualityRange", "EASY", False, ""),
  ("new-allowed-area", "Create a named allowed area", "AreaManager.TryMakeNewAllowed(out Area_Allowed)", "EASY", False, "⚠️ the OLD roster calls this absent - it exists at Verse/AreaManager.cs:147"),
  ("home / roof / no-roof / snow areas", "Paint the standard areas", "AreaManager.Home[cell] / .BuildRoof / .NoRoof / .SnowOrSandClear / Area.Clear()", "EASY", False, ""),
 ],
 "Jobs, work & schedules": [
  ("force-job", "Start any JobDef right now", "JobMaker.MakeJob(def, target) + Pawn_JobTracker.StartJob", "MEDIUM", False, "⚠️ jawa/order_pawn is Goto-only today"),
  ("ordered-job", "The player-order path, which pawns respect properly", "Pawn_JobTracker.TryTakeOrderedJob(Job, JobTag?, requestQueueing)", "EASY", False, "refuses if IsCurrentJobPlayerInterruptible() is false"),
  ("prioritized-work", "The right-click prioritize order, WorkGiver and cell included", "TryTakeOrderedJobPrioritizedWork(Job, WorkGiver, IntVec3)", "MEDIUM", False, ""),
  ("stop / clear queue", "Cancel what a pawn is doing", "Pawn_JobTracker.StopAll / EndCurrentJob(JobCondition) / ClearQueuedJobs", "EASY", False, ""),
  ("set-work-priority", "The work tab, per pawn per type", "Pawn_WorkSettings.SetPriority(WorkTypeDef, int)", "EASY", False, "⚠️ getter returns 3 for everything when useWorkPriorities is off"),
  ("draft / fire-at-will", "Draft a pawn and set its fire policy", "Pawn_DraftController.Drafted / .FireAtWill", "EASY", False, "refusal is reported by Lord.AllowsDrafting(pawn)"),
  ("timetable", "One of the 24 hourly slots", "Pawn_TimetableTracker.SetAssignment(hour, TimeAssignmentDef)", "EASY", False, "⛔ ignored outright for non-colonists"),
  ("player settings", "Allowed area, master, medical care, hostility response", "Pawn_PlayerSettings.AreaRestrictionInPawnCurrentMap / .Master / .medCare", "EASY", False, ""),
 ],
 "Lords, raids & AI groups": [
  ("settle-pawns-forever", "A group that lives, works and defends a radius", "LordMaker.MakeNewLord(faction, new LordJob_DefendPoint(...), map, pawns)", "MEDIUM", False, "⛔ NEVER LordJob_DefendBase - it self-converts into a raid"),
  ("assault-lord", "A live attacking group", "LordMaker.MakeNewLord(faction, new LordJob_AssaultColony(...), map, pawns)", "MEDIUM", False, ""),
  ("attach / detach pawn", "Move a pawn in or out of a lord", "Lord.AddPawn(Pawn) / RemovePawn", "EASY", False, "gate on Lord.CanAddPawn(p)"),
  ("poke-lord", "Advance the state machine the way vanilla scripts do", "Lord.ReceiveMemo(string) / Find.SignalManager.SendSignal(new Signal(tag))", "EASY", False, ""),
  ("swap-lordjob / force-toil", "Rewrite what a group is doing mid-flight", "Lord.SetJob(LordJob, loading) then Lord.GotoToil(lord.Graph.StartingToil)", "HARD", False, ""),
  ("generate-raid-group", "The actual pawn list for a faction and point budget", "PawnGroupMakerUtility.GeneratePawns(PawnGroupMakerParms)", "MEDIUM", True, ""),
  ("place-arriving-pawns", "Insert them by arrival mode - drop pod, edge walk-in", "PawnsArrivalModeDef.Worker.Arrive(pawns, IncidentParms)", "MEDIUM", True, ""),
  ("raid-shape flags", "Never-flee, force-one-downed, biocoding, seed", "IncidentParms.raidNeverFleeIndividual / .raidForceOneDowned / .pawnGroupMakerSeed", "EASY", False, ""),
  ("pawn_set_duty alone", "Set a duty with no lord behind it", "ThinkNode_ConditionalHasLordDuty", "EASY", False, "⛔ DO NOT BUILD - returns false with no lord, so the duty never runs"),
 ],
 "Factions & relations": [
  ("nudge-goodwill", "The canonical path, letters and all", "Faction.TryAffectGoodwillWith(other, int, ...)", "EASY", True, "refuses on permanentEnemy / defeated / quest-locked"),
  ("pre-flight the refusal", "So a caller reports it instead of silently no-oping", "Faction.CanChangeGoodwillFor(Faction, int)", "EASY", False, ""),
  ("force-relation-kind", "Bypass the goodwill arithmetic entirely", "Faction.SetRelationDirect(other, FactionRelationKind, ...)", "EASY", True, ""),
  ("new-leader", "Roll a replacement leader", "Faction.TryGenerateNewLeader(); Faction.leader is a settable field", "MEDIUM", True, "read-only today (faction_leader_get)"),
  ("create-faction-live", "A whole new faction with relations and a settlement", "FactionGenerator.NewGeneratedFactionWithRelations + FactionManager.Add", "HARD", True, ""),
  ("hidden / defeated / temporary flags", "Take a faction off the board without deleting it", "Faction.hidden / .defeated / .temporary", "EASY", False, ""),
  ("enumerate & pick", "List factions, or pick a raidable enemy", "FactionManager.GetFactions(...) / .RandomRaidableEnemyFaction", "EASY", True, ""),
 ],
 "World map & tiles": [
  ("set-biome / scalars", "Biome, elevation, hilliness, rainfall, swampiness, pollution", "Tile.PrimaryBiome setter + .elevation / .hilliness / .rainfall", "EASY", True, "⛔ HillinessLabel, MinTemperature and Biomes CACHE with no reset - read raw fields"),
  ("tile temperature", "Per-tile temperature", "Tile.temperature + TileTemperaturesComp.ClearCaches()", "MEDIUM", True, ""),
  ("tile mutators", "Add or remove a tile mutator", "Tile.AddMutator(TileMutatorDef) / RemoveMutator", "EASY", True, "refuses on a same-category priority conflict"),
  ("landmarks", "Place a named landmark on a tile", "WorldLandmarks.AddLandmark(LandmarkDef, tile, layer, forced)", "EASY", True, "⛔ never checks IsValidTile; Odyssey-gated"),
  ("roads & rivers", "Overlay a road or river between tiles", "WorldGrid.OverlayRoad(from, to, RoadDef) / OverlayRiver", "MEDIUM", True, "⛔ removal unsupported; a lower-priority def is refused silently"),
  ("named regions", "The planet's named features", "WorldFeature + Tile.feature", "HARD", True, "⚠️ needs Find.WorldFeatures.textsCreated = false"),
  ("world info", "Planet name, seed, population, landmark density", "World.info", "EASY", True, "⛔ overallPopulation and landmarkDensity are NOT scribed - they revert on load"),
  ("redraw the planet", "Nothing you changed is visible without it", "Find.World.renderer.SetAllLayersDirty()", "EASY", True, "RimWorld has no per-tile invalidation except pollution"),
 ],
 "Settlements, caravans & gravship": [
  ("found-player-colony", "Put a player settlement on a tile", "SettleUtility.AddNewHome(PlanetTile, Faction)", "EASY", False, "does not generate a map"),
  ("spawn-any-world-object", "Any WorldObjectDef anywhere", "WorldObjectMaker.MakeWorldObject(def) + Find.WorldObjects.Add", "EASY", True, "⛔ a Settlement with a null faction is DESTROYED on load"),
  ("generate-a-map-for-a-tile", "Make the map a tile would produce", "GetOrGenerateMapUtility.GetOrGenerateMap(tile, size, suggestedMapParentDef)", "MEDIUM", False, ""),
  ("abandon / defeat", "Remove a settlement or a map", "SettlementAbandonUtility.TryAbandonViaInterface / Game.DeinitAndRemoveMap", "MEDIUM", False, ""),
  ("make & move a caravan", "Create one and send it somewhere", "CaravanMaker.MakeCaravan(...) + Caravan_PathFollower.StartPath(...)", "EASY", False, "the whole caravan domain is absent today"),
  ("form caravan off a map", "The real leave-the-map path", "CaravanFormingUtility.FormAndCreateCaravan(pawns, faction, exitTile, dirTile, destTile)", "MEDIUM", False, ""),
  ("attack a settlement", "Send a caravan in", "SettlementUtility.Attack(Caravan, Settlement)", "EASY", False, "applies the goodwill hit itself"),
  ("gravship launch & travel", "Lift, fly, land", "GravshipUtility.GenerateGravship -> TravelTo -> ArriveNewMap / AbandonMap", "HARD", False, "fuel via TryGetPathFuelCost"),
 ],
 "Weather, temperature & conditions": [
  ("set-weather-now", "Change the weather this instant", "WeatherManager.TransitionTo(WeatherDef)", "EASY", True, "⚠️ overridden next tick if a GameCondition_ForceWeather disagrees"),
  ("roll-next-weather naturally", "Let the game pick, now", "WeatherDecider.StartNextWeather()", "EASY", False, ""),
  ("lock-weather", "Hold weather against the decider", "GameConditionMaker.MakeCondition(GameCondition_ForceWeather, duration) + RegisterCondition", "MEDIUM", False, ""),
  ("suppress-rain", "No rain for N ticks", "WeatherDecider.DisableRainFor(int ticks)", "EASY", False, ""),
  ("add / end a game condition", "Map-scoped or world-scoped", "GameConditionMaker.MakeCondition(def, duration) + RegisterCondition / GetActiveCondition(def).End()", "EASY", True, ""),
  ("force sky glow / brightness", "Darken or brighten the sky", "SkyManager.ForceSetCurSkyGlow(float) / GameConditionManager.SetTargetBrightness", "EASY", False, "glow is advisory - recomputed next frame"),
  ("read effective temperature", "What a cell actually is", "GenTemperature.TryGetTemperatureForCell(cell, map, out float)", "EASY", False, "MapTemperature.OutdoorTemp is computed, not settable"),
 ],
 "Storyteller, incidents & quests": [
  ("fire-incident-now", "Any IncidentDef immediately", "IncidentDef.Worker.TryExecute(IncidentParms)", "EASY", True, "⛔ CanFireNow carries pacing TryExecute never consults - false does NOT block a raid"),
  ("fire-through-storyteller", "So it is recorded in adaptation state", "Storyteller.TryFire(new FiringIncident(def, comp, parms))", "MEDIUM", False, ""),
  ("build valid parms", "The points and target an incident needs", "StorytellerUtility.DefaultParmsNow / DefaultThreatPointsNow", "EASY", False, ""),
  ("schedule for a future tick", "Queue an incident ahead of time", "Storyteller.incidentQueue.Add(def, fireTick, parms, retryDurationTicks)", "EASY", False, ""),
  ("swap storyteller live", "Change who is running the game", "Current.Game.storyteller.def then Storyteller.Notify_DefChanged()", "MEDIUM", False, "read-only today"),
  ("tune difficulty", "Threat scale, big threats, adaptation", "Storyteller.difficulty.threatScale / .allowBigThreats / .adaptationEffectFactor", "EASY", False, ""),
  ("generate & surface a quest", "Make one available with its letter", "QuestUtility.GenerateQuestAndMakeAvailable(QuestScriptDef, points) + SendLetterQuestAvailable", "EASY", True, ""),
  ("accept / end a quest", "Drive a quest to an outcome", "Quest.Accept(Pawn) / Quest.End(QuestEndOutcome, sendLetter, playSound)", "MEDIUM", False, ""),
  ("drive quest parts by signal", "The way quests actually talk to each other", "Find.SignalManager.SendSignal(new Signal(tag, args))", "EASY", False, ""),
  ("recount wealth", "The number every threat budget is computed from", "WealthWatcher.ForceRecount(bool)", "MEDIUM", False, ""),
 ],
 "Research & technology": [
  ("finish-project", "Complete it with prerequisites, techprints and unlocks", "ResearchManager.FinishProject(proj, doDialog, researcher, doLetter)", "EASY", False, "the whole research domain is absent today"),
  ("add-progress / set-current", "Partial progress, or pick what is being researched", "ResearchManager.AddProgress / SetCurrentProject / StopProject", "EASY", False, ""),
  ("grant-techprints", "Satisfy the techprint gate", "ResearchManager.AddTechprints(proj, amount)", "EASY", False, "gate is ResearchProjectDef.TechprintRequirementMet"),
  ("finish-everything / reset-all", "Blunt instruments for a test start", "DebugSetAllProjectsFinished() / ResetAllProgress()", "EASY", False, ""),
  ("reapply-unlocks", "REQUIRED after any direct progress edit", "ResearchManager.ReapplyAllMods()", "EASY", False, ""),
  ("anomaly knowledge", "The Anomaly research currency", "ResearchManager.ApplyKnowledge(KnowledgeCategoryDef, amount)", "MEDIUM", False, "Anomaly-gated"),
  ("availability probe", "Can this be started, and why not", "ResearchProjectDef.CanStartNow / .PrerequisitesCompleted / .PlayerHasAnyAppropriateResearchBench", "EASY", False, ""),
 ],
 "Ideology, precepts & rituals": [
  ("create & register an ideo", "A whole new religion at runtime", "IdeoGenerator.GenerateIdeo(IdeoGenerationParms) + Find.IdeoManager.Add(ideo)", "MEDIUM", False, ""),
  ("convert a pawn", "Move someone to another ideo", "Pawn_IdeoTracker.SetIdeo(Ideo)", "EASY", True, "⛔ silently refuses for babies; resets certainty and unclaims beds"),
  ("set a faction's primary ideo", "What the faction believes", "faction.ideos.SetPrimary(Ideo)", "EASY", False, ""),
  ("add / remove a precept", "Change what an ideo demands", "PreceptMaker.MakePrecept(PreceptDef) + Ideo.AddPrecept(p, init:true, ..., fillWith:RitualPatternDef)", "MEDIUM", False, "refusal comes from IdeoFoundation.CanAdd"),
  ("assign an ideo role", "Make someone the Moral Guide", "Precept_Role.Assign(Pawn, addThoughts) / Unassign", "EASY", False, ""),
  ("start a ritual for real", "Not a stub - the actual ceremony", "RitualBehaviorWorker.TryExecuteOn(target, organizer, ritual, obligation, assignments, playerForced)", "HARD", True, "needs Dialog_BeginRitual.CreateRitualRoleAssignments first"),
  ("queue a ritual obligation", "Make the colony owe a ritual", "Precept_Ritual.AddObligation(new RitualObligation(ritual, expires))", "MEDIUM", False, ""),
  ("development points", "Drive an ideo toward reform", "IdeoDevelopmentTracker.TryAddDevelopmentPoints(int) / Notify_Reformed()", "EASY", False, ""),
  ("styles & icon", "How the ideo looks", "Ideo.thingStyleCategories / Ideo.SetIcon(IdeoIconDef, ColorDef, ...)", "MEDIUM", False, ""),
 ],
 "Animals & training": [
  ("set-training-step", "Tameness, Obedience, Release, Rescue", "Pawn_TrainingTracker.Train(TrainableDef, trainer, complete:true)", "EASY", False, "the whole animal domain is absent today"),
  ("toggle wanted training", "Including prerequisites", "Pawn_TrainingTracker.SetWantedRecursive(TrainableDef, bool)", "EASY", False, ""),
  ("instant tame / recruit", "No roll", "InteractionWorker_RecruitAttempt.DoRecruit / RecruitUtility.Recruit(Pawn, Faction, Pawn)", "EASY", False, ""),
  ("set master", "Who the animal follows", "Pawn_PlayerSettings.Master + animalsReleased", "MEDIUM", False, "validate TrainableUtility.CanBeMaster"),
  ("force a bond", "Make a pawn and an animal bonded", "RelationsUtility.TryDevelopBondRelation(p1, p2, 1f)", "EASY", False, ""),
  ("manhunter pack", "Points-appropriate kind and count", "AggressiveAnimalIncidentUtility.TryFindAggressiveAnimalKind + GetAnimalsCount", "MEDIUM", False, ""),
  ("force an egg / top up milk", "Produce now", "CompEggLayer.ProduceEgg() / Fertilize(Pawn)", "MEDIUM", False, "⚠️ CompHasGatherableBodyResource.fullness is protected - needs reflection"),
 ],
 "Anomaly & entities (DLC)": [
  ("set monolith level", "Advance or reset the Anomaly spine", "Find.Anomaly.SetLevel(MonolithLevelDef, silent)", "MEDIUM", False, "fires MonolithLevelChanged and Notify_MonolithLevelChanged"),
  ("read monolith state", "Where the run is in the Anomaly arc", "GameComponent_Anomaly.LevelDef / .NextLevelDef / .HighestLevelReached / .AmbientHorrorMode", "EASY", False, ""),
  ("discover a codex entry", "Mark an entity known", "EntityCodex.SetDiscovered(EntityCodexEntryDef, ThingDef, Thing)", "EASY", False, ""),
  ("containment / study state", "Hold and study an entity", "CompHoldingPlatformTarget / CompStudiable", "MEDIUM", False, "gated by minMonolithLevelForStudy"),
  ("void awakening scripting", "Drive the endgame", "VoidAwakeningUtility + QuestScriptDefOf roots", "HARD", False, ""),
  ("ModsConfig.AnomalyActive guard", "Every row above needs it", "ModsConfig.AnomalyActive", "EASY", False, "⚠️ without the guard these no-op or throw"),
 ],
 "Time, ticks & speed": [
  ("step exactly N ticks while paused", "Deterministic advance", "TickManager.DoSingleTick()", "EASY", True, "bridge rimworld/step_game_ticks"),
  ("set speed / pause", "Play, fast, superfast, pause", "TickManager.CurTimeSpeed / Pause() / TogglePaused()", "EASY", True, "⛔ verify by reading ticksGame TWICE - success:true is not proof time stopped"),
  ("read the clock", "Game ticks, absolute ticks, ticks since settle", "TickManager.TicksGame / .TicksAbs / .TicksSinceSettle / .StartingYear", "EASY", False, ""),
  ("jump the clock without simulating", "Skip time with no events", "TickManager.DebugSetTicksGame(int)", "EASY", False, ""),
  ("date readout at a map's lat/long", "Human-readable date and season", "GenDate.DateFullStringAt(long, Vector2) / .Quadrum / .Season", "EASY", False, ""),
  ("pin normal speed", "The way combat forces it", "Find.TickManager.slower.SignalForceNormalSpeed()", "EASY", False, ""),
  ("tick perf counters", "Is the game actually keeping up", "TickManager.MeanTickTime / .TicksThisFrame / .TickRateMultiplier", "EASY", False, ""),
 ],
 "Save/load & scribe": [
  ("save now, named", "Write a save under a chosen name", "GameDataSaveLoader.SaveGame(string fileName)", "EASY", True, "saveName is honoured"),
  ("autosave now", "Trigger the autosaver", "Find.Autosaver.DoAutosave()", "EASY", False, ""),
  ("load a save", "Bring a save up", "GameDataSaveLoader.LoadGame(string)", "MEDIUM", True, "⚠️ goes through QueueLongEvent - completes a LATER frame, not in the caller"),
  ("mod-list match check", "Does this save match the running mods", "ScribeMetaHeaderUtility.LoadedModsMatchesActiveMods(out string, out string)", "EASY", False, ""),
  ("list saves with version", "What is on disk and what built it", "SaveFileInfo.LoadData() + ScribeMetaHeaderUtility.GameVersionOf(FileInfo)", "MEDIUM", True, ""),
  ("drop one map without quitting", "Free a map mid-session", "Game.DeinitAndRemoveMap(Map, notifyPlayer)", "MEDIUM", False, ""),
  ("export / import side artifacts", "Scenario, ideo (.rid), xenotype (.xtp)", "GameDataSaveLoader.SaveScenario / SaveIdeo / SaveXenotype / TryLoadIdeo / TryLoadXenotype", "MEDIUM", False, ""),
  ("ClearAllMapsAndWorld", "Tear the game down to nothing", "MemoryUtility.ClearAllMapsAndWorld()", "HARD", False, "⛔ leaves the process in a null-field state until a new Game is installed"),
 ],
 "Rendering, camera & screenshots": [
  ("jump / pan camera", "Point the camera at something", "CameraDriver.JumpToCurrentMapLoc(IntVec3) / PanToMapLocAndSize", "EASY", True, "bridge jump_camera_to_cell"),
  ("set zoom", "How close the camera sits", "CameraDriver.SetRootSize(float) / .RootSize / .CurrentViewRect", "EASY", True, "⚠️ desiredSize itself is private"),
  ("screenshot", "Capture the screen to a file", "ScreenshotTaker.TakeNonSteamShot(fileName) / QueueSilentScreenshot()", "MEDIUM", True, "⚠️ the file lands at the end of the NEXT frame - poll for it. Call jawa/clear_ui first"),
  ("rebuild map mesh", "Make map edits visible", "MapDrawer.RegenerateEverythingNow() / MapMeshDirty(cell, flags) / RegenerateLayerNow(Type)", "MEDIUM", True, "data half proven, visible half unproven"),
  ("pawn portrait to a RenderTexture", "Render a pawn off-screen", "PortraitsCache.Get(Pawn, size, rot, ...) / SetDirty(Pawn)", "MEDIUM", False, ""),
  ("pawn atlas refresh / dump", "Force pawn art to redraw, or dump the atlas", "GlobalTextureAtlasManager.TryMarkPawnFrameSetDirty(Pawn) / DumpPawnAtlases(folder)", "MEDIUM", False, ""),
  ("world layer redraw", "Make planet edits visible", "WorldRenderer.SetAllLayersDirty() / RegenerateAllLayersNow()", "HARD", True, ""),
  ("anything touching Find.UIRoot", "Read or drive the UI tree directly", "Find.UIRoot", "HARD", False, "⛔ OnGUI-scoped - THROWS outside an IMGUI frame. Main-thread and in-frame only"),
 ],
 "Diagnostics, logging & defs": [
  ("write / read / clear the log", "Talk to Player.log and read it back", "Log.Message / Log.Messages / Log.Clear() / Log.LockMessages()", "EASY", True, ""),
  ("enumerate defs", "Every def of a type", "DefDatabase<T>.AllDefsListForReading / .DefCount", "EASY", True, "a string-typed caller needs MakeGenericType"),
  ("resolve one def safely", "Look one up without throwing", "DefDatabase<T>.GetNamedSilentFail(string)", "EASY", True, ""),
  ("mod inventory", "Which mods are running, with packageIds and assemblies", "LoadedModManager.RunningModsListForReading", "EASY", False, ""),
  ("stat query + full explanation", "The number AND why it is that number", "StatExtension.GetStatValue(Thing, StatDef) / StatWorker.GetExplanationFull", "MEDIUM", False, ""),
  ("stat cache bust", "Required after quality or stuff edits", "StatWorker.ClearCacheForThing(Thing) / DeleteStatCache()", "EASY", False, ""),
  ("prefs", "Dev mode, verbose logging, autosave interval, pause-on-load", "Prefs.DevMode ... then Prefs.Save()", "EASY", False, "⚠️ Prefs.xml is rewritten from memory on exit"),
  ("player-facing output", "Put a message or letter on his screen", "Messages.Message(...) / Find.LetterStack.ReceiveLetter(...)", "EASY", True, ""),
  ("inspect-string of any thing", "What the inspect pane would say", "Thing.GetInspectString()", "EASY", True, ""),
 ],
}

# 🔴 THE TEN DOMAINS WITH NO TOOL ON EITHER SIDE, measured 2026-08-23 by a name scan of
# all 246 tool names plus a targeted API grep that returned ZERO hits in the companion
# source. These are capability GAPS, not missing functions, and they are why the roster
# is worth culling rather than skimming.
GAPS = [
 ("Research", "ResearchManager", "unlock, complete or query a project"),
 ("Work priorities & timetables", "workSettings", "set_draft is the entire work surface"),
 ("Bills & production", "BillStack", "cannot put a recipe on a workbench - the whole production loop"),
 ("Caravans, trade & world travel", "Caravan / TradeDeal", "we author the planet, never anything moving on it"),
 ("Animals & training", "TrainableDef", "animals are only generic pawns"),
 ("Power & temperature networks", "CompPower", "no grid, no battery, no room temperature"),
 ("Royalty & Anomaly DLCs", "RoyalTitle / Entity", "zero surface; Ideology IS covered, these two are not"),
 ("Prisoners, slaves & guests", "Guest", "no interaction mode, recruitment or conversion"),
 ("History, records & wealth", "WealthWatcher", "nothing can score a run"),
 ("Storyteller & difficulty", "StorytellerDef", "can fire incidents, cannot swap the storyteller"),
]
