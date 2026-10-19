# WEATHER_MAST_DELETE_BAROMETER_GOES_QUIET

Owner cards 2026-10-19: the weather instrument mast → "Delete it"; Tiers 2-4 and the
"seen on the main map" tier → "Cut them permanently". Assessment:
`design/RimMandrake/weather_sensing_descope_2026-10-19.md`.

## Done offline (this item's commit)
- Deleted `src/RimMandrake/WeatherSuite/Defs/ThingDefs_Buildings/ThingDefs_WeatherInstrument.xml`
  (no research, recipe, Keyed string, patch, Mod Settings row or owned texture existed; the
  mast drew vanilla `Things/Building/Misc/DropBeacon`).
- `CompProperties_Forecaster` / `CompForecaster` removed from `Source/WeatherSuiteHook.cs`;
  `RM_WeatherKernel.TopShares` removed; forecast fuzz family, 6 forecast mutants and the
  forecast-sort lint rule removed; the validation chain
  `weather_instrument_reports_a_live_forecast_reading` and walk steps 8-9 removed.
- `WeatherSuiteHook.dll` rebuilt on the staging drive (winbuild); it still carries
  `WeatherGeometryUtility.ArcFromSubstellar` (UtinniPatches), the terminator band and the
  nightside aurora.
- About.xml: the forecast-instrument sentence removed. `weather_suite_deep_design.md` §8 cut
  to Tier 0 folk signs (D2 was not asked; folk signs untouched).

## Owed at the next game-down window
`python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod WeatherSuite` (plan, then `--apply`):
the deployed copy still has the mast def and the old DLL. Expect one harmless
"could not load reference" per save that names the def: 68 of 345 saves on 2026-10-19,
all inside Vanilla Trading Expanded `priceHistoryRecorders` or CaravanAdventures
`packUpFilter/allowedDefs`; no save holds a built mast (`<def>RM_WS_WeatherInstrument</def>`: 0).
