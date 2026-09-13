import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/inspect_string", {"thingIds": "ChemfuelTank466253,ChemfuelTank466254,GravEngine466248,PilotConsole469283,SmallThruster466249"})
    for row in r.get("things", r.get("results", [])):
        print("==", row.get("id"), "==")
        print(str(row.get("inspect") or row.get("text"))[:500])
        print()
