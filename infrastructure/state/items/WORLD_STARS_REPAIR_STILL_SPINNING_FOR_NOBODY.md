# WORLD_STARS_REPAIR_STILL_SPINNING_FOR_NOBODY

Owner (2026-10-20): *"when you advance time in the planet view/worldmap, the Tidally Locked correctly shows the shadow as unmoving. But the stars still rotate around you as though the planet is spinning. Can we fix them too?"* By card: the stars drift slowly once a year.

## Feasibility read (offline, 2026-10-20)
- None of our mods freeze the world-view sun. `RM_PinnedSunPatches` and `RM_MapComponent_PinnedSun` pin the shadows on local maps only. The fixed terminator on the planet comes from the Alien Worlds tidally-locked add-on, or from our day/night biome paint (confirm live). See `WORLD_PHYSICS_AUDIT_LOCKED_SUN_TEMPS_RINGS`.
- Vanilla: `GlobalDrawLayer_Stars.Rotation` aims along `GenCelestial.CurSunPositionInWorldSpace()`. That value turns 360° per day from `TicksAbs`. The same value drives `GlobalDrawLayer_Sun` and `WorldRendererUtility.UpdateGlobalShadersParams`.
- Fix: a postfix on `CurSunPositionInWorldSpace` returns a fixed direction toward the substellar tile (outside `ProgramState.Entry`). If the method is inlined, patch its three consumers instead. A second postfix on the stars' `Rotation` adds `yearFraction*360°`. A Mod Setting freezes the stars completely.
- About 40–60 lines of C# plus about 15 for the setting. The change only touches rendering. It needs a DLL rebuild, and the redeploy waits until the game is down.
- Before deploying, check that Alien Worlds does not already patch the same method. Two mods patching it at cross purposes is the risk.

## Verify
- Offline: a selftest shows `CurSunPositionInWorldSpace` is identical at two tick values, and the stars' rotation differs by 6° per day.
- Live: a bridge read of the sun vector, plus two planet screenshots one in-game day apart.

## Built
- Part 1, stars (de96af3987, 2026-10-20): `RM_WorldStarsPatch`, a postfix on `GlobalDrawLayer_Stars.Rotation`. The stars aim at a fixed sun and turn by `RM_WorldStarsMath.DriftDegrees` (6° a day, one turn a year). Settings `worldStarsPinned`, plus `worldStarsYearlyDrift` (off = frozen).
- Part 2, sun disc and planet light (2026-10-21): `RM_WorldSunPatch`, a `Priority.First` postfix on `GenCelestial.CurSunPositionInWorldSpace`. While `ProgramState.Playing` it returns the unit vector toward the substellar point. That point comes from WeatherSuite's `PlanetGeometryDef`, read by name; else the first biome's `RM_PinnedSunExtension`; else (0,0). The stars now aim at the same `PinnedDirection()`. Setting `worldSunPinned`, default on, in the "Pinned sun and false shade" group. The main menu and world generation (`Entry`) keep vanilla's sun.
- How this lives with Alien Worlds - Tidally Locked (read from its DLL, decompiled 2026-10-21). While its planet type is active it prefixes `SunPositionUnmodified` (day 0, noon), which freezes this method at (0,0,-1). It also postfixes this method with `y = clamp01(y + 0.15)`. Ours runs first and writes the same (0,0,-1) for Ash'karr's (0,0), and AW's lift still applies after it, so nothing visible changes while AW is active. While AW is inactive (it drops to Default under Worldbuilder; see the 2026-10-20 note), the disc and the lit side stop turning anyway. Worldbuilder, My Little Planet and Planet Atmosphere do not patch these methods; Planet Atmosphere reads the value for `_WorldSpaceLightPos0`, so it follows the pin.

## criteria

- A1 L0: `python3 src/RimMandrake/Utils/selftest_sun_heat.py` passes 54/54. Its "world sun" case shows the pinned sun identical at two ticks a day and a bit apart (vanilla's moved), substellar (0,0) = (0,0,-1), Entry or setting-off keeping vanilla, and the direction round-tripping through `LongLatOf`. Its "world stars" case shows 6° a day and frozen when drift is off. The CreatureBehaviors DLL builds with its `.srchash`.
- A2 L2: after deploy, a bridge read of `GenCelestial.CurSunPositionInWorldSpace()` gives the same vector at two in-game hours. The log carries one `world sun pinned toward substellar (0, 0) from PlanetGeometryDef ...` line.
- A3 L2: two planet-view screenshots one in-game day apart show the sun disc and the lit side in the same place, and the stars about 6° turned.
