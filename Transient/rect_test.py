import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
BS = chr(92)
with RimBridge(host, port, token) as rb:
    rb.call("rimworld/jump_camera_to_cell", {"x": 75, "z": 125})
    s1 = rb.call("rimworld/take_screenshot", {})
    print("shot1:", s1.get("path"))
    ch = rb.call("rimworld/list_debug_action_children", {"path": "Actions" + BS + "Set terrain (rect)..."})
    kids = [c["path"] for c in ch.get("children", [])]
    grass = [p for p in kids if p.split(BS)[-1].startswith("VFEArch_Grass")]
    print("grass node:", grass[:2], "| children:", len(kids))
    if not grass: sys.exit(0)
    r = rb.call("rimworld/execute_debug_action", {"path": grass[0]})
    print("activate:", r.get("success"), str(r.get("message", ""))[:80])
    d = rb.call("rimworld/drag_cell", {"fromX": 70, "fromZ": 120, "toX": 79, "toZ": 129})
    print("drag:", d.get("success"), str(d.get("message", ""))[:80])
    time.sleep(0.5)
    s2 = rb.call("rimworld/take_screenshot", {})
    print("shot2:", s2.get("path"))
