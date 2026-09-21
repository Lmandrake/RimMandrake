import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    print(json.dumps(rb.call("jawa/get_defs",{"defs":"ThingDef/MeditationSpot;ThingDef/RUT_PaleMoss;ThingDef/Plant_TreeAnima","fields":"defName,label"}).get("defs"))[:400])
