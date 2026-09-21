import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r=rb.call("jawa/get_defs",{"defs":"ThingDef/RUT_PaleTree;ThingDef/Plant_TreeAnima","fields":"comps,statBases,thingClass","deep":True})
    for row in r.get("defs",[]):
        f=row["fields"]
        print("=====",row["defName"],"thingClass",f.get("thingClass"))
        for i in (0,1,7,8):
            print("  comp",i,json.dumps(f["comps"][i])[:400])
