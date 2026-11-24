"""python.exe: visit 8. Reload the full-list site; list a colonist's needs, the pawns within 30 cells, the nearest water."""
import json, os, sys
sys.path.insert(0, r"src\RimMandrake\Utils")
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 7))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Pyrelands"))
import northstar_site as NS  # noqa: E402
from northstar_driver.session import FastSession  # noqa: E402
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402
with FastSession(strict=False) as s:
    NS.reload_fixture(s, os.environ.get("PEEK_SAVE", "NS_Pyrelands_site_1_417df172fdb5_visit8full"), int(os.environ.get("PEEK_TILE", "193")), map_id=1)
h, p, tk = resolve_endpoint()
with RimBridge(h, p, tk) as rb:
    c = lambda tool, **kw: rb.call(tool, kw)  # noqa: E731
    pawns = c("jawa/list_pawns", limit=1000, includeHealth=True).get("pawns") or []
    for q in pawns:
        if q.get("intelligence") == "Humanlike" and q.get("isPlayer"):
            print(q["id"], q.get("x"), q.get("z"), json.dumps([(n["need"], round(n["level"], 2)) for n in c("jawa/pawn_need", pawn=q["id"], action="list").get("needs") or []]))
            print("   ", json.dumps(q.get("hediffs"))[:300])
    import collections
    print(collections.Counter((q.get("kindDef"), q.get("faction")) for q in pawns).most_common(40))
    cells = {}
    for op in str(c("jawa/get_terrain_batch", rects="0,0,250,250").get("ops") or "").split(";"):
        d, _, rr = op.partition(":")
        if rr:
            ox, oz, ow, oh = (int(v) for v in rr.split(","))
            cells.setdefault(d, 0); cells[d] += ow * oh
    print(sorted(cells.items(), key=lambda kv: -kv[1])[:25])
