import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=20) as rb:
    colonists = rb.call("rimworld/list_colonists", {})["colonists"]
    pid = colonists[0]["pawnId"]
    name = colonists[0]["name"]
    print("targeting", name, pid)
    node = rb.call("rimworld/get_debug_action", {"path": "Actions\\Mental state..."})
    leaf = next(c for c in node["children"] if c["label"] == "RM_GraffitiPaintingSpreeState")
    print("leaf:", json.dumps({k: leaf.get(k) for k in ("path","actionType")}))
    r = rb.call("rimworld/execute_debug_action", {"path": leaf["path"], "pawnId": pid})
    print("force result:", json.dumps(r.get("effects"))[:400])
