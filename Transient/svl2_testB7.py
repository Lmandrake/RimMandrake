import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/inhabited_settlement_create", {"tile": 16905, "manifest": "Inhabited_Manifest_TheClaimJump"})
    print("REENTER_CALL", json.dumps(r)[:2000])
