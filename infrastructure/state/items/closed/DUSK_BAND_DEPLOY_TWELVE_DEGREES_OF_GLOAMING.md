# DUSK_BAND_DEPLOY_TWELVE_DEGREES_OF_GLOAMING

Filed 2026-10-20 (FOUNDRY). Follows `TWILIGHT_BAND_DECIDE_HOW_FAR_DUSK_REACHES` (owner by card: "12 degrees"),
built and published at 5a1b7076e122 (`RM_TidalSunGlowMath.DefaultTwilightBandDegrees` 6 -> 12).

## spec
Deploy CreatureBehaviors (`deploy_custom_mods.py --mod CreatureBehaviors --apply`, game down: the DLL is locked while
it runs), then load. The settings key `tidalTwilightBandDegrees` is only written when it differs from the default, so
a settings file saved at the old default 6 now reads 12; check the slider says 12.

## verify
- Mod Settings > CreatureBehaviors > Pinned sun: slider reads "Dusk band past the edge of day: 12 degrees".
- Bridge read of `GenCelestial.CelestialSunGlow(tile, ticks)` at a tile with sun elevation -6 deg reads 0.30
  (the 12-degree smoothstep midpoint; with 6 it read 0). Home tile 17011 still reads 1.0.
