import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rbc
host, port, token = rbc.resolve_endpoint()
with rbc.RimBridge(host, port, token, timeout=120.0) as rb:
    for a in sys.argv[1:]:
        r = rb.call("rimworld/execute_debug_action", {"path": "Actions\\" + a}, check=False)
        print(a, r.get("success"), str(r.get("message") or r)[:150])
