import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/get_defs", {"defs":"ThingDef/RUT_PaleTree", "fields":"comps", "deep":True})
    print(json.dumps(r, indent=1)[:6000])
