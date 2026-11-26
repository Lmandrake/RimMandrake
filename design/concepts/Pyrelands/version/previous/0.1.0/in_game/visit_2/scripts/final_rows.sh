#!/bin/bash
# Visit 2: rewrite rows.jsonl from the evidence of the last run of each check (python3, offline). Checks with no driver
# evidence (not run, or a standalone script) get their rows from add_rows.py.
cd "$(dirname "$0")/../../../../../../.." || exit 1
V2=design/concepts/Pyrelands/version/in_game/visit_2
E=$V2/evidence
: > $V2/rows.jsonl
python3 $V2/scripts/make_rows.py \
  "P_startup_and_def_wiring=$E/pv2_a.json#startup_and_def_wiring" \
  "P_mapgen_log=$E/pv2_a.json#mapgen_log" \
  "P_grass_cover=$E/pv2_a.json#grass_cover" \
  "P_animal_census=$E/pv2_plant_census+scorchfruit_fire_born+animal_census.json#animal_census" \
  "sc_populations=$E/pv2_plant_census+scorchfruit_fire_born+animal_census.json#plant_census+animal_census" \
  "sc_scorchfruit=$E/pv2_plant_census+scorchfruit_fire_born+animal_census.json#scorchfruit_fire_born" \
  "sc_ruins=$E/pv2_a.json#ruins" \
  "sc_ash_ground=$E/pv2_ground_deep_ash.json#ground_deep_ash" \
  "sc_fire_dusts_ash=$E/pv2_fire_tick_effects.json#fire_tick_effects" \
  "P_ambient_ash_drift=$E/pv2_ambient_ash_drift.json#ambient_ash_drift" \
  "sc_firehawk=$E/pv2_firehawk.json#firehawk" \
  "sc_ashwallow=$E/pv2_burrowers_night.json#burrowers" \
  "sc_heat_dome=$E/pv2_heat_dome.json#heat_dome" \
  "sc_furnace=$E/pv2_furnace_warmth.json#furnace_warmth" \
  "P_furnace_room=$E/pv2_furnace_room.json#furnace_room" \
  "sc_ullai=$E/pv2_ullai_and_giant.json#ullai_and_giant~ullai_wired+herd_follows_two_day_old_burn" \
  "sc_furnace_giant=$E/pv2_ullai_and_giant.json#ullai_and_giant~giant_furnace_beast+giant_margin_over_roster+giant_classic_restore_control" \
  "sc_sand_shovel=$E/pv2_sand_shovel.json#sand_shovel" \
  "sc_firefoam_sprayer=$E/pv2_firefoam_sprayer.json#firefoam_sprayer" \
  "sc_foreign_arrivals=$E/pv2_foreign_arrivals.json#foreign_arrivals" \
  "sc_fire_sense=$E/pv2_fire_sense.json#fire_sense" \
  "sc_no_rain=$E/pv2_no_ordinary_rain.json#no_ordinary_rain" \
  "sc_three_skies=$E/pv2_cinderfall+blackrain.json#cinderfall+blackrain" \
  "P_blackrain=$E/pv2_cinderfall+blackrain.json#blackrain" \
  "sc_firehawk_rewards=$E/pv2_firehawk_first_sighting_letter.json#firehawk_first_sighting_letter" \
  "firehawk_first_sighting_letter=$E/pv2_firehawk_first_sighting_letter.json#firehawk_first_sighting_letter~firehawk_first_sighting_letter_once+firehawk_first_sighting_letter_toggle_off" \
  "firehawk_crestfeather_yield=$E/pv2_firehawk_crestfeather_yield.json#firehawk_crestfeather_yield" \
  "sc_flamefang_venom=$E/pv2_flamefang_venom.json#flamefang_venom" \
  "sc_furnace_bed=$E/pv2_furnace_sleep.json#furnace_sleep" \
  "sc_furnace_hide_bank=$E/pv2_furnace_hide_bank.json#furnace_hide_bank" \
  "sc_roof_withers=$E/pv2_roof_withers.json#roof_withers" \
  "sc_ash_watered=$E/pv2_ash_fertility_watered.json#ash_fertility_watered" \
  "sc_burn_compounds=$E/pv2_fresh_burn_bonus.json#fresh_burn_bonus" \
  "P_ashfall_weather_accumulation=$E/pv2_ashfall_weather_accumulation.json#ashfall_weather_accumulation" \
  "P_ashfall_drifts=$E/pv2_ashfall_drifts.json#ashfall_drifts" \
  "sc_burn_line_walks=$E/pv2_burn_line.json#burn_line" \
  "sc_herd_thirst=$E/pv2_herd_thirst.json#herd_thirst" \
  "sc_grass_regreens=$E/pv2_embergrass_regrow.json#embergrass_regrow" \
  "P_scorchfruit_spoils=$E/pv2_scorchfruit_spoils.json#scorchfruit_spoils" \
  "P_scorchfruit_produces=$E/pv2_scorchfruit_produces.json#scorchfruit_produces" \
  "sc_rite_hook_alone=$E/pv2_rite_hook_alone.json#rite_hook_alone@pyrelands_rite"
[ -f $E/pv2_walk_season.json ] && python3 $V2/scripts/make_rows.py "sc_walk=$E/pv2_walk_season.json#walk_season@full"
python3 $V2/scripts/add_rows.py
