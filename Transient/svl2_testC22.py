import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for pid in ["Thing_Human692541", "692541", "Yegor"]:
        r5 = rb.call("jawa/ordered_job", {
            "jobDef": "EnterBuilding",
            "pawnId": pid,
            "targetAId": "RSW_BactaTank692523",
        })
        print(pid, "->", json.dumps(r5)[:400])
