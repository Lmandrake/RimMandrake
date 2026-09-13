import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def probe(rb, tool):
    try: rb.call(tool, {"zzz": 1})
    except Exception as e: return str(e).split("Declared:")[-1].strip()
with RimBridge(host, port, token) as rb:
    for t in ("jawa/spawn_pawn","jawa/set_pawn_identity","jawa/set_pawn_skill","jawa/pawn_traits","jawa/set_pawn_age"):
        print(t, "->", probe(rb, t))
