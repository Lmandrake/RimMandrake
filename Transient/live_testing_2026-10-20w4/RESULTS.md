# Live 2026-10-20 (w4): one cold load for Wave 4 324 list + world textures v2 + StarWarsRaces heads

FOUNDRY, bridge held throughout. Items: WAVE4_LIST_DEPLOY_FIFTY_FEWER_PASSENGERS, WORLDMAP_BIOME_APPEARANCE_1, XENO_HEADS_VERIFY_FEWER_EARS_MORE_ART.

## Deploy (game DOWN, 07:59)
- Live ModsConfig backed up to `infrastructure/state/modlists/ModsConfig.LIVE_BACKUP_2026-10-20_pre_wave4.xml` (374).
  `ModsConfig.FULL.WAVE4_324_2026-10-20.xml` copied over live and over `ModsConfig.FULL.LATEST.xml`. Parsed back: 324 / 324, md5 fa62a272 for both.
- Cherry Picker: the old SHIP (1,747) saved as `CherryPicker.SHIP.PRE_WAVE4_1747.xml`. The WAVE4 candidate became `CherryPicker.SHIP.xml` and `cherrypicker_swap.py --ship --apply` wrote 1,723 cuts live.
- src: `--compose biomes --apply` sent 28 files (26 world textures plus RimMandrake.Biomes.dll and .srchash) and read back VERIFIED. `--mod UtinniPatches --mod StarWarsRaces --apply` sent 6 files (RUT_Umbra.png, 3 Ortolan masks, SW_HeadTypes.xml, RimMandrakeXenotypes.xml) and read back VERIFIED. Neither plan held any other seat's file.
- Commits: 7a0d4309f (textures and shader swap), 4c96e58c5 (lists).

## Cold load (Steam, 08:00 to 08:13, about 13 min)
- harvest (`harvest_menu.txt`): ModsConfig 324 held. Dead mods 0, defs discarded 0, xref 0, Harmony patch failures 0 (baseline 1),
  patch-op failures 0 (baseline 5), config errors 13 (baseline 17), texture failures 0.
  "Stale saved data" 7 lines are `AG_*` gene and xenotype-icon names (Alpha Genes, cut in Wave 4) read from a saved custom xenotype file. That is a notice, not an exception.
- Our line: `[RimMandrake.Biomes] world terrain shader on 9 no-road/no-river biomes: RUT_ExtremeDesert, RUT_Umbra, RM_SeabedFloor_* (5), RM_SeabedUnavailable, RM_Stillsand`.

## Load ASHKARR_DEV_START_2026-10-20 (load_game, ignoreModCompatibility: the save records 83 mods)
- Load-segment signatures (`delta.py playerlog_menu.txt log_after_load.txt`) are all classes of the 374 baseline
  (`Transient/live_testing_2026-10-20e/RESULTS.md`): 475 x non-compressible chunk, the sourcePrecept load-ID lines on the Jawa clothing,
  `Could not find think node` x4, Precept_Ritual / RitualOutcomeEffectWorker PostLoadInit NRE, InputLegacyModule FileNotFound, RimFridge_PowerFactorSetting.
  **0 new exceptions.** The DewbackPack texture miss of the 374 load is gone.
- VEF "New faction" dialogs: 3 (Junkers, Mercenaries, Roaming monstrosities), down from 7. All answered "Do nothing".
- Ticked 15,000 (play_for 60 s Ultrafast) for the noon globe and midday line-up. Nothing saved.

## Owed
- ResearchRetag `forceLoadAfter` trim (Wave 4 spec, after the dump; dump captured 15:10Z on 324). It needs a deploy and the next load.
- TIDAL_LOCK_RESTORE_SUN_STILL_COMMUTING (filed): the globe sun turns with the clock, because the Alien Worlds sun patches are not applied.
