import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/list_things", {"rect": "160,110,50,40", "limit": 200, "defName": "PowerConduit"})
    things = r.get("things", [])
    print("countMatched=", r.get("countMatched"), "returned=", len(things))
    for t in things:
        print("  ", t.get("id"), t.get("x"), t.get("z"))
