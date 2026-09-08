import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ui=rb.call("rimworld/get_ui_state", {})
    print("programState:", ui.get("programState"), "hasCurrentGame:", ui.get("hasCurrentGame"))
    if ui.get("programState")=="Playing":
        gi=rb.call("rimworld/get_game_info", {}); print("ticksGame:", gi.get("ticksGame"), "mapCount:", gi.get("mapCount"))
        rb.call("jawa/clear_ui", {}); rb.call("rimworld/close_window", {"windowType":"LudeonTK.EditWindow_Log"})
        rb.call("jawa/world_view", {"centerTile": 0, "altitude": 800})
        s=rb.call("rimworld/take_screenshot", {}); print("orbit shot:", s.get("path"))
