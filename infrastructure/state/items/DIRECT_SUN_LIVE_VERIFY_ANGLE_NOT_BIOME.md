# DIRECT_SUN_LIVE_VERIFY_ANGLE_NOT_BIOME — live rows for Direct Sun

Design: `design/RimMandrake/unified_direct_sun_heat_2026-10-19.md` §6. Blocked on
`DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES`. Replaces `SOLAR_HEAT_EXPOSURE_1` (its built shade grid,
sun pathing and rest-dash-rest stay; its per-biome heat kinds are ruled out, so its owed live rows
move here). Nothing here is built or verified.

## criteria

- **L1 (quicktest map + bridge, state reads only, no visuals).** Three maps at different sun
  elevations (a Long Shade, a Pyrelands and a Forge tile). On each, read `SunOffsetFor` and
  `ExposureFor` for one pawn in the open, under a roof, under a parasol and in a wall's lee. Equal E
  gives equal numbers whatever the biome; the lee is long at low E and absent at high E.
- **L1.** On the Forge, outdoor `map.mapTemperature` with `RM_ForgeAirHeat` on and off differs by
  its `temperatureOffset`; shade changes the sun term only.
- **L1.** On a fixed-sun map the sun elevation never changes across a day.
- **L2 (owner-watched sitting).** He tunes the zenith value, weather sun factors, the four air-heat
  offsets, and the rest-dash strictness carried over from `SOLAR_HEAT_EXPOSURE_1` (*"a tad boring
  unless we get really strict about the dashing animal behavior"*).
