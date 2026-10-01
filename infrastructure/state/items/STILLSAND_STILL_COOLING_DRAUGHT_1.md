# STILLSAND_STILL_COOLING_DRAUGHT_1 — still-water cooling draught

Split from `STILLSAND_SUN_FROM_LATITUDE_1` (its spec items 10, verbatim below). Design source and owner rulings are cited on the parent.

Built already by the parent (`STILLSAND_SUN_FROM_LATITUDE_1`): the pinned sky on `RM_Stillsand`, the 85° clamp, the heat kind resolved from sun elevation (`RM_SunHeatExtension.overheadAboveElevationDegrees`, `RM_MapComponent_ShadeGrid.EffectiveHeatKind` / `SunElevationDegrees`), heat by sin(elevation) and the sand glare floor, in `mandrake.rm.creaturebehaviors`. Read the map's sun elevation from `RM_MapComponent_ShadeGrid.SunElevationDegrees`; never re-derive it.

## spec

10. **Cooling draught:** a drink of still water gives a hediff of ComfyTemperatureMax +8 °C for
    about 6 h (XML on the still's output).

Add its Mod Settings toggle (parent item 11) in the owning mod.
