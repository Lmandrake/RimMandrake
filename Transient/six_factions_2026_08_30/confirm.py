import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def lords(rb): return rb.call("jawa/lord_pawn_move", {"action":"list"}).get("count",0)
with RimBridge(host, port, token) as rb:
    rb.call("jawa/destroy_bulk", {"filter":"nonColonists","dryRun":False})
    # 1. explicit executed/0-pawn confirmation
    lb=lords(rb); t0=time.time()
    r=rb.call("jawa/fire_raid", {"faction":"Pirate","points":3000,"strategy":"ImmediateAttack",
                                 "arrivalMode":"EdgeWalkIn","dryRun":False})
    dt=time.time()-t0
    print("PIRATE executed=%s arrived=%s lordDelta=%d  %.2fs" % (r.get("executed"), r.get("arrived"), lords(rb)-lb, dt))
    # 2. world objects: are there any outposts?
    wo = rb.call("jawa/world_objects_get", {})
    objs = wo.get("objects") or []
    from collections import Counter
    c=Counter((o.get("def") or o.get("defName") or "?") for o in objs)
    print("WORLD OBJECT DEFS:", dict(c))
    print("  outpost-ish:", [k for k in c if "utpost" in k or "VOE" in k])
    # 3. Isekai/protection/outpost log needles
    for n in ["Protection","protection","fee","Fee","Outpost","outpost","Intercept","intercept"]:
        rows=[m.get("text","") for m in (rb.call("jawa/drain_log",{"limit":20,"contains":n}).get("messages") or [])]
        if rows: print("LOG[%s] n=%d :: %s" % (n, len(rows), rows[-1][:150]))
