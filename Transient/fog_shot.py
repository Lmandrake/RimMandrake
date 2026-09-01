import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
BS = chr(92)
with RimBridge(host, port, token) as rb:
    r = rb.call("rimworld/execute_debug_action", {"path": "Actions" + BS + "Clear All Fog"})
    print("fog:", r.get("success"))
    for _ in range(4):
        c = rb.call("rimworld/close_window", {})
        if not c.get("success"): break
        print("closed:", str(c.get("message", ""))[:50])
    rb.call("rimworld/jump_camera_to_cell", {"x": 30, "z": 215})
    time.sleep(0.4)
    print(rb.call("rimworld/take_screenshot", {}).get("path"))
