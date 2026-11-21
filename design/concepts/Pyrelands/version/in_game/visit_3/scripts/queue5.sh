#!/bin/bash
cd /home/mandrake/rm/relentless/clones/RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_ACCEPTANCE_VISIT_THREE.det
while kill -0 1572012 2>/dev/null; do sleep 5; done
echo "DONE ash_fertility_watered (batch4c child, runner stopped to put firefoam first) $(date +%T)" >> design/concepts/Pyrelands/version/in_game/visit_3/evidence/runner.log
sleep 12
design/concepts/Pyrelands/version/in_game/visit_3/scripts/runner.sh batch5a firefoam_sprayer@firefoam_sprayer_s3 flamefang_venom@flamefang_venom_repaired firefoam_sprayer@firefoam_sprayer_s4
PYRE_PLANT_RING_GAP=1 design/concepts/Pyrelands/version/in_game/visit_3/scripts/runner.sh batch5b firefoam_sprayer@firefoam_sprayer_gap_planted
design/concepts/Pyrelands/version/in_game/visit_3/scripts/runner.sh batch5c plant_census,scorchfruit_fire_born@scorchfruit_fire_born_with_census script:src/RimMandrake/Pyrelands/firefoam_aim_live_proof.py script:src/RimMandrake/Pyrelands/gate_live_proof.py script:src/RimMandrake/Pyrelands/wind_burn_live.py script:design/concepts/Pyrelands/version/in_game/visit_3/scripts/walk_save.py fresh_burn_bonus burn_line scorchfruit_spoils embergrass_regrow
