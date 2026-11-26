cd "$(dirname "$0")/../../../../../../.."; V=design/concepts/Pyrelands/version/in_game/visit_9
until grep -q "END b2\|STOPPED at burn_line" $V/evidence/runner.log; do sleep 5; done
bash $V/scripts/runner.sh b3a script:$V/scripts/owed_text.py
PYRE_REGROW_PART=growth bash $V/scripts/runner.sh b3b embergrass_regrow@growth_real PYRE_PLANT_REGROW_WET_ROOTS_OFF=1:embergrass_regrow@growth_wet_off PYRE_PLANT_REGROW_NO_RING=1:embergrass_regrow@growth_no_ring
bash $V/scripts/runner.sh b3c grass_cover,embergrass_regrow@regrow2 furnace_warmth fire_sense animal_census
