cd "$(dirname "$0")/../../../../../../.."; V=design/concepts/Pyrelands/version/in_game/visit_8
until grep -q "END tier7\|STOPPED at firehawk\|STOPPED at fresh\|STOPPED at PYRE" $V/evidence/runner.log; do sleep 15; done
bash $V/scripts/runner.sh tier8 grass_cover,embergrass_regrow@regrow2
