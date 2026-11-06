# TICKBURST guard audit: per-frame work under paused tick bursts

What: for item TICKBURST_PROVE_MANY_TICKS_ONE_FRAME, final.md §2.4. A bridge tool calls `TickManager.DoSingleTick()` many times inside one Unity frame while the game is Paused. Work that runs once per frame (`Root_Play.Update` -> `Game.UpdatePlay` -> `World.WorldUpdate`, `Map.MapUpdate`, `GameComponentUpdate`) runs once for the whole burst. This lists that work, says whether it is sim or visual, and what falls behind.
Sources: RimWorld 1.6 decompile (`rw16/` = /mnt/d/ClaudeWork/rimmandrake/decomp/rw16/all) and our C# under `src/`. Every line below is from grep.
Date: 2026-11-06. Census: design/RimMandrake/tickburst_2026-11-06/update_census.json (28 hits), made by src/RimMandrake/Utils/tickburst_guard_census.py.
Frame chain: rw16/Verse/Root_Play.cs:77 -> rw16/Verse/Game.cs:670 (TickManagerUpdate, returns at once when Paused: rw16/Verse/TickManager.cs:321), rw16/Verse/Game.cs:672 (WorldUpdate), :675 (MapUpdate), :678 (GameComponentUpdate). Tick body: rw16/Verse/TickManager.cs:357.

| G | per-frame work | where (file:line) | class | consequence under paused bursts | check |
|---|---|---|---|---|---|
| G1 | power-net registration, `UpdatePowerNetsAndConnections_First` drains `delayedActions` | rw16/Verse/Map.cs:1156, rw16/RimWorld/PowerNetManager.cs:114 | sim | New and removed power comps join or leave nets only at the next frame. Every tick of the burst runs on the old topology: a new link is late, an obsolete one keeps powering. No tick-side caller found (other callers are GenStep, MapDeiniter, gravship). | LINES connect and disconnect rows |
| G2 | `RegionGrid.UpdateClean` and `TryRebuildDirtyRegionsAndRooms` | rw16/Verse/Map.cs:1157-1158, rw16/Verse/RegionGrid.cs:40, :85, :129, rw16/Verse/AutoBuildRoofAreaSetter.cs:44 | sim | Mostly self-healing: region readers (`DirectGrid`, valid-region lookups) rebuild lazily on access, and the roof setter rebuilds each tick. Readers that use `_NoRebuild` paths or cached rooms can see stale rooms until a lazy reader runs. Per-consumer trace UNMEASURED (not done in this pass). | P_pits room rows; audit list |
| G3 | glow grid recompute (Unity jobs, `Complete()` inside the update) | rw16/Verse/Map.cs:1159, rw16/Verse/GlowGrid.cs:412, :463, :484 | sim | Dirty cells from a lamp toggle stay at the old glow for the whole burst. Sim readers of `GroundGlowAt` (plant growth, sowing, darkness thoughts, stats) see the stale value: too bright or too dark. | glowtank with the lamp toggled |
| G4 | `SkyManagerUpdate` sets `curSkyGlowInt` | rw16/Verse/Map.cs:1155, rw16/Verse/SkyManager.cs:73 (only other writer :116 `ForceSetCurSkyGlow`) | sim | Sky glow freezes at the frame's value for the whole burst. A burst over dusk keeps day light: plants grow, solar makes power, sanguophage sun and darkness checks read the old sky. Shader and overlay parts are visual. | glowtank from dusk; consumers listed below |
| G5 | world and component updates: `CompDissolutionEffect_Goodwill` and `_Pollution` in `WorldUpdate`; `MapComponentUpdate` overrides | rw16/RimWorld/CompDissolutionEffect_Goodwill.cs:71, rw16/RimWorld/CompDissolutionEffect_Pollution.cs:51, rw16/Verse/Game.cs:672, rw16/Verse/Map.cs:1202 | sim | Dissolution goodwill and pollution effects run once per frame, so a burst applies them once, not per tick. Our 17 `MapComponentUpdate` overrides (census) also run once per burst; which of them change sim state is per-file and UNMEASURED here. Both Dissolution classes are in the census. | census below; both classes present |
| G6 | background path and grid jobs | rw16/Verse/PathFinder.cs:309, :318 (`ForceCompleteScheduledJobs`), :327-328 (schedule) | sim | Path jobs are completed and scheduled inside `PathFinderTick`, which runs per tick from `MapPreTick` (rw16/Verse/Map.cs:958). So the barrier is per tick, not per frame. Results arrive one tick later, same as normal play. Low risk. | read only; no extra row |
| G7 | `Pawn_JobTracker.StartJob` loop guard | rw16/Verse.AI/Pawn_JobTracker.cs:258, :266, :267 | sim | When Paused, a job counts toward the 10-jobs-per-tick loop error only if the last job was given in the same frame (:258). In a burst every tick shares one frame, so every job counts, which is what unpaused play does too. `JobTrackerTick` resets the counter every tick (:134), so a burst counts per tick like normal play. Expected: no extra loop errors. Verified in 1.6. | count job-loop errors per arm in P_pits |
| G8 | `Paused` true while ticking: direct `Paused` and frame readers | rw16/RimWorld/FleckMaker.cs:106, rw16/RimWorld/QuestPart_EndGame.cs:22, rw16/Verse/PawnRenderUtility.cs:234, src/RimMandrake/FlowWorks/Source/Superdeep/RM_PocketGrid.cs:216 | sim | Code that skips work when Paused also skips it during a burst. Fleck puffs are visual. `QuestPart_EndGame` (end-game timer) and our `RM_PocketGrid` are sim and may stall or differ. Our once-per-frame caches (list below) do their work once per burst. | grep list below; RM_WallReach is precedent |
| G9 | 1.6 variable tick rates and camera | rw16/Verse/Building.cs:106 (`MinTickIntervalRate`), rw16/Verse/Entity.cs:25 (`TickInterval(int delta)`), rw16/Verse/GenTicks.cs:117 | sim | Tick interval rate depends on distance to camera in 1.6; the camera does not move during a burst, so rates stay pinned for the whole burst. The camera-rate source line was not found by grep: UNMEASURED. | camera pinned and recorded in provenance |
| G10 | autosave and long events | rw16/Verse/TickManager.cs:471, rw16/RimWorld/Autosaver.cs:31, :36 | sim | Autosave is decided per tick but only queued as a long event; it runs at a later frame, after the burst. Mid-burst long events do not run until the frame ends, so their effects land late. | autosave off and recorded; latch trials flagged |
| G11 | tweener, draw positions, sound and effecters | rw16/Verse/PawnTweener.cs:56, :65, :76, :88, rw16/Verse/Map.cs:1160-1161 (`LordManagerUpdate`, `ProcessPostTickVisuals`), :1196 | visual | Pawn draw positions jump to the root after a burst (frame and tick gap at :65). Post-tick visuals and fleck updates run once. Shared-RNG use in sound or effecter callbacks was not traced: UNMEASURED. `LordManagerUpdate` content not read: UNMEASURED. | audit list only; screenshots to L-e |

## Update override census

28 hits; rw16 11, src 17. String literals and comments are skipped (selftests that quote method headers are not hits).

- `CompDissolutionEffect_Goodwill.WorldUpdate` rw16/RimWorld/CompDissolutionEffect_Goodwill.cs:71
- `CompDissolutionEffect_Pollution.WorldUpdate` rw16/RimWorld/CompDissolutionEffect_Pollution.cs:51
- `World.WorldUpdate` rw16/RimWorld.Planet/World.cs:236
- `WorldComponent.WorldComponentUpdate` rw16/RimWorld.Planet/WorldComponent.cs:14
- `WorldComponentUtility.WorldComponentUpdate` rw16/RimWorld.Planet/WorldComponentUtility.cs:9
- `GameComponent.GameComponentUpdate` rw16/Verse/GameComponent.cs:7
- `GameComponentUtility.GameComponentUpdate` rw16/Verse/GameComponentUtility.cs:8
- `GameComponent_DebugTools.GameComponentUpdate` rw16/Verse/GameComponent_DebugTools.cs:14
- `MapComponent.MapComponentUpdate` rw16/Verse/MapComponent.cs:12
- `MapComponentUtility.MapComponentUpdate` rw16/Verse/MapComponentUtility.cs:8
- `WorldComponent_GravshipController.WorldComponentUpdate` rw16/Verse/WorldComponent_GravshipController.cs:399
- `RM_MapComponent_AcousticReading.MapComponentUpdate` src/RimMandrake/AcousticScanner/Source/RM_MapComponent_AcousticReading.cs:42
- `RM_MapComponent_AtmosphericBase.MapComponentUpdate` src/RimMandrake/AtmosphericBase/Source/RM_MapComponent_AtmosphericBase.cs:241
- `RM_MapComponent_ExplosiveGrowth.MapComponentUpdate` src/RimMandrake/ExplosiveGrowth/Source/RM_MapComponent_ExplosiveGrowth.cs:404
- `RM_LiquidSurface.MapComponentUpdate` src/RimMandrake/FlowWorks/Source/RM_LiquidSurface.cs:241
- `RM_MapComponent_Excavation.MapComponentUpdate` src/RimMandrake/FlowWorks/Source/RM_MapComponent_Excavation.cs:2828
- `RM_MapComponent_Hoses.MapComponentUpdate` src/RimMandrake/FlowWorks/Source/Hose/RM_MapComponent_Hoses.cs:1564
- `RM_MapComponent_SuspensionBridges.MapComponentUpdate` src/RimMandrake/FlowWorks/Source/Pits/Suspension/RM_MapComponent_SuspensionBridges.cs:898
- `RM_PitLipOcclusion.MapComponentUpdate` src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitLipOcclusion.cs:318
- `RM_MapComponent_CordGraph.MapComponentUpdate` src/RimMandrake/GimmeSomeSlack/Source/RM_MapComponent_CordGraph.cs:1011
- `RM_MapComponent_Aerial.MapComponentUpdate` src/RimMandrake/GimmeSomeSlack/Source/Aerial/RM_MapComponent_Aerial.cs:537
- `RM_MapComponent_ConduitRuns.MapComponentUpdate` src/RimMandrake/GimmeSomeSlack/Source/Aerial/RM_MapComponent_ConduitRuns.cs:54
- `RM_MapComponent_HullBoltMarks.MapComponentUpdate` src/RimMandrake/RustCathedral/Source/Hum/RM_HullBolts.cs:960
- `RM_MapComponent_BiomeAttitude.MapComponentUpdate` src/RimMandrake/RustCathedral/Source/Hum/RM_MapComponent_BiomeAttitude.cs:95
- `RM_MapComponent_MirrorLight.MapComponentUpdate` src/RimMandrake/SolarMirrors/Source/RM_MapComponent_MirrorLight.cs:709
- `RM_MapComponent_WetSand.MapComponentUpdate` src/RimMandrake/Stillsand/Source/RM_StillsandWater.cs:358
- `RM_MapComponent_SkyPastures.MapComponentUpdate` src/RimMandrake/TheForge/Source/RM_ForgeSkyPastures.cs:266
- `MapComponent_EmpireSearch.MapComponentUpdate` src/RimUtinni/EmpirePursuit/Source/EmpireLadder.cs:631

## Sim consumers of per-frame state

CurSkyGlow readers (G4), decompile:
- rw16/Verse/GlowGrid.cs:291 (`GroundGlowAt`, so every glow reader below)
- rw16/RimWorld/CompPowerPlantSolar.cs:17 (solar output)
- rw16/RimWorld/SanguophageUtility.cs:113 (sun exposure)
- rw16/DarknessCombatUtility.cs:64 (darkness combat)
- visual: rw16/Verse/SectionLayer_Darkness.cs:42

GroundGlowAt sim readers (G3, G4): rw16/RimWorld/Plant.cs:220, :245, :356; rw16/RimWorld/WorkGiver_GrowerSow.cs:97; rw16/RimWorld/StatPart_Glow.cs:80; rw16/RimWorld/ThoughtWorker_SwallowedByDarkness.cs:18; rw16/RimWorld/CompSightstealer.cs:109; rw16/RimWorld/GameCondition_UnnaturalDarkness.cs:165, :174; rw16/RimWorld/InfestationCellFinder.cs:93; rw16/RimWorld/RCellFinder.cs:1823; rw16/RimWorld/StatWorker_ContainmentStrength.cs:136; rw16/RimWorld.QuestGen/QuestPart_Noctoliths.cs:138.

CurSkyGlow readers, ours: src/RimMandrake/FlowWorks/Source/Machinery/CompLiquidConverter.cs:178; src/RimMandrake/LuminousPigment/Source/DeepfireWornGlow.cs:145; src/RimMandrake/LuminousPigment/Source/MapComponent_DeepfireLights.Visibility.cs:27; src/RimMandrake/Watchers/Source/RM_WatcherCues.cs:141. Comment-only mentions (SunlightScald, SunScald, AuroraLight) are not readers.

RealTime.frameCount / Time.frameCount and Paused readers (G7, G8), decompile, non-UI:
- rw16/Verse.AI/Pawn_JobTracker.cs:258, :266 (sim, G7)
- rw16/Verse/PawnTweener.cs:56, :65, :88 (visual)
- rw16/RimWorld/Building_Bed.cs:407 (owner-change once per frame)
- rw16/RimWorld/FleckMaker.cs:106 (visual), rw16/RimWorld/QuestPart_EndGame.cs:22 (sim), rw16/Verse/PawnRenderUtility.cs:234 (visual)
- Other hits are UI, debug strings or caches (e.g. rw16/RimWorld/ListerHaulables.cs:240 and rw16/RimWorld/Storyteller.cs:360 are inside `DebugString`).

Ours (grep excluding SelfTest, first 40 lines only; the rest UNMEASURED in this pass):
- sim-risk: src/RimMandrake/FlowWorks/Source/Superdeep/RM_PocketGrid.cs:216 (Paused); src/RimMandrake/GimmeSomeSlack/Source/Aerial/CompAerialAnchor.cs:472 (autolink once per frame); src/RimMandrake/GimmeSomeSlack/Source/RM_MapComponent_CordGraph.cs:57, :124, :274 (graph built once per frame); src/RimMandrake/FlowWorks/Source/Hose/RM_MapComponent_Hoses.cs:922, :1620, :2057, :2361
- visual or probe: src/RimMandrake/FlowWorks/Source/RM_LiquidSurface.cs:248; src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitLipOcclusion.cs:192, :324; src/RimMandrake/AtmosphericBase/Source/RM_MapComponent_AtmosphericBase.cs:246, :287; src/RimMandrake/AtmosphericBase/Source/RM_AtmosphericCompositor.cs:286; src/RimMandrake/TheForge/Source/RM_ForgeSkyPastures.cs:286; src/RimMandrake/GimmeSomeSlack/Source/Aerial/ConduitStylePicker.cs:273; src/RimMandrake/GimmeSomeSlack/Source/GimmeSomeSlackProbe.cs:381, :489
