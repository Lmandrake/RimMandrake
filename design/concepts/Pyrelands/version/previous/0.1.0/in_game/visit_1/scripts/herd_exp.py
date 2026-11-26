import sys, json, math
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,tk = resolve_endpoint()
FB="RimMandrake.Pyrelands.RM_JobGiver_FollowBurn"; BL="RimMandrake.Pyrelands.MapComponent_BurnLine"
A=(30,100)
with RimBridge(h,p,tk) as rb:
    print("hist", rb.call("jawa/static_call", {"type":BL,"method":"ProbeBurnHistory","args":str(120000)}).get("result"))
    ids=[]
    for i in range(10):
        r = rb.call("jawa/spawn_pawn", {"kindDef":"RM_Ullai","x":125+(i%5)-2,"z":215+(i//5)*2-1,"faction":"none","count":1})
        ids.append(((r.get("pawns") or [{}])[0]).get("id"))
    print("ids", ids)
    def herd(issue): return rb.call("jawa/static_call", {"type":FB,"method":"ProbeHerd","args":"RM_Ullai|%s"%issue}).get("result")
    def rows():
        r = rb.call("jawa/site_state", {})
        return [(q.get("x"),q.get("z"),q.get("job")) for q in (r.get("pawns") or []) if q.get("id") in ids]
    print("issue", herd("true"))
    for i in range(6):
        rr = rows(); print(i*2500, rr[:4])
        r = rb.call("jawa/safe_advance", {"ticks":2500,"timeException":False})
        hh = herd("false"); print("   ", hh, r.get("state"))
        try:
            kv=dict(x.split("=",1) for x in hh.split(";")); print("    distA", round(math.hypot(float(kv["cx"])-A[0], float(kv["cz"])-A[1]),1))
        except Exception as e: print(e)
