# FOUNDRY FlowWorks overnight 2026-10-05

## State
- started Mon Oct  5 23:04:24 PDT 2026

## Steps

## Bars

## Fixes

## Blockers
- 23:10 killed game; JawaBench built+deployed (deed2e5ca); FlowWorks DLL deployed (6b5eefe90 build); tier flowworks (10 mods) applied; launched via steam
- context: walk checklist is DRAFT (owner released hash 59681505d) -> modcheck can't GREEN until owner re-validates; v2 latest 203150 58P/1F (P4_ladder_frees); last ext run 201540: oil_pit_burns_occupant FAIL + fire_on_map surprises
- 23:13 game UP on flowworks tier; running v2 live run A
- 23:17 run A GREEN 59/59 (validation_v2_result_20261005T231740.json); run B for P4 flake check
- 23:22 run B GREEN 59/59 (232201). pushed 8fb5106e8; verify pass recorded on BASELINE_RUN_1. Next: extensions (core+rivers)
- 23:30 ext batch1 (11 chains): 23 PASS / 10 UNMEASURED: surprises from Anomaly Entities (toughspike/fingerspike) + unexplained colonist injuries; oil_pit_burns_occupant now PASS. Rerunning bottle_revert,dig_finds,machinery_hoses
- 23:44 ROOT CAUSE ext UNMEASURED: harness kill of Toughspike -> DeathActionWorker_Divide -> fingerspikes land mid-chain. Fix 055a0457b (vanish). Rebuilding JawaBench
- 23:45 untracked WIP src/RimMandrake/FlowWorks/{Defs,Source}/Machinery/Kits (21:18, not mine, uncommitted) had its XML in the game folder w/o the class in the DLL -> launch gate refused maps. Removed the GAME copy of RM_LiquidKits.xml only (repo untouched); restarted
- 23:55 ext run3 (11 chains) running in bg
- 00:05 ext3 still running (started 23:55), wrote river_site.py (river map founder) for rivers chains
- 00:08 ext3: 23P/3F/7U. FAILs: pit_fluid_effects (poison got {}), wall_faces (verts 76->76), dig_finds (forced cut no find). fleshbeast noise gone. Rerunning those 3 alone
- 00:14 ROOT CAUSE 3 FAILs: stale excavation from aborted run on same map (prep_plot doesn't reset engine cuts). Fix 810882cd0 ProofResetRect + dig force flag consumed. Redeployed (Kits WIP xml removed from game copy again)
- 00:22 ext5: 22P/1F/9U -> fixes d316e9755 (reset uses dug depth; prison chain vanishes its pawns). Rerun ext6
- 00:34 ext6: 24P/0F/9U (UNMEASURED = heatstroke on 38C tile + worldgen/VE). river_site.py founded mild river map (tile 162 Desert, map 1). Running rivers chains
- 00:35 rivers run1: 4P/2F/10U -> harness/proof fixes e6ae63376 (ProofShove ';', weir site off map edge). restart
- 00:39 RIVERS 16/16 PASS (5e7375011) on river_site map 4 (tile 304 TemperateForest). Next: all non-plot chains on this map
- 00:40 river_site mild-lat (map 5 tile 630). Running chains A (core 11 + rivers) then B (29 toggle/other chains) in bg
- 00:57 A: 30P/1F/18U (Norman fall/Blunt surprises = start colonists wander into pits; weir pool dropped=0 at (181,..)). B running
- 01:11 B: 24P/0F/35U (all env: leftover pawns, frostbite). weir FAIL root: plot T Soil paint cut across the river. Fixes 278983687 (sweep earlier chains' pawns, rivers first, tropical river_site). Full run next on fresh river map
- 01:21 ALL run (restart+river_site+49-ish chains) in progress
- 01:31 ALL still running
- 01:41 ALL still running
- 02:02 ALL (rivers first, sweep): 87P/7F/14U extension_result_20261006T020120.json. FAILs: pit_cover_fall light_does_not_spring_reinforced, flow_doors sluice_holds_small_only, toggle_pit_depth_draw off, pit_fill_effects water {}, toggle_tank_loop, fluid_identity_recorded, pit_prison_room capture_down. Isolating each
- 02:18 root causes: settings leak via guarded set_setting (superdeepCapture stuck False), factionless doors, cover None, census incl. river. Fixed 55e446ee8. flow_doors 6/6. Remaining: toggle_tank_loop asserts a non-existent mechanic (tankLoopEnabled gates bottle WorkGivers only) -> file item. Next: full rerun
- 02:18 filed FLOWWORKS_TANK_LOOP_ROW_WRONG_1; ALL2 rerun started (bg)
- 02:37 ALL2 running
- 02:53 ALL2: 72P/1F/35U (heatstroke on Desert tile; confinement FAIL = river cells inside plot B). rivers all PASS. -> river_site --dry (3aaa6b844); running EXT chains on a dry mild map
- 02:54 dry mild site map 3 (tile 45, 20C spring). EXT chains running (bg)
- 03:23 EXT still running, 1 surprise so far
- 03:37 EXT dry: 74P/3F/15U. fixes pushed (confinement source skip, geyser tiles, old colonists vanished). tank_loop filed. Rerunning residual chains on a new dry site
- 03:57 residual run on dry map 6 (16C spring) in progress
- 04:05 residual 16P/1F; filed CONFINEMENT_TOGGLE_VESTIGIAL_1. Final v2 core rerun on current DLL
- 04:14 v2 GREEN 59/59 (040914). plot chains: state PASS; canal_dry_obstacle pathCost row harness bug fixed (json.dumps). Read shots: pit occupants on south row/1x1 hidden by near-lip -> filed FLOWWORKS_PIT_OCCUPANT_HIDDEN_BY_LIP_1 (owner). Done; releasing bridge
