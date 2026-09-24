import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    info = rb.call("rimworld/get_game_info", {})
    print("AFTER_LEAVE", json.dumps(info)[:600])
    # re-enter to check casing persistence
    r = rb.call("jawa/inhabited_settlement_create", {"tile": 16905, "manifest": "Inhabited_Manifest_TheClaimJump"})
    print("SECOND_VISIT", json.dumps(r)[:2000])
