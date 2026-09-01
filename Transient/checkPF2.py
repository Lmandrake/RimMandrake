import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r1 = rb.call("jawa/spawn_pawn", {"kindDef": "Jawa_Homestead_Grunt", "count": 4, "x": 70, "z": 60, "faction": "OutlanderCivil"})
    r2 = rb.call("jawa/spawn_pawn", {"kindDef": "Jawa_DeepDesert_Grunt", "count": 4, "x": 80, "z": 60, "faction": "TribeCivil"})
    ids = [p["id"] for p in (r1.get("pawns") or [])+(r2.get("pawns") or []) if p.get("ok")]
    print("spawned:", len(ids), ids[:8])
    rb.call("rimworld/save_game", {"saveName": "qt_flavor_probe2"})
