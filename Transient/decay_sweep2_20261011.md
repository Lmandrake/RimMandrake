# Decay sweep 2 (FOUNDRY queue ranks 26-60), 2026-10-11

Base: origin/main fe5f4e10b5. Offline only.

Result: closed 0, dropped 0, implemented 0, left 35. Every item is a genuine live/owner/deploy/dependency wait; blockers re-probed against origin/main.

| item | action | reason |
|---|---|---|
| BIOME_WORLD_SWITCH_WAVE_1 | left | needs bridge (live tile edits) |
| FASCINATING_WORLD_JUNK_1 | left | needs owner |
| MOD_VALIDATION_RETROFIT_1 | left | blocked on owner ratifying modcheck sheet format |
| CATHEDRAL_MISSION_BOON_OFFERS_1 | left | blocked: CATHEDRAL_STAGE_COMMENTARY_POOLS_1; RUT_HumCommentary still absent on origin/main |
| CATHEDRAL_STAGE_COMMENTARY_POOLS_1 | left | blocked: RUST_CATHEDRAL_MECHANICS_1 (validated, needs bridge); RUT_HumCommentary absent |
| CATHEDRAL_SURVEY_MISDIRECTION_QUEST_1 | left | same gate; no quest defs on origin/main |
| CATHEDRAL_DESCENT_REVEAL_SITE_1 | left | same gate plus bridge |
| CATHEDRAL_EXPOSURE_COMPLETION_1 | left | multi-slice build downstream of the same gate; not a <20 min offline unit |
| MODCHECK_SUITE_CORRECTIONS_1 | left | verify step is a live min16 re-run, none since 09-13 |
| MODCHECK_DONOR_ENVIRONMENTS_1 | left | needs live bisection (bridge) |
| LIQUID_THIRST_CHAIN_1 | left | STALE BLOCK NOTE: bottles (RM_LiquidBottles.xml) and DBH drinkables patch landed b22bd59b16; remaining: crude still, DBH terrain tag, live verify (bridge) |
| BAZAAR_WINDOW_GRID_1 | left | needs deploy/live; intercept hazard unresolved |
| BAZAAR_HAGGLE_DUEL_1 | left | blocked on BAZAAR_PRICE_ENGINE_1 / WINDOW_GRID |
| BAZAAR_BANTER_LINES_1 | left | blocked on HAGGLE_DUEL |
| BAZAAR_BROKER_TAB_1 | left | blocked on price engine |
| FLORA_LEGIBILITY_BAR_1 | left | owner grades still synthetic prefill |
| CANON_CREATURE_REGEN_1 | left | needs owner grade |
| BACTA_TANK_ART_1 | left | 6 artpipe jobs filed 10-10, awaiting renders + owner sheet |
| GREENTIDE_MECHANICS_2 | left | M10 stub blocked on EXPLOSIVE_PLANT_GROWTH_1; bridge verification |
| EVENT_TRACE_PROPS_LIBRARY_1 | left | NEXT is deploy + modcheck run (live) |
| ATMOSPHERIC_BASE_BUILD_PROGRAM_1 | left | multi-wave program, not a <20 min unit |
| PIT_SUPERDEEP_COLLAPSE_1 | left | needs bridge; fresh leases 10-11 |
| AQUATIC_WATER_BREATHING_GENE_1 | left | only live quicktest proof remains |
| FISH_BESTIARY_BUILD_1 | left | live catch passes owed |
| COMMISSION_LEDGER_CLEANUP_1 | left | wave 16: remaining slugs need design, not art |
| STONEBACK_BOKKA_ART_STANDARD_1 | left | regen done; swap needs owner yes |
| HOSTILE_MOBILE_PLANTS_1 | left | design sitting first (2 of 5 questions unset) |
| FEVERWOOD_ANT_HIVE_DUNGEON_1 | left | umbrella; 3 child items + live proof |
| SUMP_GASLIGHT_1 | left | NEXT is live rerun with skilled doctor |
| VANILLA_BEAST_EXCISION_1 | left | NEXT repoint donor faction carriers; large design-adjacent, not done |
| REGROWTH_RECOLOR_MINEABLES_NRE_1 | left | third-party DLL NRE, cosmetic; resolution needs live diagnostic; not provably dead |
| FEVERWOOD_TWO_FRONT_LURE_TUNING_1 | left | points 1/4 need owner ruling; live tuning |
| WEBWORK_EGG_BROKER_CHANNEL_1 | left | blocked on BAZAAR_WINDOW_GRID_1 |
| SUMP_TAR_FIRE_NETWORK_1 | left | Part 1 unbuilt (sluice gates); multi-hour build |
| CONTAGION_RULED_CONTENT_1 | left | offline build done; deploy + quicktest owed (bridge) |
