import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for _ in range(4):
        r = rb.call("rimworld/close_window", {})
        if not r.get("success"): break
        print("closed:", str(r.get("message", ""))[:60])
    rb.call("rimworld/jump_camera_to_cell", {"x": 30, "z": 215})
    time.sleep(0.4)
    print(rb.call("rimworld/take_screenshot", {}).get("path"))
