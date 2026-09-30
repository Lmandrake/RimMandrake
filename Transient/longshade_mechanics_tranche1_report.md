# LONGSHADE_BEDAZZLE_MECHANICS_1 — tranche 1 report

Status: LANDED (tranche 1 of several; item stays open). 2026-09-29.

## Built

**Part 1, golden hour (the pinned sun).** This is a kit mechanic in `mandrake.rm.creaturebehaviors`, carried as data on `RM_LongShade`.
- `RM_PinnedSunExtension` (BiomeDef extension) holds the substellar point (0,0), the elevation clamp (2–30°), the render length, a fixed shadow opacity, the glow (0.8) and the sky, shadow and overlay colours. All of these are first values, to be tuned by looking at them in game.
- `RM_MapComponent_PinnedSun` puts a never-expiring `RM_WeatherEvent_PinnedSun` at the front of the weather-event list. RimSage confirms this pins the sky target and `OverrideShadowVector`, with no anchor Thing left in the save. The sky gives way to any GameCondition that paints its own sky (eclipse, aurora, and later the haze).
- `RM_PinnedSunPatches` is a postfix on `SkyManager.SkyManagerUpdate`. It pins the shadow opacity, which vanilla would otherwise fade at the real dusk.
- Public contract for `SOLAR_HEAT_EXPOSURE_1`'s directional grid: `For(map)`, `IsActive`, `ShadowDirection`, `SunElevationDegrees`, `ShadowLengthPerHeight`, and a settable `ShadowLengthFactor` for the haze. The grid itself is not built; it is that item's scope.
- Settings (Creature Behaviors): "Pinned sun (golden hour)" and a sky-strength dial. That settings screen now scrolls, because it had outgrown one window.

**Part 2, the mirrak.**
- `RM_FalseShadeExtension`, `RM_MapComponent_FalseShade` and `RM_ShadePerception.PerceivedShadeAt` form a false-shade layer that sits apart from the grid. The shade-seeking wander now reads perceived shade.
- `RM_CompFalseShadeAmbusher` lies still on open ground and seizes anything small that stands in its "shadow". Each seizure leaves a sand-disturbed patch and the blood from the strike. It eats the kill where it fell, and when the victim is the player's own it sends a message.
- The `RM_Mirrak` def and kind are authored, along with `RM_Leather_Mirrak` (tagged with `RM_ShadeClothExtension` for `SHADE_GEAR_FAMILY_1`).
- Settings: "False-shade ambush (the mirrak)".

**Part 3, first seam.** A sarlacc swallow now churns the sand and sends a message for prey that is not the player's. Toggle: Sarlacc settings, "Swallows leave a sign".

## Remaining

- **Mirrak roster row.** The art is still in the artpipe queue (`pending/RM_Mirrak_*`). Adding the row now would put a magenta animal on the map. Wiring it is one line in `RM_LongShade.xml`, done once the render lands.
- **The dash giver treating the mirrak as shade.** The rest-dash-rest givers belong to `SOLAR_HEAT_EXPOSURE_1`. When they are built they should read `RM_ShadePerception.PerceivedShadeAt`.
- **Haze leaving the mirraks short.** This needs the smoke calendar, which is unbuilt. The seam for it is `ShadowLengthFactor`.
- **Part 3 swimmer's road.** Still to build: the incident, the one-per-map gate, the route to the largest dew ring (which needs the patch graph from `SOLAR_HEAT_EXPOSURE_1`), and rooting into a well. It is also RSW-tier.
- **Part 4 Crawler Road.** Still to build: the GenStep chain spaced by human dash range (which needs the patch graph), minifiable wrecks, and a tall `staticSunShadowHeight`. Hulk art is queued.
- **Part 5 Long Carry.** Still to build: the graves GenStep and journals as lore only (no gnomons). The gear it relies on is `SHADE_GEAR_FAMILY_1`.
- **Quicktests on a Long Shade map.** Every quicktest criterion (all five features, kill signs, swimmer one-per-map) still needs a live session. Tuning the golden-hour colour and glow needs the owner watching.

## Verification

- CreatureBehaviors, LongShade and Sarlacc all build clean with 0 errors, and each DLL is committed with its `.srchash`.
- The touched XML parses.
- `run_selftests.py`: 76/78 passed. The only failure is the known one, `selftest_deployed_biome_refs`.
- Nothing was deployed or tested live.
