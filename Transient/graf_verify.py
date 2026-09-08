import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=25) as rb:
    colonists = rb.call("rimworld/list_colonists", {})["colonists"]
    pid = colonists[0]["pawnId"]
    x, z = colonists[0]["position"]["x"], colonists[0]["position"]["z"]
    print("target:", colonists[0]["name"], pid, x, z)
    for dx in range(-2, 3):
        rb.call("rimworld/spawn_thing", {"defName": "Wall", "x": x+dx, "z": z-3})
    node = rb.call("rimworld/get_debug_action", {"path": "Actions\\Mental state..."})
    leaf = next(c for c in node["children"] if c["label"] == "RM_GraffitiPaintingSpreeState")
    rb.call("rimworld/execute_debug_action", {"path": leaf["path"], "pawnId": pid})
    print("spree forced")
