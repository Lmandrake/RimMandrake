import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    # spawn astrofuel beside the tanks (deck cells)
    for x, z, n in ((150,148,150),(150,151,150),(151,148,150),(151,151,150)):
        s = rb.call("rimworld/spawn_thing", {"defName": "VGE_Astrofuel", "x": x, "z": z, "stackCount": n})
        print("spawn:", s.get("success"), s.get("thingId"))
    p = rb.call("jawa/list_pawns", {"faction": "PlayerColony", "limit": 10})
    cols = p.get("pawns", [])
    print("colonists:", [(c.get("id"), c.get("name") or c.get("label")) for c in cols])
