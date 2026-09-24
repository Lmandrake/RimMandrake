import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for dn in ["PowerConduit", "Battery", "SolarGenerator", "GravEngine"]:
        r = rb.call("jawa/list_things", {"rect": "160,110,60,60", "limit": 30, "defName": dn})
        things = r.get("things", [])
        print(dn, "countMatched=", r.get("countMatched"))
        for t in things[:5]:
            print("  ", t.get("id"), t.get("x"), t.get("z"))
