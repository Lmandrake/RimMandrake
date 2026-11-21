# RIMMANDRAKE_BUILD_PYRE_CONTROLS_NO_BRIDGE_TOOL_CAN_RUN

Caused by RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_TWO_RUN_TWO (Stage 6 visit 2, 2026-11-20). Class HARNESS (the
instrument does not exist). One source event: the scenes (design/concepts/Pyrelands/scenes.json) name controls that the
bridge cannot stage, so the rows that hold them read UNMEASURED by construction, on every visit, and each leaves its whole
check UNMEASURED. Evidence: design/concepts/Pyrelands/version/in_game/visit_2/evidence/pv2_*.json.

## spec

The rows, with the reason each one prints:
- `plant_census` / `same_seed_gate_off_map` (sc_populations), `ground_deep_ash` / `ash_ground_gate_off_regeneration`
  (sc_ash_ground): no tool regenerates the site's tile with its seed, the gate held off through generation.
- `plant_census` / `wild_plant_allowlist_day` (sc_populations): no donor plant is in this tile's wild-plant pass and no
  tool adds one, so the allowlist on-day is not told apart.
- `ullai_and_giant` / `giant_classic_restore_control` (sc_ullai, sc_furnace_giant): RM_PyrelandsGiants.RestoreClassicFurnaceBeast
  is private; jawa/static_call reaches public statics only.
- `ash_fertility_watered` / `growth_rate_factor_temperature` (sc_ash_watered): Plant.GrowthRateFactor_Temperature is an
  instance property no tool reads.
- `no_ordinary_rain` / `forced_rain_becomes_black_rain` (sc_no_rain): no tool sets GameCondition_ForceWeather.weather.
  Visit 1's `scripts/rain_postfix.py` route (weather locked to Rain, `jawa/weather_roll_next`) did read the decider's
  swap live; it is a candidate.
- `ruins` / `vanilla_ruins_unpainted`, `no_ordinary_rain` / `forced_rain_vanilla_control`, `ground_deep_ash` /
  `ash_ground_vanilla_shore`: the scratch world has no free flat TemperateForest tile in its first 60,000 tiles (or the
  AridShrubland control rolled no water). This part is SITE.
- `furnace_hide_bank` / `furnace_hide_bank_warms_a_room` (sc_furnace_hide_bank, the whole check): "no free flat Tundra land tile among the first 60000 world tiles for the vanilla control map" (SITE, the scratch world).
- `fire_sense` / `fire_sense_roster_toggle_off`: RM_BiomesSettings.enabled["Pyrelands"] (a dictionary entry) has no setter.

For each row, decide one: build the read (a JawaBench [Tool], a public probe), restage it (a world with the control
biome), or remove the control from the scene if another row already decides its bar. A removal is the Designer's, not a
driver's: a control is part of what the scene rules out.

## verify

Each row named above reads PASS or FAIL on a visit, or is gone from the scene with a recorded reason.

## criteria

- No row of the Pyrelands scenes is UNMEASURED by construction.

## Acceptance test

Live only. Red now: on the visit-2 rows, every row listed above reads UNMEASURED with the reason quoted (seen 2026-11-20).
Green: none of them reads UNMEASURED for a missing tool or tile.

## refs

file: src/RimMandrake/Pyrelands/validation.py
file: design/concepts/Pyrelands/scenes.json
file: src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchCompanionProbeTools.cs
