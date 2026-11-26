cd "$(dirname "$0")/../../../../../../.."; V=design/concepts/Pyrelands/version/in_game/visit_8
PYRE_WALK=1 PYRE_WALK_PARTS_ONLY=1 bash $V/scripts/runner.sh tier5walk walk_season@walk_parts_tier
bash $V/scripts/runner.sh tier5 burrowers firehawk firehawk_first_sighting_letter plant_census,scorchfruit_fire_born@scorchfruit fire_tick_effects furnace_warmth fresh_burn_bonus grass_cover,embergrass_regrow@regrow
