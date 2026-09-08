# AshkarrWeatherSuite — validation walk
subject: src/RimUtinni/AshkarrWeatherSuite  (packageId: mandrake.rut.weathersuite)
deps: mandrake.rsw.weathersuite (modDependencies + loadAfter)
list: minimal+mandrake.rsw.weathersuite
status-hint: Wires the generic terminator-band/nightside-band weather engine (mandrake.rsw.weathersuite) onto Ash'karr's real substellar point and band arcs, plus folk-sign flavor text patched onto five vanilla WeatherDefs.

## must be true

- Exactly one `PlanetGeometryDef` ships: `RUT_WS_AshkarrGeometry`, with substellarLat=0, substellarLon=0, terminatorBandMinArc=63, terminatorBandMaxArc=117, nightsideBandMinArc=117.
- Five vanilla WeatherDefs — `Clear`, `Fog`, `DryThunderstorm`, `SnowGentle`, `SnowHard` — have their `description` replaced to append a folk-sign sentence (each Replace is `PatchOperationConditional`-guarded, so a mismatch is a silent no-op, not a red error — the RESULT is what must be checked, never "patch applied").
- The folk-sign patch never touches `BiomeDef[defName="ZBiome_Grasslands"]` or any `baseWeatherCommonalities` field (verified distinct from FIRE_ECOLOGY_LOOP_1's own patch target at authoring time; a def dump of ZBiome_Grasslands should be unchanged by this mod's presence).
- No mechanic promised in the flavor text (static seasons, glass storms) actually exists yet — the text is intentionally silent about that v2 system.

## the walk

1. [L] Player.log after load contains no `Config error in mandrake.rut.weathersuite` and no XML error naming `WeatherGeometryDefs_Ashkarr.xml` or `AshkarrWeather_FolkSigns.xml`
2. [D] def read-back: PlanetGeometryDef `RUT_WS_AshkarrGeometry` exists; substellarLat=0; substellarLon=0; terminatorBandMinArc=63; terminatorBandMaxArc=117; nightsideBandMinArc=117
3. [D] def read-back: WeatherDef `Clear` description contains "Folk sign: a still, colorless sky"
4. [D] def read-back: WeatherDef `Fog` description contains "Folk sign: fog this thick"
5. [D] def read-back: WeatherDef `DryThunderstorm` description contains "Folk sign: count the gap"
6. [D] def read-back: WeatherDef `SnowGentle` description contains "Folk sign: snow this gentle"
7. [D] def read-back: WeatherDef `SnowHard` description contains "Folk sign: when hard snow comes on fast"
8. [B] jawa/get_defs {defType: "WeatherDef", fields: ["description"]} filtered to Clear/Fog/DryThunderstorm/SnowGentle/SnowHard → every one of the five RESOLVED (post-patch) descriptions contains "Folk sign:" — the check a matched-nothing Conditional cannot fake
9. [B] jawa/get_def {defType: "RimMandrake.StarWars.WeatherSuite.PlanetGeometryDef", defName: "RUT_WS_AshkarrGeometry"} → resolved fields match step 2 exactly, confirming the def loaded from THIS mod and not shadowed by another PlanetGeometryDef
10. [B] jawa/weather_get → weather system reports a current weather/condition with no error, confirming the WeatherDecider pathway these WeatherDefs feed is healthy with the new geometry def present
11. [S] (human pass) confirm the terminator storm-wall and dark-side aurora actually render at the correct band on the live planet map
