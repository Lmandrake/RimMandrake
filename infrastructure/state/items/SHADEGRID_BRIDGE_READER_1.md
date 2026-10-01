# SHADEGRID_BRIDGE_READER_1 — a bridge read of the shade grid and the pinned sun

`STILLSAND_SUN_LIVE_VERIFY_1` asks for state reads of `RM_MapComponent_ShadeGrid.SunElevationDegrees`,
`EffectiveHeatKind` and `ExposureAt(cell)`, and of `RM_MapComponent_PinnedSun.IsActive`. No JawaBench tool
reads a MapComponent's members, and the comps expose no debug action. So the 2026-10-01 live session could
not take any of these readings.

Seen on that session's RM_Stillsand quicktest (standard planet, latitude 37.9): a `SolarGenerator` gave
1700 W from tick 20,400 to 24,436, then 1672, 1563 and 1446 W by tick 26,872. So sky glow was not constant
there. Whether `PinnedSun` was active on that map is not known.

## spec
Add a read-only `jawa/` tool (rimbridge-companion skill). Given a cell list, it returns the sun elevation,
the heat kind, `ShadeAt`/`ExposureAt` per cell, the pinned-sun state and the current sky glow.

## criteria
- The tool answers on a Stillsand quicktest, and `STILLSAND_SUN_LIVE_VERIFY_1` can be run from it.
