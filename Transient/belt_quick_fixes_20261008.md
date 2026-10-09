# Quick-fix batch 2026-10-08 (design pass DESIGN_PASS_2026-10-08.md)
Filed 22 items (all FOUNDRY, v1, offline) + 3 card-ruling notes. Quick fixes landed, one commit each:
- [x] TB-1 SCALD_GRAZER_STEAM_IMMUNE_1 eaa6bde7c (RM_ScaldWalker in the 3 immune lists; the planet-wide tag is NATIVE_HAZARD_TAG_ONE_1)
- [x] X-1 SURFACE_HOME_MAP_HELPER_1 99b1619d9 (EH RM_SurfaceHome; FlowWorks keeps a private copy, it cannot reference EH). NOTE: that commit also swept in untracked FlowWorks art_source pngs + northstar result jsons by my mistake (pushed, small)
- [x] LP-3 DEEPFIRE_NODLC_SETTING_DELETE_1 b5e2a2d1b
- [x] CB-2 PARENTAL_ENRAGE_FACTION_GUARD_1 c46d8afb1
- [x] DI-1 ELDER_TREASURE_TAG_TABLE_1 9874d0386 (code half; the 3 canon RUT treasures are still owed, carry RM_ElderTreasureExtension)
- [x] LP-1 DEEPFIRE_ANY_STOVE_DISHES_1 be41f62b1
- [x] SC-1 WARSCAR_MARK_MUTUAL_LOCK_1 5b74feefe
- [x] EH-2 MOD_TICKER_COMPAT_LINT_1 f96404eb1; 5 real hits filed as TICKER_NEVER_FIRES_FIX_1
