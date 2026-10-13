"""BENCH round 1 (2026-10-13): read every player colonist on every map -- alive, Food need, Malnutrition/ToxicBuildup,
death/GameEnded letters. PYRE_SITE_FOOD_REPAIR_COLONY_STARVES: 'every colonist fed after the rows'.
  python.exe colony_fed.py <out.json> <label>
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402

out, label = sys.argv[1], sys.argv[2]
h, p, t = resolve_endpoint()
with RimBridge(h, p, t) as rb:
    mi = rb.call("jawa/map_info")
    allc = rb.call("rimworld/list_colonists", {"currentMapOnly": False}).get("colonists") or []
    site = rb.call("rimworld/list_colonists", {"currentMapOnly": True}).get("colonists") or []
    rows = rb.call("jawa/list_pawns", {"faction": "player", "includeHealth": True, "limit": 100}).get("pawns") or []
    pawns = []
    for r in rows:
        if (r.get("intelligence") or "") != "Humanlike":
            continue
        nd = rb.call("jawa/pawn_need", {"pawn": r.get("id"), "action": "list"})
        food = next((n.get("level") for n in nd.get("needs") or [] if n.get("need") == "Food"), None)
        hd = {x.get("def"): round(x.get("severity") or 0, 3) for x in (r.get("health") or {}).get("hediffs") or []
              if x.get("def") in ("Malnutrition", "ToxicBuildup", "Heatstroke", "Dehydration")}
        pawns.append({"id": r.get("id"), "name": r.get("name"), "dead": r.get("dead"), "downed": r.get("downed"),
                      "food": food, "hediffs": hd, "xz": [r.get("x"), r.get("z")]})
    L = rb.call("rimworld/list_letters").get("letters") or []
    bad = [x.get("label") for x in L if x.get("letterDef") in ("Death", "GameEnded")]
res = {"label": label, "tick": mi.get("ticksGame"), "map": [mi.get("mapId"), mi.get("mapBiome")],
       "colonistsAllMaps": len(allc), "colonistsSite": len(site), "pawns": pawns, "deathLetters": bad,
       "fed": bool(pawns) and all(not x["dead"] and (x["food"] or 0) > 0.25 and "Malnutrition" not in x["hediffs"] for x in pawns)}
with open(out, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1)
print(json.dumps(res))
