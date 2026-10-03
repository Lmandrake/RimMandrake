# STILLSAND_EVENT_CREATURES_REMAINDER_1 work log (2026-10-03)

## What already exists (searched src/, design, artpipe-irrelevant: no art owed except below)
- Incident workers: RM_IncidentWorker_SandLeviathan (RM_SandLeviathan.cs; RUT_KraytAttack in UtinniPatches is XML-only), RM_DuneGale, RM_SandBusterEruption, RM_HorizonWarning.
- Cave tier rows: RSW_PreciousCave_SarlaccSeep (Sarlacc/Defs/MapGeneration, brine pool + RSW_DeepDesertSeep marker), RSW_PreciousCave_KraytDen (SWBestiary; 25% a live RSW_GreaterKraytDragon, else skull+pearl), RM_CaveTierElements.cs.
- Sarlacc swimmer road (Long Shade): RSW_SwimmerRoad.cs / CompSarlaccSwimmer (roots on RSW_DeepDesertSeep within 4 cells by chance, or on reserve exhaustion).
- Krayt lens patch RM_KraytLens.xml; RSW_PreciousCave rows; RM_MapComponent_PreciousCave records rowDefName + caveCells.
- ALREADY DONE (spec lines stale): item 4 Debt weighting -> RM_SandLeviathan.ChanceFactorNow calls RM_StillsandWater.IncidentChanceFactor -> RM_WaterLedger.IncidentFactor; RUT_TheReturn.xml weightedIncidents lists RUT_KraytAttack/RM_MuurrokEmergence/RM_SandBusterEruption; a fresh pour is a draw in LoudestCell. Item 5 corpses->skeletons: RM_MapComponent_SkeletonRemains + RM_GiantSkeletons_Wiring.xml (muurrok) + SWBestiary/Patches/RSW_GiantSkeletons_Remains.xml (krayt, greater krayt, war wyrm). Not rebuilt.
- NOT existing: any Stillsand seep-root incident, den quest, RSW_KraytHorn, charged thumper / landing ship in LoudestCell.

## Tier decisions
1. Sarlacc roots incident: RSW tier, src/RimStarWars/Sarlacc (sarlacc is canon). Reuses RSW_MapComponent_SwimmerRoad + job giver; adds seepMode, a worker, IncidentDef, toggle. Biome gate is data (RM_Stillsand).
2. Krayt den quest: QuestScriptDef in UtinniPatches (RUT tier: Deep Desert Tribes/Jawa campaign + canon krayt). One generic C# node (RM tier, Stillsand: RM_QuestNode_GetCaveDen + RM_QuestPart_CaveDenCleared) because vanilla has no node that finds a generated cave den.
3. Krayt horn: RSW tier (canon sound/creature) in SWBestiary; C# is generic in Stillsand? DECIDED below as built.
4. Loudest draws (charged thumper, landing ship): RM tier, RM_SandLeviathan.cs.

## Built (offline; no commit, no deploy, no live)
- Sarlacc roots: RSW tier. Sarlacc/Source/RSW_SwimmerRoad.cs (seepMode, RSW_IncidentWorker_SwimmerSeep, RSW_SwimmerSeepLogic), CompSarlaccSwimmer.RootAtSeep, RSW_SarlaccSettings.swimmerSeepEnabled + UI; Defs/IncidentDefs_SwimmerSeep.xml (RSW_SwimmerSeepRoot, biomes=[RM_Stillsand] only). Largest seep = RSW_DeepDesertSeep marker with most RM_WaterBrineShallow cells within 6.9. Needs no Creature Behaviors. Built Sarlacc.dll.
- Horn: item/recipe in SWBestiary (RSW_KraytHorn, RSW_Make_KraytHorn: skull + 20 krayt leather at TableMachining); mechanism generic RM code in Stillsand/Source/RM_EventRemainder.cs (RM_CompUseEffect_Horn, RM_HornExtension). Answer incident named only by UtinniPatches/Patches/RUT_KraytHorn_Answer.xml (RUT_KraytAttack). Settings in RM_StillsandEventsSettings: hornEnabled, hornAnswerChance (15%), denQuestEnabled. Roll is logged ("[Stillsand] krayt horn answer roll ...") and shown in the item's inspect string. Rout = PanicFlee on predators with BodySize <= 3 and hostile Neolithic-tech humanlikes. Art: PLACEHOLDER bantha-horn texture; no krayt-horn art in artpipe state; art owed, not queued.
- Den quest: UtinniPatches/Defs/QuestScriptDefs/RUT_KraytDenQuest.xml (validator 0 errors). Custom nodes RM_QuestNode_GetCaveDen / RM_QuestNode_ClaimCaveDen / RM_QuestPart_CaveDenCleared (generic, Stillsand). Offered only on a map whose cave row is RSW_PreciousCave_KraytDen with the greater krayt alive. Success krayt.Destroyed. Bait/thumper/charges are TEXT only, not enforced. Asker is the nearest settlement (any faction), the tribes/Jawa crew are named in text. Cleared den: comp.denCleared; preservation is gated off while a body-size>=3 wild animal is inside (DenHeld).
- Loud draws: LoudestCell = drill > charged thumper > landed/landing shuttle (RM_LoudDraws.xml patches vanilla Shuttle, ShuttleIncoming) > pour > colonist. Grav ships not scored.
- Items 4 (Debt weighting) and 5 (skeleton landmarks) were ALREADY built; nothing re-done.
- Validation: validation.py chain "remainder" (5 offline PASS checks, 4 live arms UNMEASURED with reasons), settings roundtrips; selftest exits 0 (106 comps).
