import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
BS = chr(92)
with RimBridge(host, port, token) as rb:
    ch = rb.call("rimworld/list_debug_action_children", {"path": "Actions" + BS + "Set terrain (rect)..."})
    node = [c["path"] for c in ch.get("children", []) if c["path"].split(BS)[-1] == "GrasslandSoil"]
    print("node:", node[:1])
    r = rb.call("rimworld/execute_debug_action", {"path": node[0]})
    print("tool:", r.get("success"))
    for zb in range(0, 250, 25):
        rb.call("rimworld/click_cell", {"x": 0, "z": zb})
        rb.call("rimworld/click_cell", {"x": 249, "z": min(zb + 24, 249)})
    print("repainted")
    time.sleep(0.5)
    print(rb.call("rimworld/take_screenshot", {}).get("path"))
