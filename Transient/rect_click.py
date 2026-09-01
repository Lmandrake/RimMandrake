import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("rimworld/click_cell", {"x": 79, "z": 129})
    print("click2:", r.get("success"), str(r.get("message",""))[:60])
    time.sleep(0.3)
    s = rb.call("rimworld/take_screenshot", {})
    print(s.get("path"))
