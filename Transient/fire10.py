import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("rimworld/execute_debug_action", {"path": "Actions\\Spawn Pawn...\\Megascarab", "x": 230, "z": 41})
    rb.call("rimworld/step_game_ticks", {"ticks": 500})
    ps = rb.call("jawa/list_pawns", {})
    scars = [p for p in ps.get("pawns", []) if "egascarab" in str(p.get("kind"))]
    for s in scars:
        print("scarab", s.get("id"), "at", s.get("x"), s.get("z"), "downed:", s.get("downed"), "dead:", s.get("dead"))
    if len(scars) < 2:
        print("=> one scarab GONE — the slug killed it")
