import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for dn in ["Corpse_Human", "Human"]:
        r = rb.call("jawa/list_things", {"rect": "0,0,250,250", "limit": 30, "defName": dn})
        print(dn, "countMatched=", r.get("countMatched"))
        for t in r.get("things", []):
            print("  ", t.get("id"), t.get("x"), t.get("z"))
