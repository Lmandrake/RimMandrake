import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for shape in ("220,10,242,40", ["220,10,242,40"]):
        try:
            r = rb.call("jawa/destroy_batch", {"rects": shape, "categories": "Plant"})
            print("destroy", type(shape).__name__, ":", str(r)[:160]); break
        except Exception as e:
            print("ERR", type(shape).__name__, str(e)[:100])
    rb.call("rimworld/step_game_ticks", {"ticks": 600})
    ps = rb.call("jawa/list_pawns", {})
    scar = [p for p in ps.get("pawns", []) if "egascarab" in str(p.get("kind"))]
    print("scarab:", "ALIVE downed=%s" % scar[0].get("downed") if scar else "GONE - killed")
