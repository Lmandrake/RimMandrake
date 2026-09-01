import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
BS = chr(92)
with RimBridge(host, port, token) as rb:
    st = rb.call("rimworld/get_ui_state", {})
    print("windows:", json.dumps(st.get("windows") or st)[:300])
    for _ in range(3):
        r = rb.call("rimworld/close_window", {})
        print("close_window:", r.get("success"), str(r.get("message",""))[:60])
    ch = rb.call("rimworld/list_debug_action_children", {"path": "Actions" + BS + "Set terrain (rect)..."})
    node = [c["path"] for c in ch.get("children", []) if c["path"].split(BS)[-1] == "GrasslandSoil"][0]
    rb.call("rimworld/execute_debug_action", {"path": node})
    for zb in range(0, 250, 25):
        rb.call("rimworld/click_cell", {"x": 0, "z": zb})
        rb.call("rimworld/click_cell", {"x": 249, "z": min(zb + 24, 249)})
    print("repainted")
    time.sleep(0.5)
    rb.call("rimworld/jump_camera_to_cell", {"x": 112, "z": 130})
    print(rb.call("rimworld/take_screenshot", {}).get("path"))
