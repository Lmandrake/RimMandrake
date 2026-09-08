import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
def brief(x,n=400): return json.dumps(x)[:n]
with RimBridge(h,p,t) as rb:
    r = rb.call("jawa/spawn_pawn", {"kindDef":"Colonist","x":125,"z":125,"faction":"player","count":1})
    print("spawn_pawn:", brief(r)); print()
    for m in ("jawa/list_things","rimworld/get_game_info"):
        try:
            a = {"category":"Pawn"} if "list_things" in m else {}
            print(m, "->", brief(rb.call(m, a), 500)); print()
        except Exception as e:
            print(m, "!!", type(e).__name__, str(e)[:200]); print()
