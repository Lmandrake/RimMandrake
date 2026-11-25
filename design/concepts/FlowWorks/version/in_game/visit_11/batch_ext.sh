#!/bin/bash
# batch_ext.sh <check>:<chain> ... : extension_proof chains on the calm dry site through run_row.py, inside a 3000 s budget
cd "$(dirname "$0")/../../../../../.."
R=design/concepts/FlowWorks/version/in_game/visit_11/run_row.py
start=$(date +%s)
for tc in "$@"; do
  t=${tc%%:*}; c=${tc#*:}
  left=$(( 3000 - ($(date +%s) - start) ))
  if [ $left -lt 400 ]; then echo "NOT STARTED (budget): $t"; continue; fi
  python3 $R "$t" --timeout 600 -- python.exe -u src/RimMandrake/FlowWorks/northstar/extension_proof.py --live --site dry --site-save calm --chains "$c" --out OUT 2>&1 | head -1
done
