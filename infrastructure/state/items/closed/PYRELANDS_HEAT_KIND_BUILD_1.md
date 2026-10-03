# PYRELANDS_HEAT_KIND_BUILD_1

Spec: `design/Jawa/worldbuilding/biomes/pyrelands_bedazzle_review_2026-10-01.md` §1 (finding 3) and §4 row 0b. Law: one kind of heat planet-wide (owner, 2026-09-29/30; `SOLAR_HEAT_EXPOSURE_1`, `SHADE_GEAR_FAMILY_1`, `STILLSAND_SUN_FROM_LATITUDE_1` for the latitude pin).

1. Add `RimMandrake.CreatureBehaviors.RM_SunHeatExtension` to `RM_Pyrelands`: `heatKind overhead`; sun elevation from the map tile's latitude (as the Stillsand does, never a region name); `overheadAboveElevationDegrees` so a low-sun Pyrelands tile uses `lowSun` cover rules; `heatScalesWithElevation true`; `heatOffsetC` an invented first value, tuned in live play (the biome is already ~54 °C median: keep it modest).
2. Retire `RM_FurnaceWarmth` (`RM_PyrelandsHediffs.xml`) and its aura's hediff stamping. The furnace-beast's warmth becomes a local felt-temperature offset (+°C within a radius, falling off with distance) through the built `Thing.AmbientTemperature` postfix in `RM_SunHeatPatches`, so vanilla hypothermia relief and heatstroke do the work. Keep the vanilla heat pusher for rooms.
3. Mod Settings: the existing sun-heat toggles cover it; add a furnace-warmth strength slider.

The burn itself stays ordinary vanilla fire heat. Depends on `PYRELANDS_FAUNA_TIER_PORT_BUILD_1` (the `RM_` furnace-beast).

🔴 **North-star re-measure:** `PYRELANDS_NORTHSTAR_TRIAL_1` must re-measure after row 0 (the animal move) lands: it changes the cast the trial's census reads. Sequence with `PYRELANDS_SHIP_READINESS_1`.

## verify
- Selftest: a pawn beside a furnace-beast reads a higher `AmbientTemperature`; no comfort-range hediff exists.
- Quicktest on a Pyrelands map: open-sun exposure heats a colonist through vanilla heatstroke; a parasol helps under a high sun.
