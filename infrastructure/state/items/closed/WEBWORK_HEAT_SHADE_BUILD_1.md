# WEBWORK_HEAT_SHADE_BUILD_1 — declare the Webwork's heat kind; the ollathrix's sun-scald reads tree shade

Caused by `WEBWORK_SCORING_SITTING_1` (turn 1). Free tier, `mandrake.rm.webwork` + shared code in
`mandrake.rm.creaturebehaviors`. Design: `design/Jawa/worldbuilding/biomes/webwork_bedazzle_review_2026-10-02.md`
§1 findings 2 and 3, §4 row 0b, §8. Ruling: **build first: fix the base** (decision taken by question card
2026-10-02 07:17 PDT). Law: one kind of heat planet-wide (owner, 2026-09-29/30; `SOLAR_HEAT_EXPOSURE_1`;
latitude pin as `STILLSAND_SUN_FROM_LATITUDE_1`). Precedent: `PYRELANDS_HEAT_KIND_BUILD_1`.

Sibling: `WEBWORK_BASE_PORT_BUILD_1`, same ruling.

## spec

1. **Heat kind: `overhead`.** Add `RimMandrake.CreatureBehaviors.RM_SunHeatExtension` to `RM_Webwork`:
   `heatKind overhead` (the sheet measures 38.6 / 49.2 / 58.2 °C p10/median/p90 under a sun median of
   +51°); sun elevation from the map tile's latitude, never a region name;
   `overheadAboveElevationDegrees` so a low-sun Webwork tile uses `lowSun` cover rules;
   `heatOffsetC` an invented first value, tuned in live play (keep it modest: the biome is already hot).
   No new heat hediff: vanilla heatstroke does the work. The light-moat now cuts both ways, as the review
   says: the sunlit clearing that keeps the owners out is where colonists overheat, and the canopy is
   cool but never safe (sheet ban 6).
2. **The sun-scald reads the shade grid.** `RM_Hediff_SunScald`
   (`src/RimMandrake/CreatureBehaviors/Source/RM_Hediff_SunScald.cs` l.48) keys on vanilla `InSunlight`,
   which ignores trees, so on a dayside with no night the ollathrix scalds on every unroofed cell of its
   own jungle (finding 3). Re-key it to `RM_MapComponent_ShadeGrid.ShadeAt(cell)` (roof, cast shade from
   vertical casters, gear, parasol, moving shade): exposed when `ShadeAt` is below a threshold (Mod
   Settings, default 0.5), else shaded. When the grid is off or not ready, fall back to `InSunlight`
   (today's behaviour), so the all-off case degrades gracefully. The scald stays a **light** hediff,
   worded as light ("sun-scald", "sunlight"), never as heat.
3. 🔴 **UNMEASURED: does the grid cast shade from the Webwork's trees?** The review reads "casts shade
   from big plants as well as roofs" from source; confirm which plant defs count as vertical casters
   (size / `fillPercent` / a caster extension) and that `RM_Kollavane` and the canopy trees qualify. If
   they do not, give the canopy trees whatever the grid reads (an extension or a fill value), not a new
   shade system.
4. **Mod Settings:** a toggle "sun-scald reads tree shade" (on by default) and the threshold; the
   existing sun-heat toggles cover the heat kind.

Reuse only: `RM_SunHeatExtension`, `RM_MapComponent_ShadeGrid`, the `Thing.AmbientTemperature` postfix in
`RM_SunHeatPatches`. Nothing new beyond the re-key.

Depends on: nothing open. Blocks: `WEBWORK_FELLED_NOON_RITE_1` (the owners stop at the shade line only if
the scald reads real shade).

## criteria

Deterministic state reads through debug `[Tool]`s, recorded in the Webwork functional script:
- `BiomeDef/RM_Webwork` carries `RM_SunHeatExtension` with `heatKind` = overhead; on a Webwork map
  `RM_MapComponent_ShadeGrid.SunHeatActive` is true and `ExposureAt` of an open clearing cell is greater
  than that of a cell under the kollavane canopy.
- Selftest (no game): the scald's exposure predicate returns exposed for `ShadeAt` 0.0, shaded for
  `ShadeAt` 0.9, and falls back to `InSunlight` when the grid is disabled.
- On a Webwork map: an `RM_Ollathrix` held for 2,500 ticks on an unroofed cell with `CastShadeAt` ≥ the
  threshold (under trees) ends with `RM_Webwork_SunScald` severity not higher than it started; held the
  same time on a clearing cell with `ShadeAt` 0, severity has risen.
- A colonist standing in that clearing reads a higher `AmbientTemperature` than one under the canopy; no
  new hediff def exists for heat.
- Toggle "sun-scald reads tree shade" off: the canopy case scalds again (vanilla `InSunlight` behaviour).
