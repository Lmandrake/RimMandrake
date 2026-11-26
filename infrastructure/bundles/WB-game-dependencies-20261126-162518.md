# WB-game-dependencies-20261126-162518 (home game:dependencies): DONE

All 7 members have an outcome (2026-11-26). Nothing is next for this bundle.

| member | outcome |
|---|---|
| DONOR_FOUR_RETIRE_JUST_GET_IT_DONE | dropped, stale: the four donors are in neither the live ModsConfig nor the canonical start save; A3 is the biome mods' own bars, A5 met by that state |
| GENERATOR_MODS_PROVE_INERT_AFTER_CREATION | dropped, stale: My Little Planet and Sensible Factions are already off the list and out of the canonical start save |
| WAVE1_MODLIST_RETIRE_37_IN_ONE_LOAD | dropped, stale: 0 of the 39 Wave 1 mods in the canonical start save; full-list sittings retired |
| PLANET_ATMOSPHERE_CLOUD_COST_1 | dropped, not worth the touch: offline census 74.1 MB VRAM, live A/B noise about 1.5 GB; the mod stays |
| WORLD_REMAKE_AUDIT_DEPENDENCY_CLOSURE_FIRST | closed, done already at 57b78d6f23 (05_drop_closure.md) |
| UNUSED_PORTS_MEASURE_WHAT_NOBODY_NEEDS | closed, done already (survey of 2026-11-03) |
| OILGAS_BUILDABILITY_EXCISE_FOUND_NOT_FORGED | shaped (offline selftest), fixed at 4c3f9893c8fc in Jawa Doctrine, live PASS on ArchBig, closed |

Open after the bundle: the fixed Doctrine files have had no fresh reader yet (the brief bars this run from starting a
subagent). Files: src/RimUtinni/Doctrine/Source/DoctrineCore/DoctrineSettings.cs, Patches/FoundNotForged.xml.
Game state: ArchBig runs the 15-mod tier mods__dubwise_rimefeller__vanillaexpanded_helixiengas__mandrake_rut_doctrine,
lock released; its in-memory Doctrine settings are both off (the settings file is deleted, so the next launch is at defaults).
