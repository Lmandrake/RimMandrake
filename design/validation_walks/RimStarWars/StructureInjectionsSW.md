# StructureInjectionsSW — validation walk
subject: src/RimStarWars/StructureInjectionsSW  (packageId: mandrake.rsw.injections)
deps: mandrake.rm.injections (RimMandrake: Structure Injections) — required, loadAfter it; TileMutatorDefs also carry MayRequire="Ludeon.RimWorld.Odyssey" (Odyssey is already in the minimal list); RSW_MiningSite's two extra extraGenSteps entries carry MayRequire="mandrake.rm.inhabited" (also already in the minimal list)
list: minimal+mandrake.rm.injections
status-hint: SW content for the promise/whisper structure program, riding mandrake.rm.injections' GenStep_RimplacePlan engine — 7 GenStepDefs each replaying one rimplace-exported Templates/*.txt plan, each paired with a TileMutatorDef carrying it in extraGenSteps. None are placed on any live Ash'karr tile yet (deliberate deferral, a live world-tile edit out of scope for this pass).

## must be true
- 7 GenStepDefs exist, each `genStep Class="RimMandrake.StructureInjections.GenStep_RimplacePlan"`, `order` 400, pointing at a distinct Templates/*.txt: RSW_GenStep_MoistureFarm, RSW_GenStep_KraytGraveyard, RSW_GenStep_PodracerWreck, RSW_GenStep_HuntingLodge, RSW_GenStep_BanthaGraveyard, RSW_GenStep_MynockRoost, RSW_GenStep_MiningSite.
- 7 matching TileMutatorDefs exist (MayRequire Ludeon.RimWorld.Odyssey), each carrying the matching GenStepDef defName in extraGenSteps — this is the def-driven "responder" hook (TileMutatorDef.extraGenSteps gets concatenated into the real genstep pipeline by RoofGrid.cs/MapGenerator.cs; no Harmony involved, per the defs' own comments): RSW_MoistureFarm, RSW_KraytGraveyard, RSW_PodracerWreck, RSW_HuntingLodge, RSW_BanthaGraveyard, RSW_MynockRoost, RSW_MiningSite.
- biomeWhitelist is set on 4 of the 7: RSW_MoistureFarm → Desert/ExtremeDesert/AridShrubland; RSW_KraytGraveyard → ExtremeDesert; RSW_PodracerWreck → Desert/ExtremeDesert; RSW_HuntingLodge → AridShrubland/ZBiome_Grasslands. The other 3 (RSW_BanthaGraveyard, RSW_MynockRoost, RSW_MiningSite) deliberately carry none — their roster gating is an arc/territory condition a biomeWhitelist can't encode, per the defs' own comments.
- RSW_MiningSite's extraGenSteps additionally lists `Inhabited_Cast` and `RM_InhabitedStock`, both `MayRequire="mandrake.rm.inhabited"` — cast/stock injection for a tile that also holds a WorldObject_Inhabited place, no-op otherwise.
- Each GenStepDef, run directly, replays its Templates/*.txt plan without throwing and places that template's things — proven per-template below by a defName the plan actually contains (read from the Templates/*.txt files themselves, not guessed).
- None of the 7 TileMutatorDefs are wired onto any actual Ash'karr world tile yet — a check that finds one already placed on the live world would be the surprise, not the expected state.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rsw.injections" and no XML error naming GenStepDefs_MoistureFarm.xml, GenStepDefs_Batch2.xml, GenStepDefs_Batch4.xml, GenStepDefs_MiningSite.xml, TileMutatorDefs_Batch2.xml, TileMutatorDefs_Batch4.xml, or TileMutatorDefs_MiningSite.xml   # load-time
2. [D] jawa/get_def {defType: "GenStepDef", defName: "RSW_GenStep_MoistureFarm"} → genStep class RimMandrake.StructureInjections.GenStep_RimplacePlan, order 400
3. [D] jawa/get_def {defType: "TileMutatorDef", defName: "RSW_MoistureFarm"} → biomeWhitelist = [Desert, ExtremeDesert, AridShrubland]; extraGenSteps = [RSW_GenStep_MoistureFarm]
4. [B] jawa/run_genstep {genStepDef: "RSW_GenStep_MoistureFarm"} on a throwaway quicktest map → expect success=true, threw=null
5. [B] jawa/list_things {defName: "KotOR_MoistureVaporator_big"} on that map → expect ≥1 result (the plan's vaporator ring actually landed)
6. [D] jawa/get_def {defType: "TileMutatorDef", defName: "RSW_KraytGraveyard"} → biomeWhitelist = [ExtremeDesert]; extraGenSteps = [RSW_GenStep_KraytGraveyard]
7. [B] jawa/run_genstep {genStepDef: "RSW_GenStep_KraytGraveyard"} → success=true, threw=null
8. [B] jawa/list_things {defName: "KraytDragonSkull"} → expect ≥1 result
9. [D] jawa/get_def {defType: "TileMutatorDef", defName: "RSW_PodracerWreck"} → biomeWhitelist = [Desert, ExtremeDesert]; extraGenSteps = [RSW_GenStep_PodracerWreck]
10. [B] jawa/run_genstep {genStepDef: "RSW_GenStep_PodracerWreck"} → success=true, threw=null
11. [B] jawa/list_things {defName: "AncientPodCar"} → expect exactly 1 result (the plan places one)
12. [D] jawa/get_def {defType: "TileMutatorDef", defName: "RSW_HuntingLodge"} → biomeWhitelist = [AridShrubland, ZBiome_Grasslands]; extraGenSteps = [RSW_GenStep_HuntingLodge]
13. [B] jawa/run_genstep {genStepDef: "RSW_GenStep_HuntingLodge"} → success=true, threw=null
14. [B] jawa/list_things {defName: "LargeFossilTrophy,MediumFossilTrophy"} → expect ≥1 result total
15. [D] jawa/get_def {defType: "TileMutatorDef", defName: "RSW_BanthaGraveyard"} → no biomeWhitelist field set; extraGenSteps = [RSW_GenStep_BanthaGraveyard]
16. [B] jawa/run_genstep {genStepDef: "RSW_GenStep_BanthaGraveyard"} → success=true, threw=null
17. [B] jawa/list_things {defName: "BanthaHorn"} → expect ≥1 result
18. [D] jawa/get_def {defType: "TileMutatorDef", defName: "RSW_MynockRoost"} → no biomeWhitelist field set; extraGenSteps = [RSW_GenStep_MynockRoost]
19. [B] jawa/run_genstep {genStepDef: "RSW_GenStep_MynockRoost"} → success=true, threw=null
20. [B] jawa/list_things {defName: "ChunkSlagSteel,Filth_AnimalFilth"} → expect ≥1 result total
21. [D] jawa/get_def {defType: "TileMutatorDef", defName: "RSW_MiningSite"} → extraGenSteps = [RSW_GenStep_MiningSite, Inhabited_Cast (MayRequire mandrake.rm.inhabited), RM_InhabitedStock (MayRequire mandrake.rm.inhabited)]
22. [B] jawa/run_genstep {genStepDef: "RSW_GenStep_MiningSite"} → success=true, threw=null   # tests the plan replay only; Inhabited_Cast/RM_InhabitedStock only fire when the tile also holds a WorldObject_Inhabited, out of scope for this call
23. [B] jawa/list_things {defName: "VFEPD_AncientEmptyMiningCar"} → expect ≥1 result
X. [S] (human pass) walk each of the 7 replayed templates on the quicktest map and confirm the layout reads as its label (moisture farm, krayt graveyard, podracer wreck, hunting lodge, bantha graveyard, mynock roost, mining site) rather than a debris pile
