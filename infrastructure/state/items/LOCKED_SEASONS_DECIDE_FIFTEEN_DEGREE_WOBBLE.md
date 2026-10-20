# LOCKED_SEASONS_DECIDE_FIFTEEN_DEGREE_WOBBLE

Owner question, from `WORLD_PHYSICS_AUDIT_LOCKED_SUN_TEMPS_RINGS` (`design/RimMandrake/world_physics_audit_2026-10-20.md` §3).
Under the tidal lock the DAILY swing is off (MEASURED: glow and Direct Sun constant across a day), but vanilla
`GenTemperature.OffsetFromSeasonCycle` still runs with the planet def's `seasonalTempVariationCurve` (0:15, 1:15, 2:5)
at |lat|/90: a ±15 °C seasonal swing on every tile, opposite in each hemisphere (live: ±1.25 °C offsets with hemisphere
sign on 2nd Aprimay). A locked planet with no tilt has no seasons; the biome sheets quote one temperature per tile.
## Options for the card
- A: keep ±15 °C seasons (the mod's choice).
- B: zero it — patch the TidallyLocked PlanetTypeDef's `seasonalTempVariationCurve` to 0 (XML patch, our tier).
- C: small (e.g. ±3 °C), named as an orbital eccentricity in lore.
## criteria
- owner decision recorded; if B/C, `AverageTemperatureAtTileForTwelfth` spread on a sample tile matches it
