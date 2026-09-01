import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    t0 = rb.call("rimworld/get_game_info", {}).get("ticksGame")
    r = rb.call("rimworld/step_game_ticks", {"ticks": 400})
    t1 = rb.call("rimworld/get_game_info", {}).get("ticksGame")
    print("ticks:", t0, "->", t1)
    ps = rb.call("jawa/list_pawns", {})
    scar = [p for p in ps.get("pawns", []) if "egascarab" in str(p.get("kind"))]
    print("scarab now:", str(scar)[:250] if scar else "GONE (dead/destroyed)")
    rb.call("jawa/clear_ui", {})
    rb.call("rimworld/jump_camera_to_cell", {"x": 233, "z": 26})
    s = rb.call("rimworld/take_screenshot", {})
    print("shot:", s.get("path"))
