#!/bin/bash
cd "$(dirname "$0")/../../../../../.."
V=design/concepts/FlowWorks/version/in_game/visit_10
R=$V/run_row.py
N=src/RimMandrake/FlowWorks/northstar
python.exe $V/load_site.py calm "$(wslpath -w $PWD/$V/evidence/calm_hung.log)" | cut -c1-100
python3 $R sc_hung_bridge --timeout 600 --site-log $V/evidence/calm_hung.log 'verified=True' -- python.exe -u $N/suspension_bridge_proof.py OUT 2>&1 | head -1
python.exe $V/load_site.py calm "$(wslpath -w $PWD/$V/evidence/calm_ways.log)" | cut -c1-100
python3 $R sc_ways_out --timeout 900 --site-log $V/evidence/calm_ways.log 'verified=True' -- python.exe -u $N/live_session.py --only B0,B4 --no-owner-save --out-dir 'design\concepts\FlowWorks\version\in_game\visit_10\evidence\ls_b4_site' 2>&1 | head -3
