import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimdrive import Session
with Session(lock=None) as s:
    mi = s.call("jawa/map_info"); sx, sz = mi.get("sizeX"), mi.get("sizeZ"); print("map", sx, sz)
    x, z = 20, 20
    def pawns():
        return (s.call("jawa/list_pawns", limit=500, includeHealth=True, includeCorpses=True) or {}).get("pawns") or []
    before = {p["id"] for p in pawns()}
    r = s.call("jawa/spawn_pawn", kindDef="Rat", x=x, z=z, faction="none", count=1)
    t = (r.get("pawns") or r.get("spawned") or [None])[0]; print("spawn T", json.dumps(r)[:300])
    r2 = s.call("jawa/spawn_pawn", kindDef="Rat", x=x+2, z=z, faction="none", count=1)
    n = (r2.get("pawns") or r2.get("spawned") or [None])[0]; print("spawn N", json.dumps(r2)[:200])
    tid = t["id"]; nid = n["id"]; tpos = t.get("position") or {}
    print("tpos", tpos)
    fires0 = (s.call("jawa/list_things", defName="Fire", limit=50) or {}).get("countMatched")
    s.track("pawn", tid, tpos.get("x", x), tpos.get("z", z))
    res = s.sweep(); print("sweep", json.dumps(res)[:300])
    ps = pawns(); ids = {p["id"]: p for p in ps}
    print("T present as pawn after sweep:", tid in ids)
    print("N alive:", nid in ids, "N health:", json.dumps(ids.get(nid, {}).get("health") or ids.get(nid, {}).get("hediffs"))[:200])
    fires1 = (s.call("jawa/list_things", defName="Fire", limit=50) or {}).get("countMatched")
    print("fires before/after", fires0, fires1)
    cor = s.call("jawa/list_things", group="Corpse", rect="%d,%d,5,5" % (x-2, z-2), limit=20)
    print("corpses near:", cor.get("countMatched"))
    # cleanup neighbour
    s.track("pawn", nid, (n.get("position") or {}).get("x"), (n.get("position") or {}).get("z")); print("cleanup", json.dumps(s.sweep())[:200])
