# STILLSAND_MIRAGE_CONDITION_1 — the mirage

Split from `STILLSAND_SUN_FROM_LATITUDE_1` (its spec items 8, verbatim below). Design source and owner rulings are cited on the parent.

Built already by the parent (`STILLSAND_SUN_FROM_LATITUDE_1`): the pinned sky on `RM_Stillsand`, the 85° clamp, the heat kind resolved from sun elevation (`RM_SunHeatExtension.overheadAboveElevationDegrees`, `RM_MapComponent_ShadeGrid.EffectiveHeatKind` / `SunElevationDegrees`), heat by sin(elevation) and the sand glare floor, in `mandrake.rm.creaturebehaviors`. Read the map's sun elevation from `RM_MapComponent_ShadeGrid.SunElevationDegrees`; never re-derive it.

## spec

8. **The mirage (slate IN).** On a tile with sun elevation above a threshold, a GameCondition
   paints a shimmering false-water band on the far map edge and lowers long-range accuracy in full
   sun. A heat-struck pawn can break into a `MentalStateDef` "chasing the water": it walks toward
   the mirage until rescued or it collapses. It always leaves the pawn on the map, with a letter.

Add its Mod Settings toggle (parent item 11) in the owning mod.

## criteria

- The mirage's mental state ends with the pawn still on the map and a letter.
