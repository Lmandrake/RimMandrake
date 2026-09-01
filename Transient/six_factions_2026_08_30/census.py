import sys, json, io, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def lords(rb): return rb.call("jawa/lord_pawn_move", {"action":"list"}).get("count",0)
rows=[]
with RimBridge(host, port, token) as rb:
    facs=[f for f in rb.call("jawa/list_factions",{"includeHidden":True}).get("factions",[]) if not f["isPlayer"]]
    rb.call("jawa/destroy_bulk", {"filter":"nonColonists","dryRun":False})
    for f in facs:
        fd=f["defName"]
        best=None
        for attempt in range(3):
            lb=lords(rb); t0=time.time()
            try:
                r=rb.call("jawa/fire_raid", {"faction":fd,"points":3000,"strategy":"ImmediateAttack",
                                             "arrivalMode":"EdgeWalkIn","dryRun":False})
            except Exception as e:
                best=("ERR",str(e)[:60],0); break
            dt=time.time()-t0; ld=lords(rb)-lb
            n=sum(a.get("pawnsArrived",0) for a in (r.get("arrived") or []))
            act=(r.get("actual") or {})
            rows.append({"fac":fd,"try":attempt,"lordDelta":ld,"pawns":n,"secs":round(dt,2),
                         "executed":r.get("executed"),"substituted":act.get("substituted"),"actualFac":act.get("faction")})
            rb.call("jawa/destroy_bulk", {"filter":"nonColonists","dryRun":False})
            if ld>0: break
        rr=[x for x in rows if x["fac"]==fd]
        ok=sum(1 for x in rr if x["lordDelta"]>0)
        print("%-24s hostile=%-5s  %d/%d ok  times=%s  subst=%s" %
              (fd, f["hostile"], ok, len(rr), [x["secs"] for x in rr], set(str(x["substituted"]) for x in rr)))
with io.open("census.json","w",encoding="utf-8") as fh: json.dump(rows,fh,indent=1)
