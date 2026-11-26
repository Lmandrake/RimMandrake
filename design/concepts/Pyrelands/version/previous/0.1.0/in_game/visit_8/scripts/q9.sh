cd "$(dirname "$0")/../../../../../../.."; V=design/concepts/Pyrelands/version/in_game/visit_8
until grep -q "END tier8\|STOPPED at grass" $V/evidence/runner.log; do sleep 15; done
export PYRE_WALK=1
PYRE_WALK_ONE=walk_master_off_then_on bash $V/scripts/runner.sh tier9a walk_season@walk_master_real PYRE_PLANT_MASTER=left_on:walk_season@walk_master_left_on PYRE_PLANT_MASTER=left_off:walk_season@walk_master_left_off
PYRE_WALK_ONE=walk_gate_off_then_on bash $V/scripts/runner.sh tier9b PYRE_PLANT_GATE_IGNORED=1:walk_season@walk_gate_planted2
PYRE_WALK_ONE=walk_roster_toggle bash $V/scripts/runner.sh tier9c PYRE_PLANT_ROSTER_IGNORED=1:walk_season@walk_roster_planted
bash $V/scripts/runner.sh tier9d animal_census burn_line@burn_line3
