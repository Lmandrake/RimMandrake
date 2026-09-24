import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    try:
        rb.call("jawa/power_net", {"__bogus__": 1})
    except Exception as e:
        print("PARAMS", e)
    r = rb.call("jawa/power_net", {"thing": "RSW_BactaTank692523", "forcePowerOn": True})
    print("POWER_NET", json.dumps(r)[:2000])
