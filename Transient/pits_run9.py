import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=20) as rb:
    sel = rb.call("rimworld/select_pawn", {"pawnName": "Ark"})
    print("select:", json.dumps(sel)[:500])
    kids = rb.call("rimworld/list_debug_action_children", {"path": "Actions"})
    labels = [c["label"] for c in kids["children"]]
    hits = [l for l in labels if "prison" in l.lower() or "arrest" in l.lower() or "captur" in l.lower()]
    print("hits now:", hits)
    print("visible count now:", len(labels))
