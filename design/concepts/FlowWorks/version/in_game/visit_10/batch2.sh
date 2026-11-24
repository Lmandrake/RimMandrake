#!/bin/bash
cd "$(dirname "$0")/../../../../../.."
V=design/concepts/FlowWorks/version/in_game/visit_10
R=$V/run_row.py
N=src/RimMandrake/FlowWorks/northstar
python3 $R sc_pit_crowd --timeout 500 -- python.exe -u $N/pit_crowd_live.py --out OUT 2>&1 | head -1
python3 $V/load_site.py calm >/dev/null 2>&1
python3 $R sc_canal_fire --timeout 300 -- python.exe -u $N/x10_canal_fire_live.py --out OUT 2>&1 | head -1
python3 $R sc_hung_bridge --timeout 600 --site-key site.verified -- python.exe -u $N/suspension_bridge_proof.py OUT 2>&1 | head -1
for tc in sc_dig_and_read:plot_H_depth_ladder sc_dig_finds:dig_finds sc_fill_tiers:plot_B_fill_tiers sc_slime:slime_slip sc_pit_reads:plot_G_pit sc_covered_pit:pit_cover_fall sc_sluice:flow_doors sc_one_network:machinery_pipes; do
  t=${tc%%:*}; c=${tc#*:}
  python3 $R "$t" --timeout 600 -- python.exe -u $N/extension_proof.py --live --site dry --site-save calm --chains "$c" --out OUT 2>&1 | head -1
done
python3 $R sc_pawn_height --timeout 600 -- python.exe -u $N/concept_scenes.py --scene scene_pawn_height --out OUT 2>&1 | head -1
