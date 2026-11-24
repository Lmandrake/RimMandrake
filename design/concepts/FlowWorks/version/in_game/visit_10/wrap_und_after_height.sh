#!/bin/bash
# does sc_pawn_height leave something behind that loses the under-deck path (visit 10 hunt of UND_floor_path_walks_under)?
cd "$(dirname "$0")/../../../../../.."
V=design/concepts/FlowWorks/version/in_game/visit_10
N=src/RimMandrake/FlowWorks/northstar
python.exe -u $N/concept_scenes.py --scene scene_pawn_height --out "$(wslpath -w $PWD/$V/evidence/hunt_height.json)" 2>&1 | head -1 | cut -c1-200
python.exe $V/load_site.py calm >/dev/null 2>&1
python.exe -u $N/suspension_bridge_proof.py "$(wslpath -w $PWD/$V/evidence/hunt_und_after_height.json)" 2>&1 | tr -d '\r' | grep -E "UND_(floor|both)|40 rows" | cut -c1-3000
