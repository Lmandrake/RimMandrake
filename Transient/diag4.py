import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/inspect_string", {"thingIds": "BigLaserCannon22478,VanometricPowerCell22477"})
    if r.get("success"):
        for t in r.get("things", []) or [r]:
            print("----", str(t)[:500])
    else:
        print(str(r)[:300])
