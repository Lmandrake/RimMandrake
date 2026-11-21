#!/bin/bash
cd /home/mandrake/rm/relentless/clones/RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_ACCEPTANCE_VISIT_THREE.det
while kill -0 1445006 2>/dev/null; do sleep 5; done
echo "DONE ullai_and_giant (batch2 child, runner stopped) 09:44:35" >> design/concepts/Pyrelands/version/in_game/visit_3/evidence/runner.log
sleep 12
design/concepts/Pyrelands/version/in_game/visit_3/scripts/runner.sh batch3 firehawk@firehawk_rerun ruins@ruins_repaired +script:design/concepts/Pyrelands/version/in_game/visit_3/scripts/plant_ruins_unpaint.py@plant_ruins_unpaint +ruins@ruins_planted no_ordinary_rain@no_ordinary_rain_repaired firefoam_sprayer@firefoam_sprayer_sampled
PYRE_PLANT_NO_RAIN_GATE_OFF=1 design/concepts/Pyrelands/version/in_game/visit_3/scripts/runner.sh batch3b no_ordinary_rain@no_ordinary_rain_planted
PYRE_PLANT_CONTROL_HAS_SPRAYER=1 design/concepts/Pyrelands/version/in_game/visit_3/scripts/runner.sh batch3c firefoam_sprayer@firefoam_sprayer_planted
PYRE_PLANT_ASHFALL_STRIKE=DryThunderstorm design/concepts/Pyrelands/version/in_game/visit_3/scripts/runner.sh batch3d cinderfall@cinderfall_planted_strike
