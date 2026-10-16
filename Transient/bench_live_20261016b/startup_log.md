# Startup log, ratchet_pilot (21 mods, modSet 21/058a6d3f), 2026-10-16 launch

Player.log is a fresh file (the launch-offset 44717 was the previous log's size; read from byte 0, 319 lines). Menu reached: bridge answers, programState=Entry.

- First exception: NONE. No line contains "Exception". First red line is `Could not find a type named AlphaBehavioursAndEvents.DamageWorker_Vampiric` (plus 6 more `Could not find a type` for absent donor mods: BiomesPlus, VanillaBiomes, ReGrowthCore, CypreJungle). Donor mods are not in the tier; expected.
- `[RimMandrake.GimmeSomeSlack] Harmony: patched 28, missing 0` (census is 28 now, not the sheet's 23; missing 0).
- `Harmony patch failed, feature switched off`: 0 hits, any mod. FlowWorks patched 64 missing 0; hose essential patches all present.
- RustCathedral: Hum patched 12 missing 0, Walls patched 1 missing 0; no red RustCathedral line.
- `Could not resolve cross-reference`: 1, `guy762_MandoHelmet_supercom` (wanter=apparelRequired), a donor def; NO RM_/RSW_/RUT_ name. Also 20 `Failed to find ... VAEWaste_*` (donor, absent).
- 61 `Patch operation ... failed` (SWBestiary, Baroque TheRot AngelMoth, RimUtinni Patches): conditional/absent-donor targets, standard noise.
- Config errors: 5 RUT_Jawa_* weaponMoney min < cheapest weapon (weaponless risk), BasicMechtech techprint, 2 faction memes.
- Missing textures: ~20 RM_/RUT_ plant defs fall back on absent vanilla-donor paths (Things/Plant/SnakePlant, PincushionPlant, Echeveria) and 6 `Collection cannot init` (RM_Glasmaw, Murrowbulb, Thrannagourd, Salvessa, CorriskTree, Crimmelroot, LumbrelTree). Art-owed, not startup-fatal.
- JawaBench ready: 413 tools, modSet 21/058a6d3f.
