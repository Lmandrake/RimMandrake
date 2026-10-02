import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    info = rb.call("rimworld/get_game_info", {})
    print("status:", info.get("status"))
    ui = rb.call("rimworld/get_ui_state", {})
    print("paused:", ui.get("paused"), "timeSpeed:", ui.get("timeSpeed"), "mapCount:", ui.get("mapCount"))
    pawns = rb.call("jawa/list_pawns", {})
    print("pawn count:", len(pawns.get("pawns", pawns) if isinstance(pawns, dict) else pawns))
