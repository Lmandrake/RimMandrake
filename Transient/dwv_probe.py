import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for tool in ("jawa/spawn_pawn","jawa/pawn_traits","jawa/list_pawns"):
        try:
            rb.call(tool, {"zzz": 1})
        except Exception as e:
            print(tool, "->", str(e)[:400])
