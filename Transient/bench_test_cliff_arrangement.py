import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    # horizontal row of face pieces, with top pieces one row "behind" (north, -z)
    ops = []
    for i in range(5):
        ops.append(f"Dirt_Hill_Right:{190+i},60")
    for i in range(5):
        ops.append(f"Dirt_HillTop_Right:{190+i},59")
    res = rb.call("jawa/build_batch", {"ops": ";".join(ops)})
    print(json.dumps(res)[:600])
    rb.call("jawa/clear_ui", {})
    rb.call("rimworld/jump_camera_to_cell", {"x": 192, "z": 60})
    rb.call("rimworld/set_camera_zoom", {"rootSize": 8})
    r2 = rb.call("rimworld/take_screenshot", {"fileName": "cliff_test_horizontal_2026-09-06"})
    print(r2.get("path") or r2)
