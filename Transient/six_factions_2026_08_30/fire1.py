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
    ps = rb.call("jawa/list_pawns", {"faction":"hostile","limit":500}).get("pawns") or []
    ids = [p.get("id") or p.get("thingId") for p in ps]
    if ids:
        rb.call("jawa/destroy_batch", {"thingIds": ",".join(ids)})
    return len(ids)

out={}
with RimBridge(host, port, token) as rb:
    print("ticks", rb.call("rimworld/get_game_info",{})["ticksGame"])
    n=clear(rb); print("cleared", n, "hostiles; now", npawns(rb), "lords", lords(rb))
    rb.call("jawa/drain_log", {"limit":500})   # flush
    for fac in ["Empire","Pirate"]:
        before=npawns(rb); lb=lords(rb)
        r = rb.call("jawa/fire_raid", {"faction":fac,"points":3000,"strategy":"ImmediateAttack",
                                       "arrivalMode":"EdgeWalkIn","dryRun":False})
        time.sleep(1.5)
        after=npawns(rb); la=lords(rb)
        log = rb.call("jawa/drain_log", {"limit":400})
        msgs=[m.get("message") if isinstance(m,dict) else str(m) for m in (log.get("messages") or log.get("entries") or [])]
        out[fac]={"resp":r,"before":before,"after":after,"delta":after-before,"lordsBefore":lb,"lordsAfter":la,"log":msgs}
        print("== %-8s delta=%-4d lords %d->%d executed=%s subst=%s actual=%s arrived=%s logN=%d"
              % (fac, after-before, lb, la, r.get("executed"), r.get("substituted"),
                 json.dumps(r.get("actual"))[:80], r.get("arrived"), len(msgs)))
        clear(rb)
with io.open("fire1.json","w",encoding="utf-8") as fh: json.dump(out, fh, indent=1, ensure_ascii=False)
print("WROTE fire1.json")
