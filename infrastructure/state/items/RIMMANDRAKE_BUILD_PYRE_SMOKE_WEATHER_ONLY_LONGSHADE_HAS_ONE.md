# RIMMANDRAKE_BUILD_PYRE_SMOKE_WEATHER_ONLY_LONGSHADE_HAS_ONE

## spec
Owner, 2026-11-13 (on RIMMANDRAKE_PROVE_PYRELANDS_IN_FOUR_SCENES, walk_season_on_the_pyre): *"And I won't miss having to sweep the ash away from all my paths to keep walking clear, or the choking smoke that
sometimes come as its own weather..."*

Absent (read 2026-11-13 at a68d89e622): the RM_Pyrelands weather table (`src/RimMandrake/Pyrelands/Defs/BiomeDefs/Pyrelands.xml`
baseWeatherCommonalities) holds no smoke weather. Cinderfall only tints its fog layer as "lit smoke". Our one smoke weather,
`RM_SmokeHazeCondition` (`src/RimMandrake/LongShade/Defs/IncidentDefs/RM_SmokeHaze.xml`), is the Long Shade's RELIEF haze and
allowed only there. Build a Pyrelands choking-smoke weather that rolls on its own, reads as smoke, and hampers or harms pawns out
in it with a readable sign (owner: no pawn suffers without one). Keep RM_FE_BlackRain the only rain-rated weather in the table
(the table's own comment: the x15 rain-on-fire roll is the mechanism). Mod Setting per the superb-settings rule (on/off, weight).
The exact effect (breathing hediff, mood, vision) is the builder's call within that; the season walk reads it live.
Census and walk criteria: `D:\ClaudeWork\rimmandrake\conductor\cards_20261113_am\walk_season_criteria.md`.

Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/pyre_smoke_weather_accept.py` exits 0 with `PASS 6/6`.
Watched failing at a68d89e622: `PASS 2/6 failed: smoke_weather_defined, smoke_weather_in_biome_table, smoke_weather_has_effect,
smoke_not_rain_rated`, exit 1. Passability: a planted smoke WeatherDef (in the table, rainRate 0, a modExtension) gave 6/6, as did one
read by C#; mutants failed only their row (no effect -> has_effect; rainRate 1 -> not_rain_rated + black_rain_only_rain; not in
table -> in_biome_table; black rain dropped -> old_weathers_kept + black_rain_only_rain; vanilla Rain added -> black_rain_only_rain).
The builder does not edit the test; a clause believed wrong goes to the Conductor.
