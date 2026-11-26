cd "$(dirname "$0")/../../../../../../.."; V=design/concepts/Pyrelands/version/in_game/visit_9
export OFF_TICKS=131000
bash $V/scripts/runner.sh b5 +script:$V/scripts/off_control_source.py@off_src131 HOLD_FURNACE=1:+script:$V/scripts/off_control_source.py@off_src131_furnace
unset OFF_TICKS
PYRE_REGROW_PART=growth bash $V/scripts/runner.sh b6 PYRE_PLANT_REGROW_WET_ROOTS_OFF=1:embergrass_regrow@growth_wet_off
bash $V/scripts/runner.sh b7 grass_cover,embergrass_regrow@regrow2
