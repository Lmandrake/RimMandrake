import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    # find a hostile faction defName from the world's factions
    tools = rb.list_tools()
    fac_tools = [t["name"] for t in tools if "faction" in t["name"]]
    print("faction tools:", fac_tools)
    # spawn the target pawn via debug action at 233,32
    r = rb.call("rimworld/execute_debug_action",
                {"path": "Actions\\Spawn Pawn...\\Megascarab", "x": 233, "z": 32})
    print("spawn pawn:", str(r)[:180])
    # who is at 233,32? list pawns and find the scarab
    ps = rb.call("jawa/list_pawns", {})
    scar = [p for p in ps.get("pawns", []) if "egascarab" in str(p.get("kind") or p.get("kindDef") or p.get("defName"))]
    print("scarabs:", str(scar)[:300])
