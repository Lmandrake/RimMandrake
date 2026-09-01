import sys, json, io, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def lords(rb): return rb.call("jawa/lord_pawn_move", {"action":"list"}).get("count",0)
def clear(rb): rb.call("jawa/destroy_bulk", {"filter":"nonColonists","dryRun":False})
def grab(rb, sub, lim=60):
    r = rb.call("jawa/drain_log", {"limit":lim, "contains":sub})
    raw = r.get("messages") or r.get("entries") or []
    return [ (m.get("message") if isinstance(m,dict) else str(m)) or "" for m in raw ], r.get("totalInBuffer")
with RimBridge(host, port, token) as rb:
    clear(rb)
    for fac in ["Pirate","Empire","Pirate"]:
        pre,_  = grab(rb,"Hostile group incoming")
        prep,_ = grab(rb,"Processed")
        lb = lords(rb)
        r = rb.call("jawa/fire_raid", {"faction":fac,"points":3000,"strategy":"ImmediateAttack",
                                       "arrivalMode":"EdgeWalkIn","dryRun":False})
        time.sleep(2.0)
        la = lords(rb)
        post,tb  = grab(rb,"Hostile group incoming")
        postp,_  = grab(rb,"Processed")
        print("=== fire at %-8s  lords %d->%d  arrived=%s" % (fac, lb, la, json.dumps(r.get("arrived"))[:60]))
        print("    'Hostile group incoming' lines: %d -> %d   (buffer %s)" % (len(pre), len(post), tb))
        for m in post[len(pre):] if len(post)>len(pre) else post[-3:]:
            print("      NEW>", m[:170])
        print("    'Processed' lines: %d -> %d" % (len(prep), len(postp)))
        for m in postp[len(prep):] if len(postp)>len(prep) else postp[-2:]:
            print("      NEW>", m[:170])
        clear(rb)
