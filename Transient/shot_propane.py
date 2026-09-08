import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rb.call("rimworld/close_window", {"windowType": "LudeonTK.EditWindow_Log"})
    rb.call("jawa/clear_ui", {})
    v = rb.call("jawa/world_view", {"centerTile": 14301, "altitude": 420})
    print("world_view:", str(v)[:150])
    s = rb.call("rimworld/take_screenshot", {})
    print("shot:", s.get("path"))
