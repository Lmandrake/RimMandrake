# STILLSAND_WIND_SUN_BEARING_1 — dune wind locked to the sun bearing

Split from `STILLSAND_SUN_FROM_LATITUDE_1` (its spec items 9, verbatim below). Design source and owner rulings are cited on the parent.

Built already by the parent (`STILLSAND_SUN_FROM_LATITUDE_1`): the pinned sky on `RM_Stillsand`, the 85° clamp, the heat kind resolved from sun elevation (`RM_SunHeatExtension.overheadAboveElevationDegrees`, `RM_MapComponent_ShadeGrid.EffectiveHeatKind` / `SunElevationDegrees`), heat by sin(elevation) and the sand glare floor, in `mandrake.rm.creaturebehaviors`. Read the map's sun elevation from `RM_MapComponent_ShadeGrid.SunElevationDegrees`; never re-derive it.

## spec

9. **One bearing for everything.** Pin the dunes engine's wind to the same tile-to-substellar
   bearing (`DuneFieldExtension.lockBearingToSubstellar`, small C#), so dune crests, lees, shadows
   and the wind all point one way and *"a wind that has never once changed its mind"* holds.

Add its Mod Settings toggle (parent item 11) in the owning mod.
