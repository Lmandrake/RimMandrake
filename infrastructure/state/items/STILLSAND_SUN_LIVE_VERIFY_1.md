# STILLSAND_SUN_LIVE_VERIFY_1 — live check of the Stillsand's latitude sun

The live half of `STILLSAND_SUN_FROM_LATITUDE_1`, whose offline build closed with a selftest (`src/RimMandrake/Utils/selftest_sun_heat.py`, the five `stillsand:` cases). Needs the game up with `mandrake.rm.creaturebehaviors` and `mandrake.rm.stillsand` loaded.

## criteria

- On Stillsand quicktest maps at two latitudes: no night ever falls; shadow length differs by latitude; above 55° elevation a roof protects, below it only a lee does (read `RM_MapComponent_ShadeGrid.SunElevationDegrees`, `EffectiveHeatKind` and `ExposureAt` on a roofed and a lee cell).
- Open sand in cast shade reads exposure 0.35; a paved lee reads 0.
- A pawn in the open is in heatstroke territory within an in-game hour at the far ring.
- Solar panels on a pinned Stillsand map run at full output (sky glow constant at 1).

Added 2026-10-01, the live halves of the four items split off the parent (offline builds closed with the same selftest's `glare-blind:`, `mirage:`, `wind lock:` and `cooling draught:` cases):

- Glare-blind (`STILLSAND_GLARE_BLIND_GOGGLES_1`): a non-Jawa pawn (a slave will do) standing in open sun gains `RM_GlareBlind` and loses Sight; a Jawa (`RM_GlareAdapted` from `RSW_Jawa_GlareAdapted.xml`) never does; putting `RM_SunGoggles` (or Bothan / light-scan / pao-hat goggles) on the first pawn stops the gain and it decays.
- Mirage (`STILLSAND_MIRAGE_CONDITION_1`): on a tile whose sun is 45° or higher, `RM_Mirage` is on the conditions readout and the shimmer band draws on the sun-ward edge; below 45° it is absent. A pawn in full sun shows "Heat shimmer" on its Medium/Long accuracy factor. Force `RM_ChasingWater` on a pawn (dev): it walks for the band, never leaves the map, and ends (downed, a drafted friend adjacent, or the timer) with a "Mirage:" letter.
- Wind lock (`STILLSAND_WIND_SUN_BEARING_1`): the Moving Dunes debug readout's wind on a Stillsand map points along the shadows and never shifts across a day; off in Mod Settings, it shifts again.
