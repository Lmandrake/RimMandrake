import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

with RimBridge(host, port, token) as rb:
    rb.call("jawa/clear_ui", {})
    rb.call("rimworld/jump_camera_to_cell", {"x": 58, "z": 42})
    time.sleep(1)
    r = rb.call("rimworld/take_screenshot", {"fileName": "droidworks_minimal_quicktest_wave1.png"})
    print(json.dumps(r))
