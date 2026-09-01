import sys, json, io, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def npawns(rb):
    r = rb.call("jawa/list_pawns", {"faction":"hostile","limit":500})
    return r.get("count", len(r.get("pawns") or []))
def lords(rb):
    r = rb.call("jawa/lord_pawn_move", {"action":"list"})
    return r.get("count", len(r.get("lords") or []))
def clear(rb):
    return rb.call("jawa/destroy_bulk", {"filter":"nonColonists","dryRun":False})
INTEREST = ("MultiRaiders","SWCP","Rimesis","Isekai","group","Group","pawn","Pawn","raid","Raid","Faction","xeno","Xeno","Error","error","Exception")
out={}
with RimBridge(host, port, token) as rb:
    c=clear(rb); print("cleared:", json.dumps(c)[:200]); print("now hostiles", npawns(rb))
    for fac in ["Pirate","Empire","Jawa_HuttCartel"]:
        rb.call("jawa/drain_log", {"limit":500})
        before=npawns(rb); lb=lords(rb)
        r = rb.call("jawa/fire_raid", {"faction":fac,"points":3000,"strategy":"ImmediateAttack",
                                       "arrivalMode":"EdgeWalkIn","dryRun":False})
        time.sleep(1.5)
        after=npawns(rb); la=lords(rb)
        log = rb.call("jawa/drain_log", {"limit":400})
        msgs=[m.get("message") if isinstance(m,dict) else str(m) for m in (log.get("messages") or log.get("entries") or [])]
        out[fac]={"resp":r,"delta":after-before,"lordsBefore":lb,"lordsAfter":la,"log":msgs}
        print("== %-18s delta=%-4d lords %d->%d exec=%s subst=%s arrived=%s logN=%d"
              % (fac, after-before, lb, la, r.get("executed"),
                 (r.get("actual") or {}).get("substituted"), json.dumps(r.get("arrived"))[:70], len(msgs)))
        hits=[m for m in msgs if any(k in m for k in INTEREST)]
        for m in hits[-12:]: print("    LOG:", m[:190])
        clear(rb)
with io.open("fire2.json","w",encoding="utf-8") as fh: json.dump(out, fh, indent=1, ensure_ascii=False)
print("WROTE fire2.json")
