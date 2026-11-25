#!/bin/bash
# batch.sh <check>... : run concept scenes in order through run_row.py; stop starting new ones when under 200 s of the 3000 s shell budget remains
cd "$(dirname "$0")/../../../../../.."
R=design/concepts/FlowWorks/version/in_game/visit_12/run_row.py
start=$(date +%s)
for t in "$@"; do
  left=$(( 3000 - ($(date +%s) - start) ))
  if [ $left -lt 400 ]; then echo "NOT STARTED (budget): $t"; continue; fi
  scene="scene_${t#sc_}"
  python3 $R "$t" --timeout 600 -- python.exe -u src/RimMandrake/FlowWorks/northstar/concept_scenes.py --scene "$scene" --out OUT 2>&1 | head -1
done
