import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/spawn_pawn", {"kindDef": "RSW_Jawa", "x": 184, "z": 137, "faction": "PlayerColony"})
    print("SPAWN", json.dumps(r)[:1200])
    lp = rb.call("jawa/list_pawns", {})
    print("IMMEDIATELY_AFTER_COUNT", len(lp.get("pawns", [])))
    found = [p for p in lp.get("pawns", []) if "Human" in (p.get("id") or "") and p.get("faction")=="PlayerColony"]
    for p in found:
        print(" ", p.get("id"), p.get("name"))
