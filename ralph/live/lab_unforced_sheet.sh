#!/bin/bash
# Sheet of the lab's unforced bends for one look: bash ralph/live/lab_unforced_sheet.sh OUTDIR LOOK OUT.png [--skip-tangle]
D=$1; L=$2; O=$3; shift 3
python3 - "$D/ba_$L.out.json" "$D/ba_$L.sharp.json" <<'PY'
import json, sys
B = json.load(open(sys.argv[1]))["bends"]
rows = [{"apex": [r["x"], r["z"]], "piece": r["piece"], "forced": False, "cls": "unforced", "turn": r["turn"]} for r in B["rows"] if r["why"] == "unforced"]
json.dump(rows, open(sys.argv[2], "w"))
PY
python3 ralph/live/lab_sharp_sheet.py Transient/lab/ba/worlds/ba_$L.json "$D/ba_$L.out.json" "$D/ba_$L.sharp.json" "$O" "$@"
