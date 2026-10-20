# Owner rulings by question card, 2026-10-19 evening (FOUNDRY records; his words are the answers)

Authority for each line: `--by-card` (question → picked option). Follow-through status in the last column.

| # | question | his answer | follow-through |
|---|---|---|---|
| 1 | May the donor test pass despite the MineralsFramework NRE? | "(1) and ensure we create whatever it was that that mod did within our own holdings." | Retire done in Wave 2; nothing of ours used it (10_minerals_framework.md) |
| 2 | Forge slow-ground slot | "Create something truly alien and interesting ... Offer three options and ask us ..., then do it." Sheet pick: **Ummisk** with his steam-cushion / glass-tube note | building (FORGE_SNAILHOLE_FILL_EMPTY_SHELL_LEFT_BEHIND) |
| 3 | Repaint mod set | "Likely (1), but really it's about having any mod we NEED to represent the world and gravship and player characters ... Even our own mods are left out unless they are NEEDED (Baroque Biomes obviously is needed)." | PAINT list (08) |
| 4 | Retirement keep/cut sheet | ruled (decisions file `Transient/retirement_keepcut_sheet_2026-10-20.decisions.json`); "KEEP A FILE WITH ALL THE ORIGINAL MODS STORED" | `mod_archive/ALL_ORIGINAL_MODS.tsv`, RULED profile lists, 11_ruled_keepcut.md |
| 5 | Research Reinvented | Keep it in the lean list | DEV keeps it; undo the demotion in the RULED lists if the sheet moved it |
| 6 | Sensible Factions | "You tell me. Does our skill use it to move world factions, or does Bridge know how to do it by itself? If we don't need it, drop it permanently." | FOUNDRY finding: no skill or src uses it; only old design docs (`desert_world_design.md:460`, `build_plan.md:202`) mention it; bridge has faction tools (`jawa/faction_create`, relations §6). **Drop permanently** (Wave 3) |
| 7 | Factions/economies that must exist at paint | Green Tide raiders, Shokk Webwork economy (NOT Rust Cathedral roaches, NOT Wrecked Machines) | PAINT list adds `rut.greentideraidant`, `rut.shokkweaveeconomy` |
| 8 | Rock types per tile | "Give me ideas that would motivate something new for rocks right now. Do a design pass and give me question cards. I will rule, or select (2) or (1)." | 12_rocks_design.md (in progress) |
| 9 | New feature ideas default to v2 | "Decide per idea at filing" | no change to current default; no blanket rule |
| 10 | Open items of the 39 Wave-1 mods | "Move all to v2" | retarget those items to v2 |
| 11 | Bazaar trade window and in-game LLM voices | "Both to v2" | retarget Bazaar + LLM-voices items to v2; v1 trade = vanilla + loaded trade-UI mods |
| 12 | Direct Sun on forest maps | "Wait for the crown model in v1" | the tree shade model (tree_shade_model_2026-10-19.md) is v1-gating for Direct Sun |
| 14 | Stone rule (12_rocks_design.md card 1) | "Each biome names its stones" | item `BIOME_STONES_DESIGN_BASALT_JOINS_THE_BAND` |
| 15 | Extra stone ideas (cards 2-3) | wanted: basalt for volcanic biomes, deeper stone at superdeep pits, stones that build differently | basalt in `BIOME_STONES_DESIGN_BASALT_JOINS_THE_BAND`; `PIT_DEEPSTONE_BUILD_DIGGING_FINALLY_PAYS`; `STONE_BUILDSTATS_TUNE_GRANITE_GETS_RIVALS` |
| 16 | Hand-placed geological landmarks before the repaint (card 4) | "(1) plus we should get rid of the Fog of War" = plan them for the paint | item `GEO_LANDMARKS_SKETCH_BEFORE_THE_PAINT_DRIES` (before-paint gate) |
| 17 | Real Fog of War | "we should get rid of the Fog of War. I think I'm done with it. It's ugly." Supersedes the Route B ruling that shipped Real FoW + CAI 5000 together | Retirement Wave 3 (`14_wave3_prep.md`); CAI 5000 stays on the list (recommendation in 14 §3) |

Earlier answers recorded the same evening (no item change):
- Glass trail for the Ummisk: **NOT wanted**.
- Rhossak numbers: kept as **PROVISIONAL**.
- The 155 kept renders: **stay untouched**.

Ruling 18 (appended after the list above; same card set):

| # | question | his answer | what it changes |
|---|---|---|---|
| 18 | How should this frozen biome be settled? (the Fuel Snows / Umbra land) | "Back to Umbra, dark": "(2) it's totally dark except for the utterly beautiful and wildly active aurora. Let's call it the Auroral Umbra then. And look back at the original concept sheet to find out about precipitation. It ruled what's solid, liquid, gas at various temperatures." Then: "Yes, there should be a perpetual Auroral activity in that biome. Put that in its def now. Auroral Umbra is the new name, better than Rimefall. And yes, it should NOT snow, it should rain propane (equivalent with chemfuel)." | item `AURORAL_UMBRA_RENAME_BACK_TO_DARK`: `RUT_FuelSnows` renamed back to `RUT_Umbra`, label "Auroral Umbra"; perpetual aurora (Weather Suite, tunable); propane rain, no snow (concept sheet `worldgen_interactive_def.md:151-155,177-179`: propane liquid −188…−42 °C); the RUT_Umbra→RUT_FuelSnows paint remap is cancelled (the save already holds RUT_Umbra on 2,531 tiles) |
