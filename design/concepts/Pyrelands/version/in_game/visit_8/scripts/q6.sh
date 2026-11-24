cd "$(dirname "$0")/../../../../../../.."; V=design/concepts/Pyrelands/version/in_game/visit_8
until grep -q "END tier5 \|STOPPED at [^w]" <(sed -n '/START tier5 /,$p' $V/evidence/runner.log); do sleep 15; done
PYRE_WALK=1 PYRE_WALK_PARTS_ONLY=1 bash $V/scripts/runner.sh tier6walk walk_season@walk_parts_tier
