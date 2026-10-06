# WATCHER_CREATURES_MOD_1 build — FOUNDRY helper, 2026-10-06

Status: kit core + piinnok BUILT offline, NOT committed, NOT deployed, no live proof yet.

## Sweep (prior art)
- `WatcherKit|CompWatcher|RM_Watcher|piinnok` in src/: only the "§8, the piinnok hook" comment in
  CreatureBehaviors `RM_CompSandSwim.cs`. No watcher kit and no piinnok def existed.
- Reused, not re-invented: hide hediff shape (`RM_SandSubmerged`), job-with-one-finish-action
  (`RM_JobDriver_Burrow`), global Animal_PreWander insert (`RM_BurrowOnFire`), wander validator
  (`RM_JobGiver_WanderInShadeGrid`), comp injection (`RM_SandSwimStartup`), geophone
  (`RM_SandSwimUtility.SubmergedSwimmersNear`, bound by reflection), feeding (`RM_FilterFeedExtension`
  on RM_DeepSand, the likka likka's stack).
- Engine facts read on RimSage this pass: hermit crab `stationaryGraphicData` shape; lifestage graphicClass
  defaults to Graphic_Multi; `IsHiddenFromPlayer` blocks selection/draw/prey (FoodUtility);
  `ListFromXml` honours MayRequire on any child node; `GenSpawn.SpawningWipes` (Ethereal sign wipes
  nothing); Designator_Hunt / WorkGiver_HunterHunt / Orders `specialDesignatorClasses`.

## Mod created (standalone, no compose entry — owner ruling 2026-09-30)
`src/RimMandrake/Watchers/` packageId `mandrake.rm.watchers`, namespace `RimMandrake.Watchers`, no Harmony,
no compile-time reference to our other assemblies.
- Source: RM_WatchersMod (settings, scroll + maxOneColumn), RM_WatchersDefOf, RM_WatcherExtension
  (ConfigErrors), RM_CompWatcher (+ startup injection; medium backstop, orphan-hediff guard),
  RM_WatcherSign, RM_WatcherUtility, RM_JobGiver_Watch, RM_JobDriver_Watch, RM_JobGiver_WanderInMedium,
  RM_Flush (designator + workgiver + driver).
- Defs: RM_WatcherHidden; RM_WatcherSign_SandDimple; JobDefs Watch/Relocate/Flush; ThinkTree RM_Watchers
  (Animal_PreWander, prio 50); DesignationDef RM_WatcherFlushMark; WorkGiverDef RM_WatcherFlush (Hunting);
  Patch: Flush into Orders.
- Settings: master, hide+flinch, turn to face, stay on medium, geophone, flush marks hunt, flinch-radius
  scale, emerge-delay scale, max active per map (40).

## Creatures
- RM_Piinnok (ThingDef + PawnKindDef): deep sand only (Q1), two pictures stationary/body, no swimming
  sprite (Q2, design §5 trap), lock applies tame and wild (Q3), flush-only hunting (Q4). bodySize 0.15,
  group 2-4, flinch 6, watch 14, geophone >= 2.5. Other numbers PROVISIONAL (marked in XML).
- Cross-mod refs guarded: RM_DeepSand MayRequire flowworks; filter-feed extension + RM_Biosilica
  MayRequire mandrake.rm.biomes (CreatureBehaviors and Stillsand are composed there).
- Wave 2 members (thollim, tarruq, peeper, fessk, shiro) NOT touched: they go biome by biome at each sitting.

## Art
- `artpipe_state.py find piinnok`: 0 hits (20,592 entries; probe hawkbat hit). Nothing to install.
- PLACEHOLDERS: vanilla Odyssey hermit-crab textures (body/stationary/dessicated); dimple = vanilla
  Things/Filth/Grainy tinted. Owed: one artpipe job (peek pose with iris readable N/E/S, move sprite,
  dessicated, dimple).

## Validation
- winbuild.py Watchers: Build succeeded, 0 warnings, 0 errors; DLL + .srchash in Assemblies/.
- validate_patch.py Patches vs Core: 0 errors, 1 warn (unguarded Add on Core's Orders; Core always loads).
- validation.py static (PYTHONPATH=src/RimMandrake/Utils): PASS 0 findings; sanity probes (wrong medium,
  unscribed toggle, missing def) each produce a finding. Wreckage control also PASS.
- Live chains written, all UNMEASURED until a bridge run (state reads: hediff, sign, Rotation, CurJobDef).

## Deferred / open questions
1. "A better grade of biosilica": no def above RM_Biosilica exists; butchers to RM_Biosilica x3 PROVISIONAL.
   New grade, or this?
2. Taming: a wild piinnok hides from any tamer within 6, so the only window is the bolt after a flush.
   Is flush-then-tame the intended route (Q3 assumes it can be tamed)?
3. Roster row `RM_Piinnok` in RM_Stillsand is STILLSAND_BEDAZZLE_CONTENT_1's (needs MayRequire
   mandrake.rm.watchers); not added.
4. Validation walk `design/validation_walks/RimMandrake/Watchers.md` not written (outside this mod).
5. Not deployed; quicktest state-read proof (design step 8) owed.
6. Design §6 gives flinch radius as 3-12 cells; built as a 50-200% scale of each member's own radius.
