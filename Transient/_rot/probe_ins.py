import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r=rb.call("jawa/inspect_string",{"defName":"Meat_Cow"})
    print(json.dumps({k:v for k,v in r.items() if k!="operation"}, indent=1)[:1800])
    r2=rb.call("jawa/inspect_string",{"defName":"RUT_GrownFurnace"})
    print(json.dumps({k:v for k,v in r2.items() if k!="operation"}, indent=1)[:900])
