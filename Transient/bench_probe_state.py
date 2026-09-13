import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ui = rb.call("rimworld/get_ui_state", {})
    print("programState:", ui.get("programState"), "| hasCurrentGame:", ui.get("hasCurrentGame"))
    wins = ui.get("windows") or []
    print("windows:", [w if isinstance(w,str) else w.get("type") for w in wins][:6])
    try:
        gi = rb.call("rimworld/get_game_info", {})
        print("colony:", gi.get("colonyName"), "| ticks:", gi.get("ticksGame"), "| storyteller:", gi.get("storyteller"))
    except Exception as e:
        print("get_game_info threw:", e)
