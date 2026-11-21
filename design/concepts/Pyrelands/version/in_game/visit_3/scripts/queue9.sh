#!/bin/bash
cd /home/mandrake/rm/relentless/clones/RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_ACCEPTANCE_VISIT_THREE.det
until grep -q "^END batch8" design/concepts/Pyrelands/version/in_game/visit_3/evidence/runner.log; do sleep 5; done
PYRE_PLANT_BURNLINE_TOGGLE_IGNORED=1 design/concepts/Pyrelands/version/in_game/visit_3/scripts/runner.sh batch9a burn_line_off_control@burn_line_off_control_planted
design/concepts/Pyrelands/version/in_game/visit_3/scripts/runner.sh batch9b burn_line@burn_line_rerun scorchfruit_spoils@scorchfruit_spoils_rerun
