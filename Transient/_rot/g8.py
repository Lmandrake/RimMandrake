import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r=rb.call("jawa/get_defs",{"defs":"ThingDef/RUT_PaleTree;ThingDef/Plant_TreeAnima","fields":"comps","deep":True})
    for row in r.get("defs",[]):
        print("=====", row["defName"])
        for c in row["fields"]["comps"]:
            if isinstance(c,dict) and ("subplant" in c or "requiredSubplantCountPerPsylinkLevel" in c):
                print(json.dumps(c))
