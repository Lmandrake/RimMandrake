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

Remaining to close: LIVE verification only.

```
PROVE    bridge def-read of RM_FE_Pyrelands wildAnimals on the running game (post-patch)
EXPECT   14 entries: RUT_FireHawk 0.15, RUT_FurnaceBeast 0.08,
         AA_Razorjack 0.2, AA_Barbslinger 0.15, AA_FireWasp 0.4, GR_Mantistanis 0.05,
         GR_Boomsnake 0.5, Anooba 0.35, Iriaz 0.5, Nuna 0.5, Orray 0.25, Zeer 0.6,
         Dalgo 0.18, Gizka 0.3 — and NOT Hare/Rat/Boomalope (placeholder displaced,
         Boomalope cut)
LIES     a FindMod block that never fired logs nothing — count entries, don't just
         spot one; a trimmed list without a donor legitimately drops that donor's rows
         (verify against the donors actually loaded)
```

Rides the Pyrelands walk restart (trimmed 37-mod list staged, bridge held by BENCH,
owner granted 2026-09-14). Closes on the def-read plus natural-spawn sighting.
