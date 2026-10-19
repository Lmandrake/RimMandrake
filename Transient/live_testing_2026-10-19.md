# Live testing 2026-10-19 (FOUNDRY)

- 05:03 start; skeleton written
- 05:04 game at main menu (Entry, no map); bridge FOUNDRY. Plan: load saved sites (test_site_saves.py) rather than quicktest worldgen on the 535 list (rimworld-debug-testing: quicktest on full list has crashed the process)
- 05:05 deploy dry-run (biomes compose): 37 drift lines; four-biome ones: Cauldron RM_VexxithDoor (xml+png), Contagion DonorPorts.xml, RM_Draftprint (xml+png), AB_TentacularPlant.png. Not deployed (lead: no deploy). Evidence: Transient/live_testing_2026-10-19/deploy_dryrun_biomes.txt
- 05:06 loading saved site contagion (RM_TestSite_contagion_v1) via test_site_saves.py load
- 05:10 contagion site loaded CLEAN (receipt Transient/live_testing_2026-10-19/site_contagion_receipt.json)
- 05:11 FINDING (SITE/HARNESS): the saved test sites are TIER saves (contagion_v1 = 22 mods, no Vehicle Framework). Loaded on the 535 list they read back CLEAN (check_map) but every spawn of a path-cost thing NPEs in Vehicles.PathingHelper.RecalculatePerceivedPathCostAt (Steel, RM_TallSlimyGrass, RUT_Webwork_Nest all fail; Plant_Grass spawns). So no suite can run on a tier save under this list. Evidence: Transient/live_testing_2026-10-19/tex_sump.json, Transient/live_testing_2026-10-19/tex_after_step.json.
- texture sanity on contagion site: UNMEASURED (could not spawn the two defs). Both defs RESOLVE live (get_defs 2/2: RUT_Webwork_Nest in mandrake.rut.shokkweaveeconomy, RM_TallSlimyGrass in mandrake.rm.biomes).
- SUMP A6 sump_living_map on contagion site: on/off both 'UNMEASURED: no clear (plant-free, unroofed) 12x12 patch of ordinary ground' (SITE).
- 05:11 next: load CANONICAL_ASHKARR_START_2026-10-18_DONORFREE_REPAIRED (542-mod save, VF in; backed up to D:\Luke\dev\_rmscratch\saves_backup_20261019_live, md5 recorded) and never save over it.
- 05:19 canonical 542-mod save loaded (ignoreModCompatibility; 7 retired donors missing) in ~200 s: map 3 RUT_ExtremeDesert tile 17007 tick 126814. Never saved over.
- 05:20 BLOCKER (not our mod; mod-list): Vehicle Framework's VehiclePathingSystem MapComponent fails to construct on EVERY map this session ("Could not instantiate a MapComponent of type Vehicles.VehiclePathingSystem" NRE in VehiclePathFinder..ctor via GeneratePathData, Player.log first at the contagion-site load). Consequence measured on the canonical 542-mod save too: any spawn of a thing with pathCost>0 (Steel 14, RM_TallSlimyGrass 15, RUT_Webwork_Nest) and any terrain change NPEs in Vehicles.PathingHelper.RecalculatePerceivedPathCostAt:367; Plant_Grass (pathCost 0) spawns. Not seen in Player-prev.log (04:28 session) - unknown whether that session ever built a map.
- texture sanity (Hive / AB_SlimeGrass): UNMEASURED. Could not spawn either def (VF NPE). jawa/texture_audit reads 'No dead texPaths' for both, but it is CLASS-BLIND (passes if the path resolves as a file OR a folder OR a directional set), so it cannot see a Graphic_Random-on-a-file or Graphic_Single-on-a-folder mismatch: not evidence. (Transient/live_testing_2026-10-19/texture_audit.json)
- SUMP A6 (sump_living_map on|off) on canonical map: UNMEASURED/HARNESS: ProofRewrite NPEs in the same VF terrain-change hook (TerrainGrid.DoTerrainChangedEffects -> Patch_VehiclePathing). On the tier site it was UNMEASURED/SITE (no clear 12x12 patch). (Transient/live_testing_2026-10-19/tex_sump_canonical.json)
- 05:20 running Contagion suite (northstar_driver, --no-record) on canonical map 3
- 05:21 Contagion run 1 REFUSED at preflight no_modal (VEF Dialog_NewFactionSpawning x~8 + Dubs minimap). Closed the faction dialogs; minimap reopens itself (GameUI, forcePause false) -> added to northstar_driver/preflight.py _BENIGN_WINDOWS (HARNESS fix). Re-running.
- 05:29 STOPPED by the lead (owner sees a blank screen with small white text). Contagion run 2 killed mid burn chain.
  Contagion run 2 partial rows (canonical map 3, retiled tile 17007 -> RM_Contagion; NOT certifiable, VF broken):
  spawner: site_ready_spawner / spawner_off_buds_nothing / spawner_buds_unfinished / unfinished_rolls_limbs_and_lifespan PASS;
  unfinished_dissolves_on_death FAIL ("a corpse persists (1)") -> unfinished_leaves_mulch (A4) UNMEASURED;
  off_when_setting_off UNMEASURED (safe_advance cancelled 1560/2000 ticks); retile_to_contagion, site_is_contagion PASS;
  burn_site_ready FAIL "fixture: no open pawn" (presumed SITE/HARNESS: VF spawn NPE) -> 8 burn rows UNMEASURED.
  The tile was left RETILED to RM_Contagion (site_restore never ran) - in memory only, nothing saved.
- Player.log: VF VehiclePathingSystem ctor NRE x3 from line 10548 (contagion tier-site load, 8496);
  first Root-level exception line 25278 (Update: MapDrawer.WholeMapChanged <- GlowGrid.GlowGridUpdate_First, 785 repeats)
  right after log_revive at 25277; second storm from 87724 (OnGUI/Update: PawnTweener.TweenedPosRoot via
  TooltipGiverList / ThingOverlays) during the Contagion burn-pad fixture (05:28:06-05:28:24).
