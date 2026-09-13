import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for tid in ("ChemfuelTank466253", "ChemfuelTank466254", "GravEngine466248", "PilotConsole469283"):
        r = rb.call("jawa/inspect_string", {"thingId": tid})
        print("==", tid, "==")
        print(str(r.get("inspect") or r.get("text") or r)[:400])
