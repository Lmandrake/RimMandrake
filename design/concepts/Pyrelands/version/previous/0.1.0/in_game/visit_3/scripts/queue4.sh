#!/bin/bash
cd /home/mandrake/rm/relentless/clones/RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_ACCEPTANCE_VISIT_THREE.det
until grep -q "^END batch3d" design/concepts/Pyrelands/version/in_game/visit_3/evidence/runner.log; do sleep 5; done
design/concepts/Pyrelands/version/in_game/visit_3/scripts/runner.sh batch4a firefoam_sprayer@firefoam_sprayer_sampled2
PYRE_PLANT_CONTROL_HAS_SPRAYER=1 design/concepts/Pyrelands/version/in_game/visit_3/scripts/runner.sh batch4b firefoam_sprayer@firefoam_sprayer_planted2
design/concepts/Pyrelands/version/in_game/visit_3/scripts/runner.sh batch4c flamefang_venom ash_fertility_watered plant_census,scorchfruit_fire_born@scorchfruit_fire_born_with_census script:src/RimMandrake/Pyrelands/firefoam_aim_live_proof.py script:src/RimMandrake/Pyrelands/gate_live_proof.py script:src/RimMandrake/Pyrelands/wind_burn_live.py script:design/concepts/Pyrelands/version/in_game/visit_3/scripts/walk_save.py fresh_burn_bonus burn_line scorchfruit_spoils embergrass_regrow
