import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
D=["ThingDef/Meat_Cow","ThingDef/Meat_Human","ThingDef/RUT_Glimmerslime","ThingDef/RUT_RawDulcis","TerrainDef/Concrete","ThingDef/Steel","ThingDef/Wall","ThingDef/Door"]
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/get_defs", {"defs":";".join(D), "fields":"defName,stackLimit,label,modExtensions,passability"})
    for row in r.get("defs", []):
        print(row.get("found"), row.get("requested"), "|", row.get("label"), "|", json.dumps(row.get("fields")))
