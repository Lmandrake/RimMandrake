import sys, json, io, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def npawns(rb):
    return rb.call("jawa/list_pawns", {"faction":"hostile","limit":500}).get("count",0)
def lords(rb):
    return rb.call("jawa/lord_pawn_move", {"action":"list"}).get("count",0)
def clear(rb):
    rb.call("jawa/destroy_bulk", {"filter":"nonColonists","dryRun":False})
def drain(rb):
    log = rb.call("jawa/drain_log", {"limit":500})
    raw = log.get("messages") or log.get("entries") or []
    o=[]
    for m in raw:
        if isinstance(m,dict):
            o.append("[%s] %s" % (m.get("type") or m.get("level") or "?", m.get("message") or m.get("text") or json.dumps(m)))
        else: o.append(str(m))
    return o, log
out={}
with RimBridge(host, port, token) as rb:
    clear(rb)
    for fac in ["Pirate","Empire"]:
        drain(rb)
        before=npawns(rb); lb=lords(rb)
        r = rb.call("jawa/fire_raid", {"faction":fac,"points":3000,"strategy":"ImmediateAttack",
                                       "arrivalMode":"EdgeWalkIn","dryRun":False})
        time.sleep(2.0)
        after=npawns(rb); la=lords(rb)
        msgs, rawlog = drain(rb)
        out[fac]={"resp":r,"delta":after-before,"lords":[lb,la],"log":msgs,"logMeta":{k:v for k,v in rawlog.items() if k not in ("messages","entries","operation")}}
        print("== %-16s delta=%-4d lords %d->%d exec=%s arrived=%s logN=%d"
              % (fac, after-before, lb, la, r.get("executed"), json.dumps(r.get("arrived"))[:60], len(msgs)))
        clear(rb)
with io.open("fire3.json","w",encoding="utf-8") as fh: json.dump(out, fh, indent=1, ensure_ascii=False)
print("WROTE fire3.json")
print("LOGMETA", json.dumps(out["Pirate"]["logMeta"])[:300])
