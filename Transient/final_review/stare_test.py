import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rb.call("rimworld/close_window", {"windowType": "LudeonTK.Dialog_DevPalette"})
    cu = rb.call("jawa/clear_ui", {})
    print("clear_ui closed:", cu.get("closedCount"), "remaining:", cu.get("remaining"))
    v = rb.call("jawa/world_view", {"centerTile": 19337, "altitude": 900, "northUp": True})
    print("view:", json.dumps(v)[:200])
    s = rb.call("rimworld/take_screenshot", {})
    print("shot:", s.get("path") or s.get("filePath"))
