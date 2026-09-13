import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def fresh(): return RimBridge(host, port, token)
with fresh() as rb:
    for pid in ("Brandy", "Thing_Human922"):
        r = rb.call("jawa/ordered_job", {"pawnId": pid, "jobDef": "InspectGravEngine", "targetAId": "GravEngine466248", "timeoutSeconds": 5})
        print(pid, "->", r.get("success"), str(r.get("message",""))[:90])
        if r.get("success"): break
