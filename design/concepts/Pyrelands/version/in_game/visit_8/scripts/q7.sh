cd "$(dirname "$0")/../../../../../../.."; V=design/concepts/Pyrelands/version/in_game/visit_8
until grep -q "END tier6walk\|STOPPED at walk_season@walk_parts_tier: reload_rc=1 2[2-3]" $V/evidence/runner.log; do sleep 15; done
bash $V/scripts/runner.sh tier7 firehawk@firehawk2 PYRE_PLANT_FARHAWK_NO_SEEK=1:firehawk@firehawk_planted_no_seek fresh_burn_bonus@fresh_burn_bonus2 grass_cover,embergrass_regrow@regrow2
