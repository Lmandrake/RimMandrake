import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ch = rb.call("rimworld/list_debug_action_children", {"path": "Actions\\Spawn Pawn..."})
    kids = ch.get("children", [])
    print("total spawn-pawn children:", len(kids))
    hits = [c["path"] for c in kids if "DW_" in c["path"] or "Gonk" in c["path"] or "GNK" in c["path"].upper()]
    print("DW/Gonk hits:", len(hits))
    for h in hits[:80]:
        print(h)
