#!/bin/bash
cd "$(dirname "$0")/../../../../../.."
V=design/concepts/FlowWorks/version/in_game/visit_11
for i in $(seq 1 ${1:-8}); do
python.exe $V/load_site.py calm >/dev/null 2>&1
timeout 200 python.exe -u src/RimMandrake/FlowWorks/northstar/suspension_bridge_proof.py "$(wslpath -w $PWD/$V/evidence/und_loop_$i.json)" --only posts,grate,underpass 2>&1 | tr -d '\r' | grep "UND_floor" | cut -c1-3000
python3 -c "
import json;d=json.load(open('$V/evidence/und_loop_$i.json'))
bad=[(r['id'],r['status']) for r in d['rows'] if r['status']!='PASS' and not r['id'].startswith(('UND_raid','UND_L4','SB_sett'))];print($i,bad)
import sys;sys.exit(3 if any(x[0]=='UND_floor_path_walks_under' for x in bad) else 0)" || break
done
