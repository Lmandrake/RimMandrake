# Proposed work tickets

These are specifications only. No game, bridge, code or dependency was changed. Every switch-off ticket includes direct-worker, map-tick, reload and availability paths; no shared engine is disabled globally.

## T1: Scald steam-catch condenser and distilled-water production

Decision: Designer, delegated; next_version. An independent resource machine; the boiling shore and native life still work with imported drinking water.

Evidence: `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Buildings/RM_SteamCatch.xml`. Called by: `src/RimMandrake/TerminalBiomes/validation.py`, `src/RimMandrake/Utils/scald_showcase.py`, `src/RimMandrake/TerminalBiomes/Source/RM_TerminalBiomesMod.cs`, `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Items/RM_DistilledWater.xml`, `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Buildings/RM_ScaldVent.xml`, `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Buildings/RM_ChillStonewaterExtractor.xml`, `src/RimMandrake/EnvironmentalHazards/Defs/Misc/RM_BiomeTierCleanup_Aliases.xml`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Scald steam-catch condenser and distilled-water production”, shipped false, under master/per-sea activation. Gate construction, condenser production, research and offers; keep natural vents independent. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. 

## T2: Scald steam exposure clock and boil-suit research

Decision: Designer, delegated; next_version. A separate custom health clock beyond ordinary air heat and liquid contact. Direct Sun ruling requires hot air on the thermometer.

Evidence: `src/RimMandrake/TerminalBiomes/Defs/GameConditionDefs/RM_ScaldSteamCarrier.xml`, `src/RimMandrake/TerminalBiomes/Defs/HediffDefs/RM_ScaldExposure.xml`, `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Apparel/RM_ScaldGear.xml`. Called by: `src/RimMandrake/TerminalBiomes/prove_rindcoat_scald_live.py`, `src/RimMandrake/TerminalBiomes/validation.py`, `src/RimMandrake/TerminalBiomes/proof_scald_steam.py`, `src/RimMandrake/Utils/selftest_rindcoat_live_proof.py`, `src/RimMandrake/Utils/selftest_rindcoat_scald_clock.py`, `src/RimMandrake/TerminalBiomes/Source/RM_TerminalBiomesMod.cs`, `src/RimMandrake/EnvironmentalHazards/Defs/Misc/RM_BiomeTierCleanup_Aliases.xml`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Scald steam exposure clock and boil-suit research”, shipped false, under master/per-sea activation. Stop grant, ticks and residual reapplication; settle existing exposure safely without changing shared engine heat. Suit remains a saved object but new research/recipes are hidden. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. 

## T3: Steam-devil wandering damage encounters

Decision: Designer, delegated; next_version. A second roaming hazard, unnecessary for boiling land or the current signature.

Evidence: `src/RimMandrake/TerminalBiomes/Defs/IncidentDefs/RM_SteamDevilAppears.xml`, `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Misc/RM_SteamDevil.xml`. Called by: `src/RimMandrake/TerminalBiomes/Defs/Misc/RM_SteamDevilRename_Aliases.xml`, `src/RimMandrake/TerminalBiomes/Defs/IncidentDefs/RM_VeilFallPaneStrike.xml`, `src/RimMandrake/EnvironmentalHazards/Source/RM_IncidentWorker_SteamDevil.cs`, `src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_RoilVortexSpawner.cs`, `src/RimMandrake/EnvironmentalHazards/Languages/English/Keyed/RM_SteamDevil_Keys.xml`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Steam-devil wandering damage encounters”, shipped false, under master/per-sea activation. Gate storyteller and direct worker entry, active vortex ticking and letters. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. 

## T4: Vent-flash sky pulses

Decision: Designer, delegated; next_version. Steam already reads through its overlay and vents; map-wide flashes are an independent flourish.

Evidence: `src/RimMandrake/TerminalBiomes/Defs/SoundDefs/RM_VentFlashSpray.xml`, `src/RimMandrake/TerminalBiomes/Defs/WeatherDefs/RM_ScaldSteam.xml`. Called by: `src/RimMandrake/TerminalBiomes/Source/RM_TerminalBiomesMod.cs`, `src/RimMandrake/EnvironmentalHazards/Source/RM_WeatherEvent_VentFlash.cs`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Vent-flash sky pulses”, shipped false, under master/per-sea activation. Keep base steam overlay and ambience; suppress only weather-event flash dispatch and flash sound. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. 

## T5: Staged bubble-sail and walker appearances

Decision: Designer, delegated; next_version. Scripted set-pieces duplicate the ordinary roster encounter. No animal is evicted.

Evidence: `src/RimMandrake/TerminalBiomes/Defs/MapGeneration/RM_ScaldSailScatterer.xml`, `src/RimMandrake/TerminalBiomes/Defs/IncidentDefs/RM_WalkerSurfacing.xml`. Called by: `src/RimMandrake/TerminalBiomes/validation.py`, `src/RimMandrake/TerminalBiomes/Source/RM_TerminalBiomesMod.cs`, `src/RimMandrake/TerminalBiomes/Tools/selftest_sea_text_no_surface_place.py`, `src/RimMandrake/TerminalBiomes/Languages/English/Keyed/RM_Scald_Mechanics.xml`, `src/RimMandrake/TerminalBiomes/Defs/IncidentDefs/RM_VeilFallPaneStrike.xml`, `src/RimMandrake/TerminalBiomes/Defs/IncidentDefs/RM_SuulkArrival.xml`, `src/RimMandrake/EnvironmentalHazards/Source/RM_IncidentWorker_WalkerSurfacing.cs`, `src/RimMandrake/EnvironmentalHazards/Defs/Misc/RM_BiomeTierCleanup_Aliases.xml`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Staged bubble-sail and walker appearances”, shipped false, under master/per-sea activation. Gate scatter and surfacing incident; leave native walker population and ordinary bubble presentation. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. 

## T6: Thurlsponge colonisation of wrecks

Decision: Designer, delegated; next_version. A bespoke placement interaction between otherwise complete flora and salvage.

Evidence: `src/RimMandrake/TerminalBiomes/Source/RM_ScaldThurlspongeWrecks.cs`, `src/RimMandrake/TerminalBiomes/Defs/MapGeneration/RM_ScaldThurlspongeWrecks.xml`. Called by: `src/RimMandrake/TerminalBiomes/Source/RM_TerminalBiomesMod.cs`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Thurlsponge colonisation of wrecks”, shipped false, under master/per-sea activation. Gate genstep; ordinary thurlsponge roster and Wreckage placement stay independent. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. 

## T7: Twilight falling panes, flakes and deck launch obstruction

Decision: Designer, delegated; next_version. A separate impact/clearance system. The lid, temporary light and fish do not require hazardous pane impacts.

Evidence: `src/RimMandrake/TerminalBiomes/Source/RM_MapComponent_VeilFall.cs`, `src/RimMandrake/TerminalBiomes/Source/RM_IncidentWorker_PaneStrike.cs`, `src/RimMandrake/TerminalBiomes/Source/RM_Patch_GravEngineLaunchGate.cs`. Called by: `src/RimMandrake/TerminalBiomes/Source/RM_TerminalBiomesMod.cs`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Twilight falling panes, flakes and deck launch obstruction”, shipped false, under master/per-sea activation. Gate floor strike, ordinary shed, deck accumulation, skyfaller harm, deconstruct rewards and launch postfix together. Preserve the already-ruled floor/deck unity. Ordinary hollu fauna stay. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. 

## T8: Suulk light feeding, arrival pressure and persistent graze debt

Decision: Designer, delegated; next_version. A second consumption/maintenance economy, not ordinary wild predation.

Evidence: `src/RimMandrake/TerminalBiomes/Source/RM_IncidentWorker_SuulkArrival.cs`, `src/RimMandrake/TerminalBiomes/Source/RM_JobGiver_SeekGlow.cs`, `src/RimMandrake/TerminalBiomes/Source/RM_JobDriver_FeedOnGlow.cs`, `src/RimMandrake/TerminalBiomes/Source/RM_MapComponent_GlowGraze.cs`. Called by: `src/RimMandrake/TerminalBiomes/Source/RM_Building_SunSphere.cs`, `src/RimMandrake/TerminalBiomes/Source/RM_SeekGlowExtension.cs`, `src/RimMandrake/TerminalBiomes/Source/RM_TerminalBiomesMod.cs`, `src/RimMandrake/TerminalBiomes/Source/RM_TerminalBiomesJobDefOf.cs`, `src/RimMandrake/TerminalBiomes/Defs/JobDefs/RM_JobDefs_SeekGlow.xml`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Suulk light feeding, arrival pressure and persistent graze debt”, shipped false, under master/per-sea activation. Gate incident, think-tree dispatch, running jobs and graze reassertion. Detach well-ledger pressure calculation; native luminous fauna and well light must run without this layer. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. 

## T9: Vaulisk false-lamp ambush and lure-organ drop

Decision: Designer, delegated; next_version. A custom deceptive interaction beyond ordinary predators and the chosen current risk.

Evidence: `src/RimMandrake/TerminalBiomes/Source/RM_Comp_VaeuliskLure.cs`, `src/RimMandrake/TerminalBiomes/Source/RM_GenStep_ScatterVauliskLure.cs`, `src/RimMandrake/TerminalBiomes/Source/RM_Comp_DropLureOrganOnDeath.cs`. Called by: `src/RimMandrake/Utils/exotic_materials_census.py`, `src/RimMandrake/Utils/art/texture_regen_jobs.py`, `src/RimMandrake/TerminalBiomes/Source/RM_TerminalBiomesMod.cs`, `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_VauliskLure.xml`, `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Races/RM_TwilightSeaDangers.xml`, `src/RimMandrake/TerminalBiomes/Defs/MapGeneration/RM_TwilightScatterVauliskLure.xml`, `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Items/RM_VauliskLureOrgan.xml`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Vaulisk false-lamp ambush and lure-organ drop”, shipped false, under master/per-sea activation. Gate lure generation, proximity and job-start hooks, spawn/reveal, reward organ drop and any lure production. No roster eviction and no invisible deletion of an existing animal. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. 

## T10: Cargo floats and current shipping jobs

Decision: Designer, delegated; next_version. A logistics mini-game. Loose ordinary items already demonstrate current transport.

Evidence: `src/RimMandrake/TerminalBiomes/Source/RM_Thing_CargoFloat.cs`, `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Items/RM_CargoFloat.xml`. Called by: `src/RimMandrake/Utils/exotic_materials_census.py`, `src/RimMandrake/Utils/art/texture_regen_jobs.py`, `src/RimMandrake/TerminalBiomes/Source/RM_TerminalBiomesDefOf.cs`, `src/RimMandrake/TerminalBiomes/Source/RM_MapComponent_ChannelCurrent.cs`, `src/RimMandrake/TerminalBiomes/Languages/English/Keyed/RM_ChannelCurrent_Mechanics.xml`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Cargo floats and current shipping jobs”, shipped false, under master/per-sea activation. Remove float dependency from current arrest; disable float manufacture, gizmos, load/unload and jobs. Preserve held contents of saved floats without silent loss. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. 

## T11: Injured and lost sink outcome variants

Decision: Designer, delegated; next_version. Optional punishment variants add no required bank/carry/rescue step.

Evidence: `src/RimMandrake/TerminalBiomes/Source/RM_MapComponent_ChannelCurrent.cs`, `src/RimMandrake/TerminalBiomes/Defs/HediffDefs/RM_Hediff_Sunk.xml`. Called by: `src/RimMandrake/TerminalBiomes/Source/RM_TerminalBiomesMod.cs`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Injured and lost sink outcome variants”, shipped false, under master/per-sea activation. Default and normal settings offer Recoverable. Gate scar and Lost paths behind next-version option; even opt-in must obey readable-sign ruling. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. 

## T12: Portable constellation cages, clipped lamps and crop snapshots

Decision: Designer, delegated; next_version. A portable farming toolset, unnecessary to natural columns, bank forage or the current.

Evidence: `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Buildings/RM_TwilightConstellation.xml`, `src/RimMandrake/TerminalBiomes/Source/RM_CompCageCropSnapshot.cs`. Called by: `src/RimMandrake/TerminalBiomes/validation.py`, `src/RimMandrake/TerminalBiomes/Source/RM_TerminalBiomesMod.cs`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Portable constellation cages, clipped lamps and crop snapshots”, shipped false, under master/per-sea activation. Gate build/bill/trader availability and growth/snapshot behaviour; decouple natural plant light and mobile native glowers. Saved cages retain their plants/holders safely. Disable passability applier when this layer is off. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. 

## T13: Cultured sun-sphere and related research

Decision: Designer, delegated; next_version. An independent cultivation progression, the runner-up signature economy.

Evidence: `src/RimMandrake/TerminalBiomes/Source/RM_Building_SunSphere.cs`, `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Buildings/RM_SunSphere.xml`, `src/RimMandrake/TerminalBiomes/Defs/ResearchProjectDefs/RM_TwilightLightEconomyResearch.xml`. Called by: `src/RimMandrake/TerminalBiomes/Source/RM_TerminalBiomesMod.cs`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Cultured sun-sphere and related research”, shipped false, under master/per-sea activation. Gate construction, research, stores, culture and glow writes; keep existing holders safe. Natural wells must not count player culture to stay alive. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. 

## T14: Grey hull rime, salted doors, crust jobs and tear-free launch

Decision: Designer, delegated; next_version. A ship maintenance system independent of ordinary mineral ground and fauna.

Evidence: `src/RimMandrake/TerminalBiomes/Source/RM_GreyHullCrust.cs`, `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Buildings/RM_GreyHullCrust.xml`, `src/RimMandrake/TerminalBiomes/Defs/WorkGiverDefs/RM_WorkGiverDefs_GreyHullCrust.xml`. Called by: `src/RimMandrake/TerminalBiomes/Source/RM_GreyLampResponse.cs`, `src/RimMandrake/TerminalBiomes/Source/RM_HazardClockInspect.cs`, `src/RimMandrake/TerminalBiomes/Source/RM_TerminalBiomesMod.cs`, `src/RimMandrake/TerminalBiomes/Languages/English/Keyed/RM_GreyHullCrust.xml`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Grey hull rime, salted doors, crust jobs and tear-free launch”, shipped false, under master/per-sea activation. Gate map/game components, salt persistence reassertion, door restrictions, launch restrictions, workgivers, forced-launch gizmo and rewards together. Keep the ruled always-available tear-free escape intact whenever this deferred system is enabled. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. 

## T15: Grey lamp watchers, scrape warnings, light-seekers and lamp-breaking giant

Decision: Designer, delegated; next_version. A separate light-triggered encounter system; mineral land, endemic animal bodies and ordinary predation remain.

Evidence: `src/RimMandrake/TerminalBiomes/Source/RM_GreyLampResponse.cs`, `src/RimMandrake/TerminalBiomes/Defs/JobDefs/RM_JobDefs_GreyLampResponse.xml`, `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Misc/RM_Filth_ScrapeLine.xml`. Called by: `src/RimMandrake/TerminalBiomes/Source/RM_HazardClockInspect.cs`, `src/RimMandrake/TerminalBiomes/Source/RM_TerminalBiomesMod.cs`, `src/RimMandrake/TerminalBiomes/Source/RM_JobGiver_SeekGlow.cs`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Grey lamp watchers, scrape warnings, light-seekers and lamp-breaking giant”, shipped false, under master/per-sea activation. Gate dispatch, running jobs, burn clocks, signs and inspect branches. Native reefbacks/fessk stay alive and can behave ordinarily. Do not disable natural glow with it. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. 

## T16: Brine-crown salt-weather retraction picture

Decision: Designer, delegated; next_version. An optional reactive art trick; the crystalline plant reads in its normal form.

Evidence: `src/RimMandrake/TerminalBiomes/Source/RM_WeatherPlantGraphic.cs`, `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_GreySeaFlora.xml`. Called by: `src/RimMandrake/TerminalBiomes/Source/RM_TerminalBiomesMod.cs`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Brine-crown salt-weather retraction picture”, shipped false, under master/per-sea activation. Gate weather-driven graphic updates; normal plant and native light remain. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. 

## T17: Grey sphere-plant and brine-crown contact venom

Decision: Designer, delegated; next_version. A distinct touching-plant hazard; predatory fauna and dangerous pool terrain already supply the Grey risk.

Evidence: `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_GreySeaFlora.xml`. Called by: `src/RimMandrake/EnvironmentalHazards/Source/MapComponent_ContactVenom.cs`, `src/RimMandrake/EnvironmentalHazards/Source/CompContactVenom.cs`, `src/RimMandrake/EnvironmentalHazards/Source/RM_CompBodySizeBarrier.cs`, `src/RimMandrake/EnvironmentalHazards/Defs/ThingDefs_Plants/RM_Venomvine.xml`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Grey sphere-plant and brine-crown contact venom”, shipped false, under master/per-sea activation. Gate local venom comps by feature, not the shared engine globally. Plants stay rostered and visible. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. 

## T18: Brine elder treasure interactions and special relic loot

Decision: Designer, delegated; next_version. A one-off encounter/reward, unnecessary for ordinary mineral gathering.

Evidence: `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Buildings/RM_BrineElder.xml`, `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Items/RM_ElderTreasures.xml`. Called by: `src/RimMandrake/Utils/exotic_materials_census.py`, `src/RimMandrake/Utils/art/texture_regen_jobs.py`, `src/RimMandrake/Utils/art/fixtures/placeholder_detect_frozen.json`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Brine elder treasure interactions and special relic loot”, shipped false, under master/per-sea activation. Gate interaction, custom jobs, spawned treasures and rare-table treasure outputs. Preserve standing ruins as ordinary scenery if map placement requires them. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. 

## T19: Pool-sentinel territorial squirt encounter

Decision: Designer, delegated; next_version. A bespoke warning/attack loop added to already hazardous pools and normal predation.

Evidence: `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Races/RM_GreySeaFauna.xml`. Called by: `Engine XML loading / biome roster consumption; no explicit local caller found`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Pool-sentinel territorial squirt encounter”, shipped false, under master/per-sea activation. Gate external comp invocation for this mod only; retain the rostered creature body and existing pool geology. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. 

## T20: Chill cryoponics vat and floor growing bed

Decision: Designer, delegated; next_version. Custom agriculture buildings beyond ordinary native wild flora and supplied expedition food.

Evidence: `src/RimMandrake/TerminalBiomes/Source/RM_Building_CryoGrower.cs`, `src/RimMandrake/TerminalBiomes/Source/RM_Patch_ChillGrowers.cs`, `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Buildings/RM_ChillGrowers.xml`. Called by: `src/RimMandrake/TerminalBiomes/Source/RM_TerminalBiomesMod.cs`, `src/RimMandrake/TerminalBiomes/Source/RM_PlaceWorker_ChillFloorOnly.cs`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Chill cryoponics vat and floor growing bed”, shipped false, under master/per-sea activation. Gate construction, placement, growth overrides and cold-bath simulation; leave native wild growth independent. Never silently kill a saved crop. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. 

## T21: Chill catch-to-chemfuel refinery recipe

Decision: Designer, delegated; next_version. An industrial conversion economy, not fishing itself. Industrial catch remains nonfood.

Evidence: `src/RimMandrake/TerminalBiomes/Defs/RecipeDefs/RM_TheChillFuelChain.xml`. Called by: `Engine XML loading / biome roster consumption; no explicit local caller found`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Chill catch-to-chemfuel refinery recipe”, shipped false, under master/per-sea activation. Gate recipe availability and bill execution, including existing bills. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. 

## T22: Tarspool fraction separation and euphoric drug

Decision: Designer, delegated; next_version. A secondary manufacturing/drug chain beyond ordinary flora harvest.

Evidence: `src/RimMandrake/TerminalBiomes/Defs/RecipeDefs/RM_TheChillFuelChain.xml`, `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Items/RM_TheChillFloraProducts.xml`. Called by: `Engine XML loading / biome roster consumption; no explicit local caller found`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Tarspool fraction separation and euphoric drug”, shipped false, under master/per-sea activation. Keep stalk as ordinary harvest; gate separation bills, drug availability and new drug use/offers. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. 

## T23: Hydrocarbon-flesh manufacture and refining

Decision: Designer, delegated; next_version. An additional fuel industry beyond land, native life and current risk.

Evidence: `src/RimMandrake/TerminalBiomes/Defs/RecipeDefs/RM_TheChillFuelChain.xml`. Called by: `Engine XML loading / biome roster consumption; no explicit local caller found`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Hydrocarbon-flesh manufacture and refining”, shipped false, under master/per-sea activation. Gate recipes and active bills; keep industrial flesh non-ingestible and preserve saved stock. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. 

## T24: Stonewater powered extraction

Decision: Designer, delegated; next_version. A custom water machine beyond native plant harvest and imported colony supplies.

Evidence: `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Buildings/RM_ChillStonewaterExtractor.xml`, `src/RimMandrake/TerminalBiomes/Defs/RecipeDefs/RM_TheChillFuelChain.xml`. Called by: `Engine XML loading / biome roster consumption; no explicit local caller found`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Stonewater powered extraction”, shipped false, under master/per-sea activation. Keep stonewater ice and its existing ordinary cooking use; gate extractor construction and water-extraction bills. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. 

## T25: Hesuun wax procession and sheet extrusion

Decision: Designer, delegated; next_version. An independent timed animal-product mechanic. Hesuun remains in the roster.

Evidence: `src/RimMandrake/TerminalBiomes/Source/RM_Comp_WaxProcession.cs`, `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Races/RM_ChillWaxProcession.xml`. Called by: `src/RimMandrake/TerminalBiomes/validation.py`, `src/RimMandrake/TerminalBiomes/Source/RM_TerminalBiomesMod.cs`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Hesuun wax procession and sheet extrusion”, shipped false, under master/per-sea activation. Gate comp timing, extrusion and special sheet drops; keep creature population, movement and ordinary carcass. No eviction. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. 

## T26: Fuselight self-oxidising explosion

Decision: Designer, delegated; next_version. A custom explosive plant interaction. The ordinary luminous crystal plant and cold habitat still read.

Evidence: `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_TheChillFlora.xml`. Called by: `Engine XML loading / biome roster consumption; no explicit local caller found`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Fuselight self-oxidising explosion”, shipped false, under master/per-sea activation. Gate its explosive trigger and ignition exemption; keep natural glow and plant body. Do not redefine the shared no-oxygen fire law. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. 

## T27: Tarnn garden-defence wake

Decision: Designer, delegated; next_version. A separate thermal-agitation response beyond cold terrain and ordinary native life.

Evidence: `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Races/RM_TheChillFloorLife.xml`. Called by: `Engine XML loading / biome roster consumption; no explicit local caller found`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Tarnn garden-defence wake”, shipped false, under master/per-sea activation. Gate the external wake comp for this content only; preserve tarnn body, normal physiology and readable state. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. 

## T28: Twilight well-triggered flora spread, gloamurn charge and murkspindle light-wilt

Decision: Designer, delegated; next_version. Custom plant charge, spawning and killing loops beyond ordinary native growth.

Evidence: `src/RimMandrake/TerminalBiomes/Source/RM_TwilightFloraBehaviour.cs`, `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_TwilightUnderstorey.xml`. Called by: `src/RimMandrake/TerminalBiomes/Source/RM_MapComponent_WellLedger.cs`, `src/RimMandrake/TerminalBiomes/Source/RM_TerminalBiomesMod.cs`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Twilight well-triggered flora spread, gloamurn charge and murkspindle light-wilt”, shipped false, under master/per-sea activation. WellLedger.Opened/Closed call this directly: decouple callbacks. Replace dependency on event seeding with ordinary habitat placement for existing species. Static glows/harvest products stay; no default charge/wilt or mass plant deletion. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. 

## T29: Chill crater biome and lab-ending receiver content

Decision: Designer, delegated; next_version. Campaign ending content outside the sea visit promise; no worldgen or new planet.

Evidence: `src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_ChillCrater.xml`, `src/RimMandrake/TerminalBiomes/Defs/TerrainDefs/RM_ChillCraterTerrains.xml`. Called by: `src/RimMandrake/TerminalBiomes/validation.py`, `src/RimMandrake/Utils/sekkulaath_rising_note_check.py`, `src/RimMandrake/Utils/warlab_garrison_note_check.py`, `src/RimMandrake/Utils/mineral_matrix/prereview_harness.py`, `src/RimMandrake/Utils/mineral_matrix/check_matrix.py`, `src/RimMandrake/Utils/mineral_matrix/gen_matrix.py`, `src/RimMandrake/Utils/art/biome_worldfaces.py`, `src/RimMandrake/TerminalBiomes/Patches/RM_AcousticPayload_TerminalBiomes.xml`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Chill crater biome and lab-ending receiver content”, shipped false, under master/per-sea activation. Keep defs for save compatibility; gate this mod's availability/receiver activation. Preserve the already-ruled regional permanent consequence if the campaign ending is enabled. Do not modify the external war-lab mod. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. 

## T30: Twilight skylight tenancy, claim buoys and ageing charts

Decision: Designer, delegated; next_version. Real-estate economy beyond temporary natural illumination.

Evidence: `design/Jawa/worldbuilding/biomes/the_twilight_deep.md`, `src/RimMandrake/TerminalBiomes/Source/RM_MapComponent_WellLedger.cs`. Called by: `src/RimMandrake/TerminalBiomes/Languages/English/Keyed/RM_TwilightLightEconomy.xml`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Twilight skylight tenancy, claim buoys and ageing charts”, shipped false, under master/per-sea activation. Audit foreign callers and gate claims/charts/rent/jobs/letters, not natural lifecycle. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. Resolve the foreign adapter first; historical build claims alone cannot pass either arm.

## T31: Lid-dark crisis and theatrical gardener-passing events

Decision: Designer, delegated; next_version. Special lore/weather episodes beyond minimal roof tending and ordinary well replacement.

Evidence: `src/RimMandrake/TerminalBiomes/Source/RM_MapComponent_WellLedger.cs`. Called by: `Promised by cited design; adapter unavailable in this checkout`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Lid-dark crisis and theatrical gardener-passing events”, shipped false, under master/per-sea activation. Keep no-roof-without-gardener representation; gate special darkness events and bonus lifecycle callbacks. No perpetual freeze of ordinary wells. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. Resolve the foreign adapter first; historical build claims alone cannot pass either arm.

## T32: Chill warmth trails and immune-system shocks

Decision: Designer, delegated; next_version. Multiple triggered hazard/reward systems beyond ordinary brutal cold and drowned aurora.

Evidence: `design/Jawa/worldbuilding/biomes/the_propane_lake_floor_sitting_agenda_2026-10-02.md`. Called by: `Promised by cited design; adapter unavailable in this checkout`.

Work: retain code and defs in the tree. Provide a separate effective Mod Setting labelled “Next version: Chill warmth trails and immune-system shocks”, shipped false, under master/per-sea activation. Require external dependency owner to expose gates; separate native iliss normal bite and atmosphere from trail-triggered attacks or warmth-triggered rewards. Gate availability as well as ticking; an unbuildable recipe that still appears as an ordinary offer fails this ticket. For settings already present, change the shipped default and the missing-value Scribe default together. Existing saved opt-in values require a readable migration decision, never silent deletion of pawns or inventory.

Acceptance test: On a fresh map at shipped defaults with all kept features active, a resolved-state scan finds no newly spawned extra objects, active extra jobs, extra letters or incidents, available extra build/bill/research/trade offers, or lingering side effects; the log is clean. In an isolated copy with this next-version setting on (and required parent features enabled), the declared extra path can be entered and its objects/jobs/letters/incidents appear where applicable. Turn it back off mid-job and reload: new work stops, held contents survive, no restriction remains and the log is clean. Rostered ordinary animal/plant bodies and compatibility defs are permitted; their deferred behaviours and special products are absent. Resolve the foreign adapter first; historical build claims alone cannot pass either arm.

## T33: Recommend retiring inert cross-biome controls

Designer recommendation only: they have no consumer and offer no experience. Evidence: `Source/RM_TerminalBiomesMod.cs` explicitly groups them as not wired, and its UI and ExposeData are their callers. Keep code and serialized fields; until the owner decides, leave controls default false and labelled unsupported/next version. Do not build cross-biome behaviour.

Acceptance test: Fresh-map default state has crossBiomeEnabled false, no cross-biome jobs, incidents, letters or state changes, and a clean log. Turning the retained compatibility option on still reports unsupported/not implemented rather than falsely claiming an active feature. No on-state behaviour-presence test exists because no implementation exists; this is a retirement recommendation for an inert promise, not a request to invent it.

## T34: Chill aurora-surge shock and harvesting event

Historical implementation claimed in `the_propane_lake_floor_sitting_agenda_2026-10-02.md`; source unavailable. Resolve the external entry points before applying this switch-off. Keep the ordinary drowned-aurora picture and cold floor independent. Gate event dispatch, weather damage, harvest drops, jobs and letters behind a labelled next-version setting default false; preserve code and defs.

Acceptance test: Fresh-map default state with all kept systems on has no surge incident, shock processing, harvest reward, special job or letter; normal aurora still displays and the log is clean. With the next-version option on, its normal declared trigger produces the event and harvest path; switching off mid-event and reloading stops its new effects without deleting actors or saved inventory. The unavailable adapter must be resolved to execute this test; historical claims do not pass it.

## T40: Situation recorder and transition adapter

Work: Needed by B1, B3-B8 and M1. Extend the existing validation.py inventory into an instrument with actual map/layer, holder identity, job completion, health/water/light/growth, weather, gate, warning and Scribe transition records. The existing script says NEVER RUN LIVE YET and many checks only test defs. No def presence or kernel clone may masquerade as a working game transition.

Acceptance test: Break a catch pairing, drop a warning, permit source-map movement after transfer and make roof-over-sink recovery true in separate mutant adapters: each corresponding bar reading refuses. The production adapter records ordinary entry, carry, rescue, holder travel, off/on, actual save/reload and re-entry across the declared M1 regimes without forcing effects. Logs identify source and observed outcome separately.

## T41: Channel and landing geometry instrument

Work: Needed by B1, B5, B6, B7 and M2. Export generated flow/lane/band/sink grids, actual bed/bank terrain, elevation, obstacles, PathGrid reachability, ship landing reservations and weir arrest. Replay real field authoring; never generate planets. Add entry-phase timing and ordinary pawn path traces.

Acceptance test: Match game exported fields cell for cell for withheld generated local-floor layouts; displacements, arrest and sink arrivals match at the declared timing tolerance in M2. A crossing through a wall, an uncovered current boundary, a landing intersection and a no-safe-bank layout each produce a failing witness.

## T42: Whole-mod season recorder and calibrated models

Work: Needed by B8, M3-M5 and all unknown whole-system meetings. Capture every kept gate, native actors, resource stocks, growth, completed tasks, current transitions, warnings, light state, exposure, actual ticks and errors. Rendering-only speed-up is allowed; do not shortcut simulation clocks.

Acceptance test: Record full-map season traces for all four seas at defaults, including mid-run reload and reversed main action order. Withheld real traces agree with the models under their stated criteria. A missing native-water classification, runaway planting, blocked replacement site and non-advancing actor each yield a causal failure report rather than PASS. Save calibration fingerprints and clearly label predictions versus game observations.

## T43: Locate or supply minimal gardener/lid tending contract

Work: Needed by C21 and B7. Source search found NotifyGardenerPassAdvance hooks but no gardener implementation. First resolve deployed dependency/source; if absent, specify/build only the persistent keeper representation, ordinary tending and its link to the living lid. No boss encounter or theatrical passage is required. Retain frozen no-roof-without-gardener law; do not make the roof a permanent plant.

Acceptance test: On an ordinary Twilight visit, actual persistent keeper/tending state is inspectable and visibly attributable to the roof, survives reload and does not depend on optional lid-dark/pane/tenancy code. A fixture with keeper absent while roof persists fails B7. No pawn disappears without a readable transition/sign.

## T44: Finish channel terrain, safe arrival and rescue specification

Work: Needed by C22-C25, B1, B5 and B6. RM_ChannelBed and RM_FordStones are looked up but no defs were found under src/; RM_BankSilt is present. Define readable bed/margin/bank/sink pictures matched to authoritative membership. Replace hatch-only exclusion with actual reserved hull/access geometry. Define terminal basin overflow and reject rather than unchecked placement. Rescue means outside dangerous liquid plus safe shelter/carrier; generic Roofed alone is insufficient. No new cargo or bank-fertility engine.

Acceptance test: Across M2 placement/phase sweep, normal entry cannot be a harmless centre crossing; live water never crosses walls, a safe bank route survives surge and a legal ship unload is clear. Roof-over-live-sink is not rescue; a blocked basin never silently loses a pawn or deposits it through walls. Current movement and rescue predicate survive Scribe replay and no extra path is needed.

## T45: Resolve layer, liquid and native-physiology contracts

Work: Needed by C02-C06, B1, B3, B4 and M4. Scald SteamLock_BiomeWiring targets a background sea, not a demonstrated neighbouring beach carrier. Locate the current DivingInteraction/SeaShores/FlowWorks implementations before changing any engine. Contract: beach steam, calm floor bubbles, hot liquid contact, ordinary ambient heat, no per-biome sun and no potable Scald margin. All native species can use their own environmental water. Chill no oxygen, native cold tolerance and ordinary safe hull atmosphere remain land support, independent of thermal-defence/surge extras.

Acceptance test: Resolved runtime state demonstrates layer-correct delivery, no underwater rain, no local solar override, no drinking job from Scald body or margin, and paid boiling contact distinct from ambient heat. Native versus visitor cases in M4 reproduce real health/water transitions. The cold floor remains playable with its ordinary protective environment while every deferred hazard/reward loop is off.

## T46: Decouple natural well lifecycle and native flora from light economy

Work: Needed by C10, C19, C20, B3 and B7. Retain finite years-scale lifecycle from frozen lore, ordinary eligible replacement sites, natural glow and habitat-placed flora. Week-scale current kernel defaults are build tuning, not authority over the frozen years statement. WellLedger calls TwilightWellFlora and reads player mobile glowers for suulk pressure: sever those extra dependencies. Event-only flora gets ordinary placement, retaining species; no charge/wilt required. Use actual current membership for siting.

Acceptance test: At defaults with suulk, charge/wilt, pane fall, cages, culture, tenancy and darkness episode off, wells naturally initialize and pass all lifecycle boundaries in honest aged-save replays. Plants exist in valid habitats, gold/cold light caches restore through Scribe and the keeper remains present. No column is permanently owned; no lifecycle stalls when a moved-extra callback is stubbed out.

## T47: Resolve minimal inhabited campaign reveal

Work: Needed by D09 and B7. the_twilight_deep.md explicitly promises inhabited bottom dwellings, plots, moorings and lamplight before a full town. Locate existing Inhabited/campaign placement; this checkout does not supply it. Specify only the peaceful occupied bank fixture and ordinary tending needed for the reveal, as a campaign dependency, not RM franchise content. No rents, quests, raids or town economy.

Acceptance test: RM-only loads with a rich franchise-free sea. In campaign-enhanced state, an ordinary visit encounters occupied, tended, peaceful holdings on safe bank ground; an empty facade or hostile Compact fails B7. Occupancy and path reachability persist through reload and surge; no optional light-economy feature is needed.

## T48: Ordinary content tier and dependency binding audit

Work: Needed by C01, C07-C18 and inherited load/settings floor. Source example: RM_Eldspar harvest refers to RUT_AuroraGlass in RM_TheChillFlora.xml; do not launder a campaign reference into the standalone life promise. Resolve against actual composed defs and current naming authority, then decouple to a franchise-free product without invalidating existing saved identities. About.xml carries obsolete perched/outflow/world-generation prose and standalone dependency assumptions; proposal changes none of those files.

Acceptance test: Resolved RM ordinary content has no unguarded campaign/franchise reference, all required assembly classes and products exist in the supported composed load, and existing saved items load without silent deletion. Corrected player text agrees with terminal no-outflow geography. No second world or worldgen control is added.
