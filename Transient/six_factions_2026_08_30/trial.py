import sys, json, io, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def lords(rb): return rb.call("jawa/lord_pawn_move", {"action":"list"}).get("count",0)
rows=[]
with RimBridge(host, port, token) as rb:
    rb.call("jawa/destroy_bulk", {"filter":"nonColonists","dryRun":False})
    for rep in range(10):
        for fac in ["Pirate","Empire","Jawa_HuttCartel"]:
            lb=lords(rb)
            t0=time.time()
            try:
                r = rb.call("jawa/fire_raid", {"faction":fac,"points":3000,"strategy":"ImmediateAttack",
                                               "arrivalMode":"EdgeWalkIn","dryRun":False})
            except Exception as e:
                rows.append({"rep":rep,"fac":fac,"err":str(e)}); print("ERR",fac,e); continue
            dt=time.time()-t0
            la=lords(rb)
            arr=r.get("arrived") or []
            n=sum(a.get("pawnsArrived",0) for a in arr)
            rows.append({"rep":rep,"fac":fac,"lordDelta":la-lb,"pawns":n,"secs":round(dt,2),
                         "resolved":r.get("resolved"),"substituted":(r.get("actual") or {}).get("substituted")})
            print("rep%-2d %-18s lordDelta=%+d pawns=%-3d %.1fs" % (rep,fac,la-lb,n,dt))
            rb.call("jawa/destroy_bulk", {"filter":"nonColonists","dryRun":False})
with io.open("trial.json","w",encoding="utf-8") as fh: json.dump(rows,fh,indent=1)
from collections import defaultdict
agg=defaultdict(lambda:[0,0,0])
for r in rows:
    if "err" in r: continue
    a=agg[r["fac"]]; a[0]+=1; a[1]+= (1 if r["lordDelta"]>0 else 0); a[2]+=r["pawns"]
print("\n=== SUMMARY (successes / firings, total pawns) ===")
for f,(n,s,p) in agg.items(): print("  %-18s %d/%d  pawns=%d" % (f,s,n,p))
