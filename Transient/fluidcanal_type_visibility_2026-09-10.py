import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=30.0) as rb:
    r = rb.call("jawa/type_visibility", {"typeName": "RimMandrake.FluidCanals.FluidCanalsDebugActions"})
    print(json.dumps(r, indent=2)[:3000])
