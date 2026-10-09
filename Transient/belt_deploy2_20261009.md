# Belt deploy sitting 2 — 2026-10-09

Progress (appended per step).

- 1 bridge: FOUNDRY took it 08:51; clone reconciled to 985bf6b18. Repo copy of UtinniPatches RUT_FoundrySalvageCache.xml already deleted at 41a77e868.
- 3 deploy: game killed PID 32872 08:53; per-mod --apply 11 files; --apply --prune on LuminousPigment/SWBestiary/ShipVermin/StarWarsPatches/UtinniPatches (55 files, git-deleted files removed incl. game copy of UtinniPatches RUT_FoundrySalvageCache.xml). FlowWorks/WreckedMachines game-only files kept (never in git).
- 3b composed biomes --apply --prune: 13 files. NOTE: per-mod prune also deleted 2 game-only SWBestiary files never in git (Defs/AbilityDefs/RSW_SiloothAcidSpit.xml, Patches/Silooth/Silooth_Warbeast.xml) — no copy found; nothing in src references them.
- 4 list: live ModsConfig 622 = FULL.LATEST 614 + 8 new mandrake.rut.*artoverride mods (written 08:54 by another writer), same order; kept as is, no restore.
- 4 launched 09:01 via steam.exe -applaunch 294100 on the 622-mod list
- 3c post-apply re-plan: not captured (file empty); per-mod apply reported VERIFIED in sync
- 4 loading 09:11 (1430 log lines, no token yet)
- 4 Bridge token 09:19 (load ~18 min)
- 5 harvest (--since 09:01 --stale-ok: dump 621 vs ModsConfig 622, the 1 = uninstalled vlvop.tormentmaster.expansion, as at 07:32). Delta vs 07:32 full-list run:
  - static-ctor dead 1 -> 0 (VanillaGravshipExpanded.GravshipHelper no longer dies)
  - cross-refs 3 -> 0 (EmptyAICore x2, RUT_DeadCreep fixed)
  - ConfigErrors 42 -> 36: gone RUT_FoundrySalvageCache x6, RM_Illisk x2; NEW RUT_DyingCreep x2 ("Nutrition == 0 but preferability is RawBad") — fixed in repo (ingestible preferability NeverForNutrition), deploys next game-down
  - patch failures 6 -> 4 (BMT_GreyLady conditional, BMT_Thrumbungus sequence fixed; now below baseline 5)
  - tex 3 = 3 (RotSpecies/Swarmling, owner art), Scribe stale 122 = 122, Harmony 1 = baseline
  - RUT_Caravan_Junkers / RM_HalfExtractedCore tradeability line: 0 hits in Player.log
  - FIRST exception unchanged: line 1224 NRE in FactionDef.ConfigErrors (CannibalPirate, PirateYttakin) via donor Worldbuilder postfix; then VBE KeyNotFound '-1§Vanilla'
- 6 RM_SettingsOpenSmoke at menu: opened=80 failed=(none) nosettings=3 done=True; log regex 0 settings exceptions naming ours -> MOD_OPTIONS_RETROFIT_1 A1 PASS (run-1@full-622; item is closed, no criterion manifest)
- 6 quicktest map on the full list (09:21, rimworld/start_debug_game_ready). Reads in Transient/belt_deploy2_mapchecks_out_20261009.txt:
  - ProofHarvest true;Anchor;34 -> designatable False | workgiver False | yield 3 | weaveNear 0->3 | spawned 1. ProofHarvest picks a cell near MAP CENTRE; ProofHarvestDesignate (cell beside a colonist) -> designatable True, and the real colonist cut (2000 ticks) -> nodePresent False | weaveNear 3 | lastYield 3. So the mechanic works; the hook's centre-cell pick is what reads False (cause not measured). A1 partial.
  - ProofHarvest true;Web;0 -> yield 2, spawned 0. false;Anchor;0 -> designatable False, yield 0 -> A2 PASS.
  - RUT_FoundrySalvageCache resolves once, from mandrake.rm.biomes, thingClass Building (no duplicate).
  - Warcasket caravan: RUT_Caravan_Junkers resolves; RM_HalfExtractedCore NOT loaded because mandrake.rm.warcasket is not on the owner's full list (MayRequire skips the stock row) -> tradeability fix unmeasurable on this list; 0 tradeability lines in log.
  - CreatureBehaviors: 0 ConfigErrors lines naming VerminBreeder/ParentalEnrage/DefensiveDischarge/PlantAlarm on full list (criterion asks minimal list -> partial).
  - Death bursts: 0 error lines naming the 6 AA species / DeathBurst / Flashstorm on full list; race.deathAction unreadable via get_defs -> A1 partial.
- 7 game left UP on the full list (622) with a quicktest map; bridge released 09:33
