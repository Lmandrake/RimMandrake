# DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES — one Direct Sun in code, a pure function of sun-angle geometry

Design and per-biome migration list: `design/RimMandrake/unified_direct_sun_heat_2026-10-19.md`
(§3 the ruled model, §4 the migration, §8 the rulings). Replaces `CONTAGION_HEAT_JUDGE_SUN_KIND_UNSAID`
(the Contagion owes no heat kind; there are no kinds). Nothing here is built.

Owner, 2026-10-19, by question card: *"55 C everywhere"* · *"This is too ornate. Keep only Parasols
and Tents, and Tents are just a quick structure (any roof structure will do the same). Then we just
need to think about where "shade vs not shade" is for the various maps, and that's a pure function of
geometry, NOT biome. So: no biome-specific heat, no biome-specific sun. It's a matter of geometry (low
sun is less intense AND produces longer shade, high sun produces only covered shade and much more
intense effect). Ambient heat is normal Rimworld rules."* · *"Hotter air on the thermometer"* · *"In
Utinni this isn't possible: time of day = location, permanently. If these biomes are used on a
day/night world, then of course it follows solar angle/geometry that is now a function of time of
day. If that creates too much work, then drop sun heat (should actually be called "direct sun") when
the day/night isn't constant anymore."*

**Model: opus** (cross-cutting rewrite of `CreatureBehaviors` sun code). Tier RimMandrake.

## spec

1. **Sun elevation E** comes from the map tile's arc to the substellar point (0,0), one clamp [0°, 90°].
   E ≤ 0 (nightside, terminator below the horizon) gives no Direct Sun. Delete the per-biome
   `min/maxElevationDegrees` and `substellarLatitude/Longitude` fields.
2. **Utinni: time of day = location.** Every map of the shipped world has a fixed sun at its tile's
   E (the pinned sky the Long Shade and Stillsand already use), decided by the world, not by a
   BiomeDef field. Read how `RM_MapComponent_PinnedSun` decides today before changing it (UNMEASURED
   how the shipped world is recognised). **A world with a day/night cycle:** Direct Sun is off there
   (the owner's allowed drop; not the primary target). Following the clock is a later option, not
   this item.
3. **Intensity.** Felt offset = 55 °C × sin(E) × weather sun factor × body-size factor × strength dial,
   into the existing `RM_SunHeatPatches.Postfix_AmbientTemperature` → vanilla Heatstroke path. One
   planet zenith number (a setting, default 55). No per-biome `heatOffsetC`, floor or scaling switch.
4. **Shade is geometry.**
   - A roofed cell (any roof: a tent, a building, rock) is covered at every E. The old "thick roof
     only under lowSun" rule goes.
   - A parasol covers its carrier at every E (the owner kept parasols in the Long Shade, whose sun is
     ~14°).
   - Structures, rock and tall plants cast a shadow down-sun whose length grows as E drops
     (height / tan E, capped for performance). A high sun leaves almost no cast shade beyond covered
     cells; a low sun leaves long shade.
   - Delete `RM_HeatKind`, `KindFromElevation`, `overheadAboveElevationDegrees`, `GearKindFactor` and
     every `ambient` branch (shade grid, gizmo, shade-hop, pathing, glare, `SolarMirrors`
     `RM_MirrorPatches.cs`, `RM_ShipfallCommons.cs`).
5. **Shade gear is parasols and tents.** `RM_SunShield` is removed as a shade item
   (`EnvironmentalHazards/Defs/ThingDefs_Buildings/RM_ShadeGear.xml`; a wall casts the same lee).
   `RM_ShadeTent` is a quick roof structure: its cells read exactly as any roofed cell. The mirrak
   shade cloth keeps one deepening value, not one per kind.
6. **Ambient heat is vanilla air temperature.** The Forge (15), the Scald (15), the Fever Wood (8) and
   the Greentide (12, the wet-bulb card) lose their `RM_SunHeatExtension` heat and get a permanent
   vanilla `GameCondition_TemperatureOffset` (`RM_ForgeAirHeat`, `RM_ScaldAirHeat`,
   `RM_FeverWoodAirHeat`, `RM_GreentideAirHeat`), values PROVISIONAL. Before fixing numbers, run the
   plant check in the design doc §3 (growth limits vs tile median + offset).
7. **Every BiomeDef** loses its heat fields (list: design doc §4). Pending the owner's one confirm
   (design doc §8, D5/D6): Direct Sun runs on every sunlit map of the shipped world with no biome
   opt-in, so the Scarlands, the Miasma and the `RUT_` twins get it too; sand glare keys to natural
   sand terrain, not the Stillsand. If he says no, an opt-in list is a one-line gate.
8. **Words.** Player-facing text says "Direct Sun", never "sun heat" (settings, the sun-load bar,
   letters). C# class renames are not required.
9. **Arrival letters** (`BIOME_ARRIVAL_LETTERS_ALL_1`): rewrite each heat line from "heat kind" to
   the tile's sun and the shade that answers it (roof, parasol, long shadows when the sun is low);
   the four air-heat biomes say the air itself is hot.
10. Change the tests named in design doc §4 ("Tests to change") in the same commit.

## criteria

- No BiomeDef or patch under `src/` carries `heatKind`, `heatOffsetC`, `heatScalesWithElevation`,
  `minScaledHeatOffsetC`, `overheadAboveElevationDegrees` or per-biome elevation fields (XML parsed
  as elements), and `RM_HeatKind` is gone from the source.
- `DIRECT_SUN_SELFTEST_BUILD_EVERY_BIOME_EQUAL` passes.
- `RM_SunShield` no longer ships as shade gear; parasol and tent remain.
