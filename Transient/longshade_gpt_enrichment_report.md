# LONGSHADE_GPT_ENRICHMENT_1 — report (2026-10-01)

Related blocks: SOLAR_HEAT_EXPOSURE_1 and LONGSHADE_BEDAZZLE_MECHANICS_1 are blocked only on game-up
quicktests and owner tuning. Their offline builds are complete, so this pass built on them.

- §1 Shipfall Commons: BUILT (d4193b9e6). LongShade `RM_ShipfallCommons.cs`, rung data on `RM_LongShade.xml`, toggle in Long Shade settings.
- §2 Gloomcast moves shade: BUILT (24bf0e9b8, d4193b9e6). Moving-shade layer in the shade grid (dirty rects), gloomcast casts it; the shadow-follow tree now runs ahead of the hop; a moving shadow counts as perceived shade. Open: which grazers follow, feeding scar -> GLOOMCAST_WAKE_RIDERS_1.
- §3 Heat you can hear: BUILT (4f306af5d). Camera-keyed lit/shade bed, herd call at the rim, gloomcast footfalls; placeholder vanilla audio. Haze muffle waits on the smoke calendar (noted on LONGSHADE_BEDAZZLE_MECHANICS_1). Also fixed the proximity soundscape's never-maintained sustainers. The same bug in the Rust Cathedral -> RUST_CATHEDRAL_HUM_UNMAINTAINED_1.
- §4 Lee-side middens: NOT BUILT, all content unruled -> LONGSHADE_MIDDENS_DESIGN_1.
- §5 Shade gear learned: NOT BUILT. The lesson mapping is ambiguous, and Long Shade-only lessons conflict with the cross-biome gear ruling -> SHADECRAFT_LESSONS_DESIGN_1.
- Quicktests -> LONGSHADE_ENRICHMENT_QUICKTEST_1.

Selftests: sun heat 46/46. Full suite 77/81: walklint and sound_paths are known failures (sound_paths fails on the Wasteland Spacedrone clip). label_collision failed in the parallel run but passes standalone (exit 0).
