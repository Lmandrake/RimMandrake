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
