import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/spawn_pawn", {"kindDef": "RSW_Jawa", "x": 182, "z": 137, "faction": "PlayerColony"})
    print("SPAWN_NEW", json.dumps(r)[:1200])
