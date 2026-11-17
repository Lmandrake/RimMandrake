## spec
Found by the Graffiti 0.1.0 blind challenge, cycle 2 (RIMMANDRAKE_JUDGE_GRAFFITI_BLIND_CYCLE_TWO_TESTS_FIRST), 2026-11-17. Class: **Problem**, bar `weathering_bounds_marks`.

**Criterion:** tree.json weathering_bounds_marks: a mark disappears after its weather days 'sooner outdoors than under a roof'; T_WEATHER_OFFLINE is a decider (with sc_weathered_raid_mark) and reads Filth_Mark

**Evidence:**
- planted fault PF_C_WEATHER_ROOF_INVERTED (Filth_Mark.WeatherStepNow passes `Map.roofGrid.Roofed(Position)` as WeatherDays' outdoors: every roofed mark gets the outdoor life) left T_WEATHER_OFFLINE green; the kernel half proves roofed > unroofed only for the kernel's own argument, and the source half read only the permanent rule
- red: python3 design/concepts/Graffiti/version/blind_challenge/cycle_2/lane2/catch_check.py --fault PF_C_WEATHER_ROOF_INVERTED --test T_WEATHER_OFFLINE rc 1 (MISSED) on the parent of dad3e902ac; lane2/fixes.jsonl

**Smallest fix:** the source half also reads WeatherStepNow's WeatherDays call: 4 arguments, the third exactly `!Map.roofGrid.Roofed(Position)`; a fifth source mutant (the roof read the wrong way round)

Record: `design/concepts/Graffiti/version/blind_challenge/cycle_2/lane2/faults.json`.

## criteria
T_WEATHER_OFFLINE red on the inverted roof and green on the shipped source

## verify
Acceptance test: `python3 design/concepts/Graffiti/version/blind_challenge/cycle_2/lane2/catch_check.py --fault PF_C_WEATHER_ROOF_INVERTED --test T_WEATHER_OFFLINE` rc 0 (CAUGHT), and `python3 src/RimMandrake/Utils/selftest_graffiti_weather.py` rc 0. Watched fail on the base (rc 1) and pass at dad3e902ac: `lane2/fixes.jsonl`. FIXED dad3e902ac9d2e7c9a85e0a6d088e2047144ad4d.
