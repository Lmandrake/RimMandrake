cd "$(dirname "$0")/../../../../../../.."; V=design/concepts/Pyrelands/version/in_game/visit_9
until grep -q "END b7\|STOPPED at grass" $V/evidence/runner.log; do sleep 5; done
bash $V/scripts/runner.sh b8 PYRE_PLANT_BURNLINE_TOGGLE_IGNORED=1:burn_line_off_control@off_control_planted burn_line@burn_line2 +script:$V/scripts/lanes_probe.py firehawk_first_sighting_letter@letter firehawk_crestfeather_yield@crest mapgen_log@mapgen2 furnace_warmth fire_sense animal_census
