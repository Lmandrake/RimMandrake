#!/bin/bash
cd /home/mandrake/rm/foundry
M=src/RimMandrake/MessyConduit
T() { s=$(date +%s); echo "== $1 start $(date +%T)"; shift; "$@" 2>&1 | tr -d '\r' | grep -E 'FAIL|UNMEASURED|UNBUILT|UNCOVER|LIVE:|live:|save-load:|TIMING|-> ' | cut -c1-230; echo "== done in $(( $(date +%s)-s ))s"; }
T core python.exe $M/validation.py --live --fresh-map
T save python.exe $M/validation.py --save-load MC_REC_CORE_D_20261004
T aerial python.exe $M/validation_aerial.py --live
T aerial_sl python.exe $M/validation_aerial.py --save-load MC_REC_AERIAL_D_20261004
T hose python.exe $M/validation_hose.py --live
T hose_sl python.exe $M/validation_hose.py --save-load MC_REC_HOSE_D_20261004
T matrix python.exe $M/northstar_matrix/run_live.py --live --fresh-map --no-shots --profile --catalog Transient/mc_scenes_20261004.json --out Transient/mc_matrix_rec4_20261004.json
echo ENDPLAN
