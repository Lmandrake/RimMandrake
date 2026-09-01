import sys, json, io
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
TYPES = ["PawnGroupMakerUtility","PawnGroupKindWorker_Normal","PawnGroupKindWorker","PawnGroupMaker",
         "IncidentWorker_RaidEnemy","IncidentWorker_Raid","PawnGenerator","PawnGenOption",
         "RaidStrategyWorker","Faction","StorytellerUtility"]
out = {}
with RimBridge(host, port, token) as rb:
    for t in TYPES:
        try:
            r = rb.call("jawa/harmony_patches", {"typeName": t})
        except Exception as e:
            r = {"error": str(e)}
        out[t] = r
with io.open("harmony_dump.json","w",encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
for t,r in out.items():
    ms = r.get("methods") or r.get("patchedMethods") or []
    print("==", t, "keys=", [k for k in r.keys() if k!="operation"], "n=", len(ms) if isinstance(ms,list) else ms)
