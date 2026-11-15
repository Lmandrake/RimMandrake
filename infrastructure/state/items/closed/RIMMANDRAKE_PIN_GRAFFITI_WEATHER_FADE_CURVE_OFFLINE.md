# RIMMANDRAKE_PIN_GRAFFITI_WEATHER_FADE_CURVE_OFFLINE

Found by the Stage 2 preflight of Graffiti 0.1.0 (steward run RIMMANDRAKE_STEWARD_GRAFFITI_PREFLIGHT_STAGE, 2026-11-15); table `design/concepts/Graffiti/version/test_table.json`, record `design/concepts/Graffiti/version/preflight.json`.

## spec
Test T_WEATHER_OFFLINE in the table, specified at Stage 2, built at Stage 3 (red first). Observes: fade curve: WeatherDays roofed > unroofed for every form and craft; WeatherFade alpha 1 before 60% of life, 0 at its end, monotone; a permanent mark never fades; mutants go red
File: `src/RimMandrake/Utils/selftest_graffiti_weather.py`. Reads: src/RimMandrake/Graffiti/Source/Kernel/RM_GraffitiKernel.cs, src/RimMandrake/Graffiti/Source/Filth_Mark.cs

## verify
Acceptance test: `python3 src/RimMandrake/Utils/selftest_graffiti_weather.py` exits 0 on the shipped mod and goes red on a planted mutant of the behaviour (watched failing 2026-11-15: the file does not exist yet). Expected: 1 pass.
