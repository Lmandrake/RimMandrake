"""ids.py SUBSTR [MAPID] -- ids/pos/faction of pawns whose id contains SUBSTR (full list, no truncation)."""
import sys, time
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h_, p_, t_ = resolve_endpoint()
with RimBridge(h_, p_, t_) as B:
    if len(sys.argv) > 2:
        B.call("jawa/set_current_map", {"mapId": int(sys.argv[2])}); time.sleep(0.5)
    for p in (B.call("jawa/list_pawns", {}) or {}).get("pawns") or []:
        if sys.argv[1] in str(p.get("id")):
            print(p.get("id"), p.get("x"), p.get("z"), p.get("faction"), "dead" if p.get("dead") else "")
