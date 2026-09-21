import sys, json, os
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/get_defs", {"defs":"GameConditionDef/RUT_SporeCloud;GameConditionDef/RUT_SheenExposureLock", "fields":""})
    print(json.dumps(r, indent=1)[:4000])
