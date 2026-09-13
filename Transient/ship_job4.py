import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    c = rb.call("rimworld/list_colonists", {"currentMapOnly": True})
    for p in c.get("colonists", c.get("pawns", []))[:6]:
        print({k: p.get(k) for k in ("pawnId","id","name","nickname","fullName") if k in p})
    r = rb.call("jawa/ordered_job", {"pawnId": "Human922", "jobDef": "InspectGravEngine", "targetAId": "GravEngine466248", "timeoutSeconds": 5})
    print("full error:", str(r.get("message",""))[:400])
