import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

tile = int(sys.argv[1]) if len(sys.argv) > 1 else -1
alt = float(sys.argv[2]) if len(sys.argv) > 2 else 1100.0

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    try:
        rb.call("jawa/clear_ui", {})
    except Exception as e:
        print("clear_ui:", e)
    args = {"altitude": alt, "northUp": True}
    if tile >= 0: args["centerTile"] = tile
    v = rb.call("jawa/world_view", args)
    print("world_view ->", json.dumps({k: v for k, v in v.items() if k != "operation"})[:300])
    time.sleep(1.5)
    s = rb.call("rimworld/take_screenshot", {})
    print("shot ->", json.dumps({k: v for k, v in s.items() if k != "operation"})[:400])
