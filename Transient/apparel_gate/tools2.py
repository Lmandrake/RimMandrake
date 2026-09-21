import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=60.0); S.connect()
ts = S.list_tools() or []
for t in ts:
    n = t.get("name","")
    if n in ("jawa/spawn_pawn","jawa/pawn_get","jawa/list_pawns","rimworld/start_debug_game_ready","jawa/harmony_patch_report"):
        print(n, json.dumps(t.get("inputSchema") or t.get("input_schema"))[:900])
        print()
print([t.get("name") for t in ts if "pawn_get" in t.get("name","") or "list_pawns" in t.get("name","") or "harmony" in t.get("name","")])
