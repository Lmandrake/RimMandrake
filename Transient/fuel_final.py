import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/inspect_string", {"thingIds": "GravEngine466248,PilotConsole469283"})
    for row in r.get("things", r.get("results", [])):
        print(row.get("id"), str(row.get("inspect") or row.get("text"))[:220], "\n")
    d = rb.call("jawa/get_defs", {"defs": "JobDef/Refuel;JobDef/RefuelAtomic;JobDef/VGE_Refuel"})
    for row in d.get("defs", []):
        print(row.get("request") or row.get("defName"), "found:", row.get("found"))
