import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for t in rb.list_tools():
        if t["name"] in ("jawa/fire_raid","jawa/drain_log","jawa/list_pawns","jawa/lord_pawn_move","jawa/pawnkind_audit"):
            sch=t.get("inputSchema") or {}
            print("###",t["name"]); print(" props:", json.dumps(sch.get("properties",{}))[:1200])
