import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/spawn_pawn", {"kindDef": "Jawa_Homestead_Grunt", "count": 2, "x": 60, "z": 40, "faction": "none"})
    print("requested Jawa_Homestead_Grunt x2:", str(r)[:250])
    ps = rb.call("jawa/list_pawns", {})
    recent = [p for p in ps.get("pawns", []) if p.get("x",0) in range(38,66) and p.get("z",0) in range(36,44)]
    for p in recent:
        print(p.get("id"), "| kind:", p.get("kind"), "| faction:", p.get("faction"))
    rb.call("rimworld/save_game", {"saveName": "qt_flavor_probe"})
