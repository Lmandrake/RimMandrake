"""Read-only: the walk save's creatures and the things near the roof station's swirl (visit 9)."""
import json, os, sys
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 7))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h, p, t = resolve_endpoint()
with RimBridge(h, p, t) as rb:
    print(rb.call("rimworld/get_game_info", {}).get("ticksGame"))
    r = rb.call("jawa/list_pawns", {})
    ps = r.get("pawns") or []
    print(len(ps), r.get("count"), list(ps[0])[:30] if ps else r)
    for q in ps:
        k = str(q.get("kindDef") or q.get("def") or "")
        if "Ullai" in k or "Furnace" in k or "Ashwallow" in k:
            print(k, q.get("x"), q.get("z"), q.get("job"), q.get("downed"), q.get("dead"), q.get("position"))
    ex = rb.call("jawa/export_things", {"rect": "64,22,20,10", "includePawns": True, "includeItems": True, "limit": 100000})
    print(sorted({str(x.get("def")) for x in ex.get("things") or []}))
    ex = rb.call("jawa/export_things", {"rect": "110,20,20,16", "includePawns": True, "includeItems": True, "limit": 100000})
    print(sorted({str(x.get("def")) for x in ex.get("things") or []}))
