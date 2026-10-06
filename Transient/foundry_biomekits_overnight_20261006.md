# FOUNDRY biome-kits push — overnight 2026-10-06

Item: `BIOME_KITS_PUSH_TO_TEST_1` (claimed+started). Offline only; bridge not used.

## census (kit mods, 2026-10-06)
All 8 kit folders (TheForge, TerminalBiomes[Scald], Miasma, TheSump, FeverWood, RustCathedral, Greentide,
Scarlands[Warscar]) + EnvironmentalHazards/CreatureBehaviors: About.xml ok, Mod Settings class present,
validation.py present, every .cs in an explicit-compile csproj listed, every DLL srchash MATCH,
validate_patch over all kit Patches/ vs FULL.LATEST modlist: 27 files, 0 errors.
Walks were missing for Miasma and Scarlands -> written (eb4b3e41f).

## last live results (situational_rerun 2026-10-03/04) — FAILs classified
- TheForge cycle_walk.rain_forces_boiling_weather_and_floods: MOD defect, fixed 86c0e1d06
  (WeatherDecider waits 4000 ticks before a forced weather; bursts are 20-40 min). Needs live rerun.
- TheSump defs_resolve: RM_CapstanTurret_PitRigged / RUT_PreservedDrawJoint notFound = deploy drift
  (run's deploy_start reported 2 new files not yet loaded); defs exist in src and in deployed Biomes.
  Not a mod defect; clears on a rerun after a load.
- Everything else non-pass is UNMEASURED (needs generated map / seeded state) or surprise-aborted (wildlife bites).

## work done
- 86c0e1d06 SnapForcedWeather in RM_GameCondition_WeatherPulse (+ ForgeCycle phase entry); EH+Forge DLLs rebuilt
- eb4b3e41f Miasma.md + Scarlands.md walks; Miasma script round-trips all 18 settings
- 37c96a7dd TheForge script: cycle chains declare own letters/fires; wind-down extinguishes (HARNESS)
- 4b6127995 CreatureBehaviors script: all 96 settings at defaults, 64 bools round-trip (was 13)
- 6f08b61ae TheForge script drops other suites' permanent weather locks before the cycle (SITE)
- f983aca2b Greentide seeded mire_escalation chain; RM_Mired added to ambient hediffs (detectors 96/96)
- run_selftests 192/192 PASS

## findings for the bridge holder (not fixed: live-only / harness)
- FeverWood + Greentide + TheForge runs were aborted mid-chain by RM_Kurreth bites. Forge's surprise
  frame (Transient/modcheck/surprises/20261003T191839/TheForge__cycle_arms__colonist_died__t36006__001.png)
  shows "The kurreth hive has noticed you": the test map carries a FeverWood ant-hive dungeon
  (genstep is biome-gated to RM_AntHiveBiomeExtension, so the site map is/was a FeverWood map).
  SITE defect: bland-world kill_hostiles does not stop the hive's swarm re-emerging.
- Same frame: ~18 "forced weather" conditions listed while paused. jawa/weather_set lock ends the old
  lock with Duration=TicksPassed, which only leaves the list on the next tick; repeated lock calls while
  paused stack them, and WeatherDecider.ForcedWeather takes the LAST non-null. Possible second cause of
  a wrong weather read; unproven.
- Deployed RimMandrake.Biomes carries the PRE-fix EnvironmentalHazards/TheForge DLLs; deploy before
  the next Forge run (game is up on flowworks tier now, so not deployed by me).

## blocked / needs owner
- Nothing needs the owner. Live-gated: deploy Biomes (new EH/Forge DLLs) + rerun the 8 kit suites.
- Still owed as tools/items (not filed by me): GREENTIDE_FRENZY_SEED_1, MIASMA_WARDEN_SUCCESSION_SEED_1
  (walk-named), RustCathedral attitude-read tool, Scald S3 (FISH_BESTIARY), FeverWood F5 design call,
  Greentide M10 (EXPLOSIVE_PLANT_GROWTH_1).
