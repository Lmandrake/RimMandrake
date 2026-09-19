# PYRELANDS_FAUNA_WIRING_1 — wire ruled fauna roster into RM_FE_Pyrelands

## Status 2026-09-14 (BENCH)

The wiring is BUILT and DEPLOYED: `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Pyrelands.xml`
(authored 2026-09-13) carries the ruled roster from
`design/Jawa/worldbuilding/biomes/rosters/the_pyrelands.json`, verbatim numbers,
FindMod-guarded per donor. deploy_custom_mods reports UtinniPatches in sync (239 files).

**2026-09-14 (FOUNDRY, BOOMALOPE_CUT_EVERYWHERE_1)**: Boomalope removed from
the roster and this file's unconditional block — owner ruling "Absolutely no
boomalopes," reversing the 2026-09-09 KEEP-reskinned card the 15-animal count
below assumed. Roster is now 14 animals, sum 4.21.

**2026-09-14 (FOUNDRY, BOOMSNAKE_CUT_CONFLICT_1)**: GR_Boomsnake removed from
the roster and this file's Vanilla Genetics Expanded block — its ThingDef was
already Cherry-Picker cut by BOOM_FAMILY_CUT_1 (2026-09-10); the roster row
was a stale round-2 move-mapping import mechanically re-applied hours after
`biome_findings.md` had already recorded the move as voided by that cut, and
no ruling ever restored it. Roster is now 13 animals, sum 3.71. (This was
live and spawning on the map as of 2026-09-14 per MEASURED bridge census —
next load clears it.)

Remaining to close: LIVE verification only.

```
PROVE    bridge def-read of RM_FE_Pyrelands wildAnimals on the running game (post-patch)
EXPECT   13 entries: RUT_FireHawk 0.15, RUT_FurnaceBeast 0.08,
         AA_Razorjack 0.2, AA_Barbslinger 0.15, AA_FireWasp 0.4, GR_Mantistanis 0.05,
         Anooba 0.35, Iriaz 0.5, Nuna 0.5, Orray 0.25, Zeer 0.6,
         Dalgo 0.18, Gizka 0.3 — and NOT Hare/Rat/Boomalope/GR_Boomsnake
         (placeholder displaced, Boomalope and GR_Boomsnake both cut)
LIES     a FindMod block that never fired logs nothing — count entries, don't just
         spot one; a trimmed list without a donor legitimately drops that donor's rows
         (verify against the donors actually loaded)
```

Rides the Pyrelands walk restart (trimmed 37-mod list staged, bridge held by BENCH,
owner granted 2026-09-14). Closes on the def-read plus natural-spawn sighting.
