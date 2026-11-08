"""hurts.py <name>... : every hediff of the named pawns (dead included): what hurt them (spikes, the fall, arrows)."""
import json
import sys

import fwb

B = fwb.FW()
allp = []
for f in ("hostile", "player"):
    allp += (B.call("jawa/pawn_census", faction=f, includeDead=True) or {}).get("pawns") or []
for p in allp:
    if p.get("name") not in sys.argv[1:]:
        continue
    h = B.call("jawa/pawn_health", pawn=p["id"]) or {}
    hs = h.get("hediffs") or h.get("health", {}).get("hediffs") or []
    print(p["name"], p["id"], "dead" if p.get("dead") else "", "at", p.get("x"), p.get("z"))
    for d in hs:
        print("   ", d.get("def") or d.get("defName") or d.get("label"), d.get("part") or d.get("bodyPart"), d.get("severity"),
              d.get("source") or d.get("sourceDef") or "", flush=True)
    if not hs:
        print("   ", json.dumps(h, default=str)[:600])
