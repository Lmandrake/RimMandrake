#!/bin/bash
cd /home/mandrake/rm/relentless/clones/RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_ACCEPTANCE_VISIT_THREE.det
until grep -q "^END batch6" design/concepts/Pyrelands/version/in_game/visit_3/evidence/runner.log; do sleep 5; done
design/concepts/Pyrelands/version/in_game/visit_3/scripts/runner.sh batch7 flamefang_venom@flamefang_venom_repaired3
