# BRIDGE_TOOLS_MEDIUM_BLOCK_1 — the 41 MEDIUM capabilities, split into four workloads

Derived 2026-08-26 from `design/Jawa/bridge/capability_roster_data.py` and
`dll_capability_roster.decisions.json`: every MEDIUM row the roster marks not-built and
that the owner did not strike. The cull's posture is DEFAULT INCLUDE.

⚠️ **The roster's own `built` flag is STALE and `ROSTER_VS_BUILT_2026-08-26.md` says so.**
198 tools exist today. Before writing anything, check the live list and SKIP a row that is
already covered, reporting which tool covers it:

```
grep -rho '"jawa/[a-z_]*"' src/RimMandrake/bridgetools/JawaBench.BridgeTools --include=*.cs | sort -u
```

⛔ The companion is ONE `sealed partial class` across many files. Each group creates its OWN
new file, named below, and edits nothing else — that is what lets four run at once.

Build with `python.exe src/RimMandrake/bridgetools/build.py --gm` (Windows python).
`--gm` is NOT optional: without it the plan drops the player-acting tools.


## Group H — JawaBenchZoneTools.cs — 9 tools

- **create-stockpile / growing zone** — Zones, stockpiles, bills & areas
  - api: `new Zone_Stockpile(preset, ZoneManager) + ZoneManager.RegisterZone`
  - effect: Make a zone from nothing
  - ⚠️ read-only today via map_zones
- **add/remove zone cells** — Zones, stockpiles, bills & areas
  - api: `Zone.AddCell / RemoveCell + CheckContiguous`
  - effect: Grow or shrink a zone
  - ⚠️ ⛔ AddCell REFUSES SILENTLY - a 6x6 stockpile took 11 of 36 cells
- **storage priority & filters** — Zones, stockpiles, bills & areas
  - api: `StorageSettings.Priority / ThingFilter.SetAllow / SetDisallowAll`
  - effect: What may be stored and at what priority
  - ⚠️ ⚠️ then Zone_Stockpile.Notify_SettingsChanged()
- **add-production-bill** — Zones, stockpiles, bills & areas
  - api: `new Bill_Production(RecipeDef, Precept_ThingStyle) + BillStack.AddBill`
  - effect: Put a recipe on a workbench
  - ⚠️ the whole production loop is unreachable today
- **force-job** — Jobs, work & schedules
  - api: `JobMaker.MakeJob(def, target) + Pawn_JobTracker.StartJob`
  - effect: Start any JobDef right now
  - ⚠️ ⚠️ jawa/order_pawn is Goto-only today
- **prioritized-work** — Jobs, work & schedules
  - api: `TryTakeOrderedJobPrioritizedWork(Job, WorkGiver, IntVec3)`
  - effect: The right-click prioritize order, WorkGiver and cell included
- **anomaly knowledge** — Research & technology
  - api: `ResearchManager.ApplyKnowledge(KnowledgeCategoryDef, amount)`
  - effect: The Anomaly research currency
  - ⚠️ Anomaly-gated
- **royal-title & favor** — Skills, traits, relations & backstory
  - api: `Pawn_RoyaltyTracker.SetTitle / SetFavor / GainFavor`
  - effect: Grant or revoke a title, set honor
  - ⚠️ Royalty-gated
- **set-stuff retroactively** — Apparel, equipment & inventory
  - api: `Thing.SetStuffDirect(ThingDef)`
  - effect: Change what an existing item is made of
  - ⚠️ + stat-cache clear + HitPoints fix


## Group I — JawaBenchIncidentTools.cs — 9 tools

- **fire-through-storyteller** — Storyteller, incidents & quests
  - api: `Storyteller.TryFire(new FiringIncident(def, comp, parms))`
  - effect: So it is recorded in adaptation state
- **swap storyteller live** — Storyteller, incidents & quests
  - api: `Current.Game.storyteller.def then Storyteller.Notify_DefChanged()`
  - effect: Change who is running the game
  - ⚠️ read-only today
- **accept / end a quest** — Storyteller, incidents & quests
  - api: `Quest.Accept(Pawn) / Quest.End(QuestEndOutcome, sendLetter, playSound)`
  - effect: Drive a quest to an outcome
- **recount wealth** — Storyteller, incidents & quests
  - api: `WealthWatcher.ForceRecount(bool)`
  - effect: The number every threat budget is computed from
- **settle-pawns-forever** — Lords, raids & AI groups
  - api: `LordMaker.MakeNewLord(faction, new LordJob_DefendPoint(...), map, pawns)`
  - effect: A group that lives, works and defends a radius
  - ⚠️ ⛔ NEVER LordJob_DefendBase - it self-converts into a raid
- **assault-lord** — Lords, raids & AI groups
  - api: `LordMaker.MakeNewLord(faction, new LordJob_AssaultColony(...), map, pawns)`
  - effect: A live attacking group
- **set master** — Animals & training
  - api: `Pawn_PlayerSettings.Master + animalsReleased`
  - effect: Who the animal follows
  - ⚠️ validate TrainableUtility.CanBeMaster
- **manhunter pack** — Animals & training
  - api: `AggressiveAnimalIncidentUtility.TryFindAggressiveAnimalKind + GetAnimalsCount`
  - effect: Points-appropriate kind and count
- **force an egg / top up milk** — Animals & training
  - api: `CompEggLayer.ProduceEgg() / Fertilize(Pawn)`
  - effect: Produce now
  - ⚠️ ⚠️ CompHasGatherableBodyResource.fullness is protected - needs reflection


## Group J — JawaBenchSocietyTools.cs — 11 tools

- **create & register an ideo** — Ideology, precepts & rituals
  - api: `IdeoGenerator.GenerateIdeo(IdeoGenerationParms) + Find.IdeoManager.Add(ideo)`
  - effect: A whole new religion at runtime
- **add / remove a precept** — Ideology, precepts & rituals
  - api: `PreceptMaker.MakePrecept(PreceptDef) + Ideo.AddPrecept(p, init:true, ..., fillWith:RitualPatternDef)`
  - effect: Change what an ideo demands
  - ⚠️ refusal comes from IdeoFoundation.CanAdd
- **queue a ritual obligation** — Ideology, precepts & rituals
  - api: `Precept_Ritual.AddObligation(new RitualObligation(ritual, expires))`
  - effect: Make the colony owe a ritual
- **styles & icon** — Ideology, precepts & rituals
  - api: `Ideo.thingStyleCategories / Ideo.SetIcon(IdeoIconDef, ColorDef, ...)`
  - effect: How the ideo looks
- **generate-a-map-for-a-tile** — Settlements, caravans & gravship
  - api: `GetOrGenerateMapUtility.GetOrGenerateMap(tile, size, suggestedMapParentDef)`
  - effect: Make the map a tile would produce
- **abandon / defeat** — Settlements, caravans & gravship
  - api: `SettlementAbandonUtility.TryAbandonViaInterface / Game.DeinitAndRemoveMap`
  - effect: Remove a settlement or a map
- **form caravan off a map** — Settlements, caravans & gravship
  - api: `CaravanFormingUtility.FormAndCreateCaravan(pawns, faction, exitTile, dirTile, destTile)`
  - effect: The real leave-the-map path
- **reimplant-xenogerm** — Genes & xenotypes
  - api: `GeneUtility.ReimplantXenogerm(caster, recipient)`
  - effect: Copy one pawn's xenogenes onto another
  - ⚠️ pre-check PawnWouldDieFromReimplanting
- **generate-random-geneset** — Genes & xenotypes
  - api: `GeneUtility.GenerateGeneSet(int? seed)`
  - effect: Seeded gene set plus auto-named xenotype, for fuzzing
- **set-severity** — Pawn state & health
  - api: `HealthUtility.AdjustSeverity`
  - effect: Force a condition's severity up or down
  - ⚠️ ⚠️ needs CheckForStateChange afterwards or down/death is not re-evaluated
- **install-bionic** — Pawn state & health
  - api: `Recipe_InstallArtificialBodyPart.ApplyOnPawn`
  - effect: The full surgery path; cheap route is RestorePart + AddHediff


## Group K — JawaBenchRenderTools.cs — 12 tools

- **place-blueprint** — Map things & buildings
  - api: `GenConstruct.PlaceBlueprintForBuild(BuildableDef, center, map, rot, faction, stuff)`
  - effect: A real build order the colony will execute
- **instant-finish-frame** — Map things & buildings
  - api: `Frame.CompleteConstruction(Pawn worker)`
  - effect: Complete a construction frame now
  - ⚠️ ⛔ hard-requires a non-null worker Pawn or it NREs
- **power-net query & force-power** — Map things & buildings
  - api: `PowerNet.CurrentEnergyGainRate() / CurrentStoredEnergy() / CompPowerTrader.PowerOn`
  - effect: Read a grid's gain and store, or force a building on
  - ⚠️ ⚠️ after a bulk spawn call UpdatePowerNetsAndConnections_First()
- **set monolith level** — Anomaly & entities (DLC)
  - api: `Find.Anomaly.SetLevel(MonolithLevelDef, silent)`
  - effect: Advance or reset the Anomaly spine
  - ⚠️ fires MonolithLevelChanged and Notify_MonolithLevelChanged
- **containment / study state** — Anomaly & entities (DLC)
  - api: `CompHoldingPlatformTarget / CompStudiable`
  - effect: Hold and study an entity
  - ⚠️ gated by minMonolithLevelForStudy
- **drop one map without quitting** — Save/load & scribe
  - api: `Game.DeinitAndRemoveMap(Map, notifyPlayer)`
  - effect: Free a map mid-session
- **export / import side artifacts** — Save/load & scribe
  - api: `GameDataSaveLoader.SaveScenario / SaveIdeo / SaveXenotype / TryLoadIdeo / TryLoadXenotype`
  - effect: Scenario, ideo (.rid), xenotype (.xtp)
- **pawn portrait to a RenderTexture** — Rendering, camera & screenshots
  - api: `PortraitsCache.Get(Pawn, size, rot, ...) / SetDirty(Pawn)`
  - effect: Render a pawn off-screen
- **pawn atlas refresh / dump** — Rendering, camera & screenshots
  - api: `GlobalTextureAtlasManager.TryMarkPawnFrameSetDirty(Pawn) / DumpPawnAtlases(folder)`
  - effect: Force pawn art to redraw, or dump the atlas
- **room temperature & push-heat** — Terrain, roof & grids
  - api: `Room.Temperature setter / GenTemperature.PushHeat(cell, map, energy)`
  - effect: Warm or chill a room
  - ⚠️ ⚠️ EqualizeTemperature drags it back toward ambient
- **lock-weather** — Weather, temperature & conditions
  - api: `GameConditionMaker.MakeCondition(GameCondition_ForceWeather, duration) + RegisterCondition`
  - effect: Hold weather against the decider
- **stat query + full explanation** — Diagnostics, logging & defs
  - api: `StatExtension.GetStatValue(Thing, StatDef) / StatWorker.GetExplanationFull`
  - effect: The number AND why it is that number


**41 rows total.** Declared `[Tool]` count today: 198.
