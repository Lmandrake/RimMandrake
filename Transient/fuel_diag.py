import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    # is chemfuel forbidden? check inspect
    f = rb.call("jawa/list_things", {"defName": "Chemfuel", "rect": "143,59,86,133", "limit": 4}).get("things", [])
    print("chemfuel:", [(t["id"], t["x"], t["z"], t.get("forbidden")) for t in f])
    # can a colonist even do the job? try a plain haul (proved workable before)
    j = rb.call("jawa/ordered_job", {"pawnId": "Human470527", "jobDef": "Refuel", "targetAId": "ChemfuelTank483473", "targetBId": f[0]["id"], "count": 75, "timeoutSeconds": 8})
    print("refuel full:", json.dumps(j)[:600])
