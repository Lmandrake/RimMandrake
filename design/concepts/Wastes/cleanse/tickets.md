# Implementation and instrument tickets — proposal only

No ticket is executed in this pass. The builder keeps all code/defs loadable and makes changes in a later authorized build. Each built extra has its own ticket and acceptance witness even if a shared parent gate implements several. A setting is labelled “Next version — unvalidated”, defaults off and survives real settings-file reload. Existing callbacks and cross-layer adapters must be searched again at implementation time; source changes invalidate this census.

Common switch-off protocol: fresh disposable RM_Wastes local map, all DLC and every kept feature on at shipped defaults, shared settings on, next-version extras off; no clock/weather/AI locks. Read state at creation and after an eligible activity window, with real callback boundaries reached. No runtime objects/jobs/letters/incidents/effects of the named extra may appear; the log is clean. Defs and types still resolve. In the on arm enable the target and only its required next-version prerequisites, explicitly listed in the state manifest, construct an eligible state, and read actual behavior rather than a checkbox or def presence. Reload once in each arm. An off transition suspends existing objects readably without deleting them, stock or pawns. This is a scope regression test, not acceptance of a next-version feature as polished gameplay.

## T1: Contaminant-bezoar shearing

**Scope:** Gate availability/progress/collection of its special CompProperties_Shearable resource; keep the species, ordinary diet/taming and ordinary butcher outputs. It is not the milkable bay processor.

**Source and coupling:** src/RimMandrake/Wastes/Defs/ThingDefs_Races/RM_Excretor.xml; src/RimMandrake/Wastes/Defs/ThingDefs_Items/RM_WastesItems.xml Called by: RM_Excretor.xml CompProperties_Shearable -> shear job -> RM_ContaminantBezoar; does not match bay FindProcessor.

**Default-off witness:** RM_Excretor special shear resource progress, gather job and bezoar output. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** Timed contaminant-bezoar shearing is a special refinery economy; ordinary taming survives without that output. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no RM_Excretor special shear resource progress, gather job and bezoar output and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show RM_Excretor special shear resource progress, gather job and bezoar output. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T2: Gripper junk carrying

**Scope:** Coordinate with theft gate so disabled theft cannot swap or conjure inventory; preserve vanilla inventory from an existing save and readable actual drops/death. Do not destroy held real items on switch-off.

**Source and coupling:** src/RimMandrake/Wastes/Source/RM_GripperTheft.cs; src/RimMandrake/Wastes/Defs/ThingDefs_Races/RM_Gripper.xml Called by: RM_Gripper.xml comp -> PostSpawnSetup/damage/drop and vanilla death inventory.

**Default-off witness:** spawned junk inventory, special carry/drop readout and injury-generated junk. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** Spawn junk, special inventory UI and injury drops support the independent theft vignette. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no spawned junk inventory, special carry/drop readout and injury-generated junk and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show spawned junk inventory, special carry/drop readout and injury-generated junk. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T3: Gripper theft

**Scope:** Gate the Animal_PreMain jobgiver as well as comp startup. Taming and ordinary animal AI remain. The historical keep/proof is not questioned; only new default-off behavior is being verified.

**Source and coupling:** src/RimMandrake/Wastes/Source/RM_GripperTheft.cs; src/RimMandrake/Wastes/Source/Kernel/RM_DoseKernel.cs; src/RimMandrake/Wastes/Defs/ThinkTreeDefs/RM_GripperTheft.xml Called by: RM_GripperTheft.xml Animal_PreMain -> RM_JobGiver_GripperSteal -> RM_GripperSteal job.

**Default-off witness:** RM_GripperSteal job selection, actual theft and special scurry. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** Stockpile theft is independent of environmental refuge maintenance. The prior agent keep cites existing proof, not necessity under this later scope instruction. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no RM_GripperSteal job selection, actual theft and special scurry and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show RM_GripperSteal job selection, actual theft and special scurry. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T4: Brine-bed extraction

**Scope:** Gate real local GenStep registration/execution and play acquisition; the shared brine terrain/FlowWorks mapping must remain. Coordinate the recipes and RM/RUT campaign deposit counterparts, rather than gating only the RM scatter patch.

**Source and coupling:** src/RimMandrake/Wastes/Defs/MapGeneration/RM_WastesBrine_Scatter.xml; src/RimMandrake/Wastes/Patches/RM_WastesBrine_ScatterRegister.xml; src/RimMandrake/Wastes/Defs/ThingDefs_Buildings/RM_WastesBrine_Deposits.xml; src/RimMandrake/Wastes/Defs/ThingDefs_Items/RM_WastesBrine_Items.xml Called by: RM_WastesBrine_Scatter.xml + ScatterRegister patch -> local Base_Player GenSteps -> mineables/products.

**Default-off witness:** sparkcrab/brineleech/electrode deposit scatter, their special mining availability and generated products. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** Pool-bed mining adds an independent resource route; dangerous brine remains without it. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no sparkcrab/brineleech/electrode deposit scatter, their special mining availability and generated products and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show sparkcrab/brineleech/electrode deposit scatter, their special mining availability and generated products. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T5: Raw brineleech shock

**Scope:** Gate its ingestion outcome too: absent natural acquisition is not protection from existing items or other producers. Do not conflate RM_Drazz with living RUT_BrineBattery discharge.

**Source and coupling:** src/RimMandrake/Wastes/Defs/ThingDefs_Items/RM_WastesBrine_Items.xml; src/RimMandrake/Wastes/Defs/HediffDefs/RM_BrineShock.xml Called by: RM_Drazz ingestion outcome in RM_WastesBrine_Items.xml -> RM_BrineShock.

**Default-off witness:** RM_BrineShock from special raw brineleech ingestion. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** A custom raw-food stun adds another hazard chain beyond native ground exposure. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no RM_BrineShock from special raw brineleech ingestion and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show RM_BrineShock from special raw brineleech ingestion. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T6: Plate-to-salt processing

**Scope:** Gate bill/menu eligibility and actual recipe completion, including queued jobs when switched off; retain ordinary salt from other mods.

**Source and coupling:** src/RimMandrake/Wastes/Defs/RecipeDefs/RM_CrackBrinePlate.xml Called by: RM_CrackBrinePlate.xml -> crafting spot / stonecutter consumes RM_BrinePlate.

**Default-off witness:** RM_CrackBrinePlate bill/recipe and its plate-cracking output. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** Plate cracking is coupled to deferred beds, not necessary ordinary land. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no RM_CrackBrinePlate bill/recipe and its plate-cracking output and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show RM_CrackBrinePlate bill/recipe and its plate-cracking output. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T7: Deadlight Halo

**Scope:** Remove it from default selection and gate direct weather-worker/controller and generic dose-layer paths for this deferred weather. Do not gate ash dose by disabling the entire common storm component.

**Source and coupling:** src/RimMandrake/Wastes/Source/RM_NamedStorms.cs; src/RimMandrake/Wastes/Source/Kernel/RM_StormKernel.cs; src/RimMandrake/Wastes/Defs/WeatherDefs/RM_WastesStorms.xml; src/RimMandrake/Wastes/Defs/SoundDefs/RM_WastesSounds.xml; src/RimMandrake/Wastes/Defs/FleckDefs/RM_WastesFlecks.xml Called by: RM_Wastes weather table -> RM_WastesRadiationHalo -> named weather worker / RM_MapComponent_StormPhases and dose component.

**Default-off witness:** natural Deadlight selection, phase warnings/clicks/rim flecks and its weather dose. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** The entire Deadlight Halo weather/dose/warning is another event; ash supplies the chosen signature. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no natural Deadlight selection, phase warnings/clicks/rim flecks and its weather dose and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show natural Deadlight selection, phase warnings/clicks/rim flecks and its weather dose. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T8: Cinderwire effects

**Scope:** Parent gate covers dose and phase controller plus the MovingDunes weather binding and weather sand input. Test forced eligible weather as well as absent natural scheduling. When enabled, no outside-terminator occurrence is allowed; do not implement a planet/region generator.

**Source and coupling:** src/RimMandrake/Wastes/Source/RM_NamedStorms.cs; src/RimMandrake/Wastes/Defs/WeatherDefs/RM_WastesStorms.xml; src/RimMandrake/Wastes/Defs/SoundDefs/RM_WastesSounds.xml; src/RimMandrake/Wastes/Defs/FleckDefs/RM_WastesFlecks.xml Called by: RM_WastesPlasmaStorm -> named storm controller, storm component and MovingDunes binding; no natural scheduler found.

**Default-off witness:** Cinderwire warning/static/levitating scrap/whine/EMP/lightning/dose/fall/burial multipliers. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** EMP and plasma lightning form a separate electrical disaster chain. Its terminator-only ban is preserved for later enabled use. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no Cinderwire warning/static/levitating scrap/whine/EMP/lightning/dose/fall/burial multipliers and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show Cinderwire warning/static/levitating scrap/whine/EMP/lightning/dose/fall/burial multipliers. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T9: Animal and giant radiation aura

**Scope:** Gate both attachments/runtime calls; storm toxicity uses a separate path and remains active. Dead-source guard and source-body geometry remain code, not new bars.

**Source and coupling:** src/RimMandrake/Wastes/Source/RM_CompAmbientDose.cs; src/RimMandrake/Wastes/Source/Kernel/RM_DoseKernel.cs; src/RimMandrake/Wastes/Defs/ThingDefs_Races/RM_Smolderback.xml; src/RimMandrake/Wastes/Defs/ThingDefs_Buildings/RM_Middenshell.xml Called by: RM_Smolderback.xml / RM_Middenshell.xml attach RM_CompAmbientDose; not called by storm dose.

**Default-off witness:** RM_Smolderback / RM_Middenshell room/radius ToxicBuildup. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** Animal/building auras serve the deferred furnace and giant; storms call ToxicUtility separately. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no RM_Smolderback / RM_Middenshell room/radius ToxicBuildup and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show RM_Smolderback / RM_Middenshell room/radius ToxicBuildup. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T10: Resident living furnace

**Scope:** Gate heat and associated aura under the same next-version parent with separate child controls. Keep the resident ordinary animal. Legacy nonresident RUT_Radiothermal remains external and is not silently consolidated or renamed.

**Source and coupling:** src/RimMandrake/Wastes/Source/RM_CompAmbientDose.cs; src/RimMandrake/Wastes/Defs/ThingDefs_Races/RM_Smolderback.xml Called by: RM_Smolderback.xml -> RM_CompRadiothermalHeat; RUT_Radiothermal uses separate shared heat/cook/spacing comps.

**Default-off witness:** RM_Smolderback heat pushes and room-dose bargain. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** The living furnace is the signature runner-up; keeping it adds another colony management bargain. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no RM_Smolderback heat pushes and room-dose bargain and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show RM_Smolderback heat pushes and room-dose bargain. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T11: Pollution-fed herd output

**Scope:** Gate CompMilkable Active, fullness changes, inspect promises and gather completion; decouple FindProcessor/bay conversion so it cannot use a disabled animal comp as a production permit. No soot-brick fuel behavior is assumed from flammability.

**Source and coupling:** src/RimMandrake/Wastes/Source/RM_CompProcessorGatherable.cs; src/RimMandrake/Wastes/Source/Kernel/RM_DoseKernel.cs; src/RimMandrake/Wastes/Defs/ThingDefs_Races/RM_Sloghog.xml; src/RimMandrake/Wastes/Defs/ThingDefs_Races/RM_Sootgrazer.xml; src/RimMandrake/Wastes/Defs/ThingDefs_Items/RM_WastesItems.xml Called by: RM_Sloghog / RM_Sootgrazer comps -> Milk jobs; RM_CompWasteContainment.FindProcessor also reads this comp.

**Default-off witness:** Sloghog/Sootgrazer special fullness, milk jobs, bezoars and soot bricks. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** Pollution-fed bezoars and soot bricks add a refinery economy, unnecessary for ordinary feeding/taming. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no Sloghog/Sootgrazer special fullness, milk jobs, bezoars and soot bricks and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show Sloghog/Sootgrazer special fullness, milk jobs, bezoars and soot bricks. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T12: Animal pollution consumption

**Scope:** Gate TryConsumePollution itself. Existing code calls it outside Active, so processorGatherEnabled=false alone does not switch it off. Leave shared plant sequestration working.

**Source and coupling:** src/RimMandrake/Wastes/Source/RM_CompProcessorGatherable.cs; src/RimMandrake/Wastes/Defs/ThingDefs_Races/RM_Sloghog.xml; src/RimMandrake/Wastes/Defs/ThingDefs_Races/RM_Sootgrazer.xml Called by: RM_CompProcessorGatherable.CompTick -> TryConsumePollution, independent of Active/fullness.

**Default-off witness:** processor unpolluting cells independently of fullness. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** Animal cleaning adds a competing map sink; later permission for consumption is preserved, not required in this version. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no processor unpolluting cells independently of fullness and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show processor unpolluting cells independently of fullness. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T13: Middenshell event parent

**Scope:** A whole event gate covers incident CanFireNow/TryExecute, scheduled Arrive, already spawned body movement/comp behavior and death effects. Keep the twenty-cell owner ruling; no roster change because the body is not a wildAnimals row. Suspend existing bodies readably; never vanish them.

**Source and coupling:** src/RimMandrake/Wastes/Source/RM_Middenshell.cs; src/RimMandrake/Wastes/Defs/ThingDefs_Buildings/RM_Middenshell.xml Called by: RM_MiddenshellArrives incident -> procession -> Building_Middenshell, never wildAnimals.

**Default-off witness:** giant arrival/body activation, omen and incidental immediate free-wander fallback. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** The titanic event is independent of native fallout/refuge maintenance; its ruled dimensions stay unchanged for later. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no giant arrival/body activation, omen and incidental immediate free-wander fallback and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show giant arrival/body activation, omen and incidental immediate free-wander fallback. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T14: Giant crushing wake

**Scope:** Gate wake effects independently of incident availability; existing bodies and direct movement callbacks must not produce destruction under off. Preserve code for the later giant parent.

**Source and coupling:** src/RimMandrake/Wastes/Source/RM_Middenshell.cs:185; src/RimMandrake/Wastes/Source/RM_Middenshell.cs:522; src/RimMandrake/Wastes/Source/RM_Middenshell.cs:574 Called by: Building_Middenshell crawl -> new-edge wake in RM_Middenshell.cs.

**Default-off witness:** new-edge building/item/plant destruction, floor/roof tearing and pawn damage. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** Moving destruction belongs to the deferred giant event. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no new-edge building/item/plant destruction, floor/roof tearing and pawn damage and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show new-edge building/item/plant destruction, floor/roof tearing and pawn damage. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T15: Giant tentacle grabs

**Scope:** Gate direct timed grabs and consume completion, not only new target selection; no destruction after an off transition.

**Source and coupling:** src/RimMandrake/Wastes/Source/RM_Middenshell.cs:625; src/RimMandrake/Wastes/Source/RM_Middenshell.cs:675 Called by: Building_Middenshell tick -> timed tentacle selection/consumption.

**Default-off witness:** tentacle targeting, consumption, dust pulls and target messages. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** Tentacle consumption belongs to the deferred giant event. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no tentacle targeting, consumption, dust pulls and target messages and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show tentacle targeting, consumption, dust pulls and target messages. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T16: Giant procession

**Scope:** Gate scheduler and Arrive under the whole giant parent. Current procession=false can give immediate free wander. Test parent-off plus child-on and saved pending omen, not just new incident selection.

**Source and coupling:** src/RimMandrake/Wastes/Source/RM_MiddenshellProcession.cs; src/RimMandrake/Wastes/Source/RM_Middenshell.cs:841; src/RimMandrake/Wastes/Defs/IncidentDefs/RM_MiddenshellArrives.xml Called by: RM_IncidentWorker_MiddenshellArrives -> RM_MapComponent_MiddenshellProcession.Schedule/Arrive; procession toggle alone falls back to immediate free wander.

**Default-off witness:** omen letter/tremor/creeping metal, pending arrival and crossing overlay. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** Omen, letters and crossing belong to the deferred giant event. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no omen letter/tremor/creeping metal, pending arrival and crossing overlay and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show omen letter/tremor/creeping metal, pending arrival and crossing overlay. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T17: Giant waste lure

**Scope:** Giant routing must not depend on special casks when both extras are off. Keep routing types loadable. A saved lure clears/suspends safely without moving any waste or deleting a body.

**Source and coupling:** src/RimMandrake/Wastes/Source/RM_Middenshell.cs:254; src/RimMandrake/Wastes/Source/RM_Middenshell.cs:310; src/RimMandrake/Wastes/Source/RM_MiddenshellProcession.cs:18 Called by: Building_Middenshell local routing -> waste-stockpile candidates, including deferred casks.

**Default-off witness:** stockpile acquisition/route bend and lure messages. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** Waste-directed routing belongs to the deferred giant event. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no stockpile acquisition/route bend and lure messages and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show stockpile acquisition/route bend and lure messages. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T18: Giant trail and shed resources

**Scope:** Gate all trail/departure production. Existing terrain/filth and resources remain physical history, not erased by a switch.

**Source and coupling:** src/RimMandrake/Wastes/Source/RM_Middenshell.cs:382; src/RimMandrake/Wastes/Source/RM_Middenshell.cs:453; src/RimMandrake/Wastes/Defs/TerrainDefs/RM_MiddenshellTrail_Terrains.xml; src/RimMandrake/Wastes/Defs/ThingDefs_Items/RM_MiddenshellTrail_Filth.xml Called by: Building_Middenshell movement/departure -> terrain/filth/sound/shed products.

**Default-off witness:** new trail/exit terrain, hot filth, shed flakes/bezoars, grind/heat and exit message. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** Permanent track and shed resources belong to the deferred giant event. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no new trail/exit terrain, hot filth, shed flakes/bezoars, grind/heat and exit message and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show new trail/exit terrain, hot filth, shed flakes/bezoars, grind/heat and exit message. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T19: Giant carcass quarry

**Scope:** Gate HardenCarcass and carcass component activation, not only a live-body incident. Saved seams remain but special effects suspend readably; no repeat material creation on reload/death.

**Source and coupling:** src/RimMandrake/Wastes/Source/RM_Middenshell.cs:735; src/RimMandrake/Wastes/Source/RM_Middenshell.cs:905; src/RimMandrake/Wastes/Defs/ThingDefs_Buildings/RM_Middenshell.xml Called by: Building_Middenshell death -> HardenCarcass -> RM_MapComponent_MiddenshellCarcass / seam jobs and dose.

**Default-off witness:** new carcass seams, special quarry resource mining and carcass worker-dose records. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** Giant carcass mining belongs to the deferred giant event. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no new carcass seams, special quarry resource mining and carcass worker-dose records and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show new carcass seams, special quarry resource mining and carcass worker-dose records. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T20: Special waste casks

**Scope:** Gate contract delivery, trade/scatter if any, direct leak/burst comp paths, special menus and dependent consumers. Decouple native refuge cleanup from special casks; vanilla wastepacks remain part of the ordinary game. Existing objects keep identity/dose and become inert readably when disabled.

**Source and coupling:** src/RimMandrake/Wastes/Source/RM_WasteCaskBay.cs:55; src/RimMandrake/Wastes/Source/RM_WasteCaskBay.cs:261; src/RimMandrake/Wastes/Source/Kernel/RM_WasteCaskKernel.cs; src/RimMandrake/Wastes/Defs/ThingDefs_Items/RM_WasteCask.xml Called by: QuestPart_RM_TippingContract deliveries; bay Casks(), reburial, leak registry, giant waste preference and launch checks read RM_CompWasteCask.

**Default-off witness:** new RM_WasteCask acquisition, leak/burst effects, alerts and reburial commands. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** Introduced cargo adds a separate source and handling system; native exposure must suffice on a fresh map. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no new RM_WasteCask acquisition, leak/burst effects, alerts and reburial commands and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show new RM_WasteCask acquisition, leak/burst effects, alerts and reburial commands. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T21: Sealed cask bays

**Scope:** Parent gate must cover the entire CompTickRare including current ungated heat evolution/PushHeat, as well as build availability and capacity mutation. Do not make the kept refuge require a bay; ordinary roofs and cleanup suffice.

**Source and coupling:** src/RimMandrake/Wastes/Source/RM_WasteCaskBay.cs:413; src/RimMandrake/Wastes/Defs/ThingDefs_Buildings/RM_WasteCaskBay.xml; src/RimMandrake/Wastes/Source/Kernel/RM_WasteCaskKernel.cs Called by: RM_WasteCaskBay.xml -> Building_RM_WasteCaskBay / RM_CompWasteContainment.CompTickRare -> heat/seals/leaks.

**Default-off witness:** bay build/menu acquisition, seal evolution, heat pushes, leaks and readout promises. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** Powered cargo containment exists for deferred casks, not the ordinary native-ground refuge. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no bay build/menu acquisition, seal evolution, heat pushes, leaks and readout promises and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show bay build/menu acquisition, seal evolution, heat pushes, leaks and readout promises. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T22: Cask processing

**Scope:** Fix global gate enforcement inside CompTickRare/TickProcessing, not only command visibility. FindProcessor must honor enabled animal production and parent cargo gates. Queued progress suspends without consuming a cask.

**Source and coupling:** src/RimMandrake/Wastes/Source/RM_WasteCaskBay.cs:534; src/RimMandrake/Wastes/Source/RM_WasteCaskBay.cs:558; src/RimMandrake/Wastes/Source/RM_WasteCaskBay.cs:643 Called by: RM_CompWasteContainment.CompTickRare -> TickProcessing -> FindProcessor; current global flag only hides command.

**Default-off witness:** processing command, progress, cask consumption and animal-product output. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** Herd-assisted cask conversion adds another refinery route. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no processing command, progress, cask consumption and animal-product output and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show processing command, progress, cask consumption and animal-product output. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T23: Special-cargo launch veto

**Scope:** Keep patch/type loadable but runtime verdict neutral when the extra is off. Preserve vanilla/other-mod launch refusals. Real unsafe versus safe gravship launch controls are required for enabled verification, not patch-installed state alone.

**Source and coupling:** src/RimMandrake/Wastes/Source/RM_WasteCaskBay.cs:582; src/RimMandrake/Wastes/Source/RM_WasteCaskBay.cs:684; src/RimMandrake/Wastes/Source/Kernel/RM_WasteCaskKernel.cs Called by: RM_WasteCaskBayUtility static constructor -> Building_GravEngine.CanLaunch postfix; settings drawer also calls ApplyCapacity.

**Default-off witness:** Wastes special CanLaunch refusal and cask/bay scanning. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** The special launch veto exists for deferred cargo; vanilla launch checks remain. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no Wastes special CanLaunch refusal and cask/bay scanning and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show Wastes special CanLaunch refusal and cask/bay scanning. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T24: Special cask reburial

**Scope:** Gate job selection and completion and NotifyIllegalDump. Retain ordinary terrain/pollution and vanilla hauling; no special cask is needed by kept pollution cleanup.

**Source and coupling:** src/RimMandrake/Wastes/Source/RM_WasteCaskBay.cs:211; src/RimMandrake/Wastes/Source/RM_WasteCaskBay.cs:225; src/RimMandrake/Wastes/Source/RM_WasteCaskBay.cs:784; src/RimMandrake/Wastes/Defs/ThingDefs_Items/RM_WasteCask.xml Called by: Cask gizmo -> reburyMarked -> workgiver/dig job -> pollution + active contract NotifyIllegalDump.

**Default-off witness:** designation/gizmo, custom workgiver/job and contract dump notifications. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** A custom disposal job exists for deferred cargo/contracts. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no designation/gizmo, custom workgiver/job and contract dump notifications and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show designation/gizmo, custom workgiver/job and contract dump notifications. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T25: Rite of Tipping

**Scope:** Gate both offers and existing QuestPart ticking/callbacks. Parent off is not just tippingEnabled at TestRun. Suspend old contracts readably without deleting them or silently continuing payment/delivery. Preserve term-limited liability.

**Source and coupling:** src/RimMandrake/Wastes/Source/RM_RiteOfTipping.cs; src/RimMandrake/Wastes/Source/Kernel/RM_TippingKernel.cs; src/RimMandrake/Wastes/Defs/Quests/RM_RiteOfTipping.xml Called by: RM_RiteOfTipping.xml incident/quest root -> QuestPart tick/pad/deliveries; RiteOfTipping_Factions.xml patches roles.

**Default-off witness:** pad build/licence acquisition, offers, active deliveries/casks/rewards/letters and ongoing contract activity. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** Repeated paid deliveries, a licensed pad and obligations are a quest extra; fresh-map danger must not require accepting it. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no pad build/licence acquisition, offers, active deliveries/casks/rewards/letters and ongoing contract activity and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show pad build/licence acquisition, offers, active deliveries/casks/rewards/letters and ongoing contract activity. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T26: Tipping evidence diplomacy

**Scope:** Gate delivery-triggered request and callbacks independently of offer visibility; include letters saved open at switch-off. No hidden discovery or goodwill activity under defaults.

**Source and coupling:** src/RimMandrake/Wastes/Source/RM_RiteOfTipping.cs:382; src/RimMandrake/Wastes/Source/RM_RiteOfTipping.cs:490; src/RimMandrake/Wastes/Source/Kernel/RM_TippingKernel.cs Called by: QuestPart_RM_TippingContract delivery -> sample request / choice-letter callbacks / timeout.

**Default-off witness:** sample-request letters, sample removal, choice callbacks and timeout goodwill. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** Diplomatic evidence letters extend the deferred quest. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no sample-request letters, sample removal, choice callbacks and timeout goodwill and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show sample-request letters, sample removal, choice callbacks and timeout goodwill. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T27: Containment grant

**Scope:** Gate the grant branch and campaign faction adapter; a standing but unpowered bay is not proof of a meaningful functioning grant condition. Later enabled definition must state the criterion; do not redesign it here.

**Source and coupling:** src/RimMandrake/Wastes/Source/RM_RiteOfTipping.cs:429; src/RimMandrake/Wastes/Source/Kernel/RM_TippingKernel.cs; src/RimUtinni/UtinniPatches/Patches/RiteOfTipping_Factions.xml Called by: QuestPart_RM_TippingContract delivery -> bay-present grant branch + campaign faction-role patch.

**Default-off witness:** grant hints, one-time payment/goodwill and repeat checks. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** A third-faction containment subsidy extends the deferred quest. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no grant hints, one-time payment/goodwill and repeat checks and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show grant hints, one-time payment/goodwill and repeat checks. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T28: Illegal dumping discovery

**Scope:** Gate NotifyIllegalDump and active-contract roll path; after the stated contract term no contractual penalty survives. Physical ground pollution persists independently.

**Source and coupling:** src/RimMandrake/Wastes/Source/RM_RiteOfTipping.cs:113; src/RimMandrake/Wastes/Source/RM_RiteOfTipping.cs:452; src/RimMandrake/Wastes/Source/Kernel/RM_TippingKernel.cs Called by: Reburial -> NotifyIllegalDump -> active QuestPart discovery/goodwill rolls.

**Default-off witness:** reburial discovery rolls, related letters and goodwill penalties. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** Discovery and goodwill penalties extend the deferred quest; contractual liability still ends with its term. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no reburial discovery rolls, related letters and goodwill penalties and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show reburial discovery rolls, related letters and goodwill penalties. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T29: Raw milk mood bonus — retirement recommended

**Scope:** Default off pending owner retirement decision; keep the clean milk and vanilla nutrition/rot handling. If enabled, only the intended custom thought returns, not new global food effects.

**Source and coupling:** src/RimMandrake/Wastes/Defs/ThingDefs_Races/RM_Kroffa.xml Called by: RM_KroffaMilk ingestion -> custom thought.

**Default-off witness:** custom raw-kroffa-milk mood thought. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** Recommend retiring the bonus: vanilla food quality already rewards pleasant meals; the milk remains useful without another mood effect. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no custom raw-kroffa-milk mood thought and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show custom raw-kroffa-milk mood thought. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T30: Isi isi defensive discharge

**Scope:** Gate this campaign creature attachment/consumer only; do not switch the shared CreatureBehaviors engine off globally. The resident and ordinary environmental drinking remain; preserve cooldown/recursion guards in its code.

**Source and coupling:** src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_BrineBattery.xml; src/RimMandrake/CreatureBehaviors/Source/RM_CompDefensiveDischarge.cs Called by: RUT_BrineBattery attaches shared defensive-discharge comp.

**Default-off witness:** shared defensive zap/EMP/organic stun triggered by RUT_BrineBattery. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** Electrical retaliation is independent of ground/refuge maintenance; retain shared engine and resident while deferring its special behaviour. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no shared defensive zap/EMP/organic stun triggered by RUT_BrineBattery and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show shared defensive zap/EMP/organic stun triggered by RUT_BrineBattery. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T31: Campaign sealed-corpse scatter

**Scope:** Gate RUT_JunkerSealedCorpses.xml registration/execution under its next-version setting. Generic Wreckage sarcophagus/hull/cylinder land remains and cannot serve as the on-arm witness for this distinct feature.

**Source and coupling:** src/RimUtinni/UtinniPatches/Patches/RUT_JunkerSealedCorpses.xml Called by: Warcasket FindMod -> RUT_SealedJunkerCorpses_Wastes -> RM_GenStep_SealedCorpses in RM_Wastes.extraGenSteps.

**Default-off witness:** RUT_SealedJunkerCorpses_Wastes local scatter and generated real sealed Junker corpse objects. Species, ordinary terrain and retained shared systems are not absence targets. Keep code and definitions in the tree.

**Decoupling:** Wreckage already provides irradiated remains; a real sealed-corpse/suit interaction is a separate campaign vignette. No kept bar may call this as its source of danger, food, warning, shelter or work; preserve shared utilities separately from its player-visible behaviour.

Acceptance test: Apply the common protocol. At fresh defaults, state reads show no RUT_SealedJunkerCorpses_Wastes local scatter and generated real sealed Junker corpse objects and the log is clean; with the labelled setting on and its documented eligible prerequisites enabled, state reads show RUT_SealedJunkerCorpses_Wastes local scatter and generated real sealed Junker corpse objects. Exercise the direct caller above and a saved active-state off/on transition so a hidden command or absent natural roll cannot produce a false pass.

## T40: Define and implement the native contamination cycle

Needed by initial_ground, dosimeter_reading, plant_sequestration, vault_reopening and redistribution. These are kept promises with missing/unproven runtime contracts, not grounds to weaken the core. Implement the state/transition semantics in definition.md using existing pollution/toxicity and transport interfaces; no player radiation meter, new weather or drift engine. First inventory actual inherited ground and any broader stock hooks. Preserve pollution and stores already in a save; local initialization is versioned/idempotent and authors no world tiles. Provide current surface/loaded-root/uncertainty information through existing inspection. Radmoss follows current mobile danger; cinderfelt indicates recent deposition and cannot rely on its unconditional temporary fallback. Handle slow sequestration, ordinary destructive callbacks including shared plant lifecycle ends, partial remainders and reload exactly once. Document brine-source input and wastepack output. If MovingDunes exposes no usable transfer observation, provide the smallest integration adapter with its owner; do not invent independent ash physics.

Acceptance test: M1 transition walks and M2 calibrated traces distinguish old-stock transport from fresh input, demonstrate surface recovery with retained bound stock, remobilize a finite load under each real destructive route, and preserve identities/remainders through reload and reordered jobs. Warm, margin and cold full maps start with informed construction choices. B3 human comparison verifies the cue/inspection result; a static def/name read cannot pass. The log is clean.

## T41: Resolve land, preservation and ordinary-life gaps

First read actual effective warm/cold rot, diet, native-water, prey targeting, flight and authored landscape states; do not declare them unbuilt from descriptions. Supply the smallest missing Wastes binding or rule implementation for B1/B2/B7. Native scabspinner does not routinely hunt settlers/tame livestock; existing vanilla/shared predator machinery is preferred. Native thirst compatibility follows the global rule, not human water permission. Suppress environmental rot consistently in the declared Wastes envelope without refrigeration or resetting items when leaving/returning. Track real cache identity/rot progress. Inventory actual fixed rib-vault structures: the located Wastes-eligible Kiln is not a rib-vault and Bones is not a generator. Where authored rib-vault sites promise ash shelter, supply real cover and truthful dirty-ground warning; no new planet or procedural landmark program. Read resolved ExplosiveGrowth profiles and ensure no anomaly/bioweapon outcomes or hidden second Wastes mechanic are introduced by the binding. Existing art is accepted; this is mechanical shelter/land readability work, not replacement art.

Acceptance test: M4 agrees with actual reachable feeding/drinking, reproduction, real milk/egg jobs, warm/cold rot records and deconstruct/protection comparisons; M1 covers interruption/death/reload. State-only flight transitions use the standing restriction. Inspect actual whole-body directional flight animation wiring (the current RM_Grimewing def lacks flyingAnimationFramePathPrefix); address the flight implementation using the existing asset system without requiring a new illustration approval or a variant quota. B1 actual-land comparison confirms described shelter has real cover and usable ground. No new roster eviction, worldgen, missing references or recurring log errors.

## T42: Park incomplete promises with explicit later boundaries

Produce later-version mechanic specifications for natural Cinderwire eligibility/scheduling, exhumation-target Grimewing circling, native titan pawn passage, and any bespoke plant-vault fuel-deposit economy beyond the kept finite-release mechanism. Cinderwire retains its existing terminator-only ban; one def remains and the campaign provides explicit authored pocket eligibility, never a temperature-only guess or new planet generator. Circling uses actual exhumation targets and is separate from required flight. Native titan passage must recover the referenced sitting and actual pool before claiming it built; a Building is not a Pawn. Recommend retiring raw-pusberry poisoning and its misleading promise: present source yields ordinary RawBerries, so do not poison vanilla berries globally. These unbuilt/unknown extras receive no implementation in 0.1.0. Preserve any already-built broader counterpart until inventoried, then give it the corresponding labelled parent gate.

Acceptance test: Document each later mechanic’s entry/exit states, player consequence, settings parent and real eligible/negative witness before enabling it; current default-map state contains none of their special events/jobs/outputs and the log is clean. For raw-pusberry retirement recommendation, the owner decides removal; until then the special harm remains off and ordinary berries keep ordinary ingestion. No acceptance of unfinished later gameplay is claimed.

## T43: Whole-map recorder and calibrated stock model

Supply the M2 actual-state adapter and recorder for B4–B8 plus M1 save/order boundaries. Read effective settings, defs/build fingerprints, all actual game ticks, unlocked weather, mobile/bound/input/cleanup/boundary accounts, projection remainders, root/cached-item identities, pollution/sand/marker grids, actual job/product/health/food histories, errors and component timings. Independent real health reads must not merely echo model-predicted dose. Add explicit disposable-save baseline/mid/end retention and full reset; current pad teardown and Clear lock are insufficient. The whole seasonal runner preserves every shared cadence during acceleration and extends naturally when the cycle has not occurred. Capture loaded-source fingerprints and do not claim mocks as runtime calibration.

Acceptance test: Export initial/mid/endpoint full-map records, validate stock and identity reconciliation, demonstrate uninterrupted versus mid-save reload and both work orders, and compare production traces with M2 at its stated calibration tolerances. Reject a record with locks, absent eligible intervals, hidden food, skipped callbacks or unobserved stock; report unknown when an adapter cannot read. M2 outputs remain predictions until this agreement is shown.

## T44: Rendered regime and route comparison instrument

Create the cheapest actual-game views and matching state records needed for B1/B3, using existing accepted assets. Present matched route contexts in swapped positions and hide labels/ground truth for an independent reader’s sorting. Include fresh fall, mature growth, bare-hot ground, ash-hidden/dead indicators, cleaned cinderfelt and clean surface/loaded roots in warm/margin/cold lighting; allow existing closer inspection, no invented safety overlay. Also show actual construction/roof/landmark affordance and natural ash state. No flight screenshot or autonomous flight performance is part of this instrument. M3 supplies the situation coverage, not a synthetic visual verdict.

Acceptance test: A reader with the definition but hidden toxicity classifies the contrasted pictures as B1/B3 do, using closer inspection for explicitly uncertain contexts; later reveal independently read actual dose/stock/source state. Swapping route sides and decorative scenery does not reverse the justified risk ordering. A name/label-only or model-rendered substitute is refused; failure points to a cue/inspect repair, not a request for the owner to guess measurements.

## T45: Shared-engine and ordinary-job state adapters

Provide the minimum missing game-state observation used by M1/M3/M4: effective ExplosiveGrowth profiles and real organ-end hooks; MovingDunes transfers/depth/cache contents and retained item IDs; actual Wreckage deconstruct outputs/worker dose; native eat/drink/prey/milk/egg/birth/death events and state-only flight tracker transitions; real rot progress and outside-biome resume; actual settings-file and direct callback gate effects. Read the shared engines as they are; do not redesign them. Existing kernel fuzz and Python mock suites remain useful regression checks but are not an independent witness for adapter correctness. Source/count/profile checks do not substitute for real jobs or effective runtime state.

Acceptance test: For each adapter used to decide a bar, compare its record with the originating save/state object and a real completed or interrupted/resumed event, including a negative control. IDs, categorical states and event order agree exactly; quantities/ticks follow the calibration tolerances in models.md. A missing/unreadable receiver returns unknown, not zero. A forced full milk bar, scatter_at bypass or installed launch patch alone is insufficient. No game or bridge is run on this design pass.
