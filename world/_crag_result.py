import sys, json, collections
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ln=rb.call("jawa/world_lint", {}); print("lint:", ln.get("findingCount", ln.get("findings")))
    lm=rb.call("jawa/world_landmarks_get", {"limit":4000})
    print("total landmarks now:", lm.get("count"))
    rb.call("jawa/clear_ui", {}); rb.call("rimworld/close_window", {"windowType":"LudeonTK.EditWindow_Log"})
    rb.call("jawa/world_view", {"centerTile": 9023, "altitude": 190})
    s=rb.call("rimworld/take_screenshot", {}); print("shot:", s.get("path"))
