# STILLSAND_SUN_LIVE_VERIFY_1 — live check of the Stillsand's latitude sun

The live half of `STILLSAND_SUN_FROM_LATITUDE_1`, whose offline build closed with a selftest (`src/RimMandrake/Utils/selftest_sun_heat.py`, the five `stillsand:` cases). Needs the game up with `mandrake.rm.creaturebehaviors` and `mandrake.rm.stillsand` loaded.

## criteria

- On Stillsand quicktest maps at two latitudes: no night ever falls; shadow length differs by latitude; above 55° elevation a roof protects, below it only a lee does (read `RM_MapComponent_ShadeGrid.SunElevationDegrees`, `EffectiveHeatKind` and `ExposureAt` on a roofed and a lee cell).
- Open sand in cast shade reads exposure 0.35; a paved lee reads 0.
- A pawn in the open is in heatstroke territory within an in-game hour at the far ring.
- Solar panels on a pinned Stillsand map run at full output (sky glow constant at 1).
