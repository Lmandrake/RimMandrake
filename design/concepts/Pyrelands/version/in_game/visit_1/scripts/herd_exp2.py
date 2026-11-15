import sys, json, math
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,tk = resolve_endpoint()
FB="RimMandrake.Pyrelands.RM_JobGiver_FollowBurn"
with RimBridge(h,p,tk) as rb:
    def rows():
        r = rb.call("jawa/site_state", {})
        return [(q.get("id")[-2:],q.get("x"),q.get("z"),q.get("job")) for q in (r.get("pawns") or []) if "Ullai" in str(q.get("id"))]
    print("before", rows())
    print("issue", rb.call("jawa/static_call", {"type":FB,"method":"ProbeHerd","args":"RM_Ullai|true"}).get("result"))
    print("after0", rows())
    rb.call("jawa/safe_advance", {"ticks":60,"timeException":False}); print("after60", rows())
    rb.call("jawa/safe_advance", {"ticks":1000,"timeException":False}); print("after1060", rows())
