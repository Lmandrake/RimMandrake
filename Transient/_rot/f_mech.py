import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r=rb.call("jawa/spawn_pawn",{"kindDef":"Mech_Scyther","x":230,"z":230,"faction":"none","count":3})
    print("mech:", r.get("success"), r.get("message"), [p.get("id") for p in (r.get("pawns") or [])])
    r2=rb.call("jawa/spawn_pawn",{"kindDef":"Muffalo","x":225,"z":230,"faction":"none","count":3})
    print("animal:", r2.get("success"), r2.get("message"), [p.get("id") for p in (r2.get("pawns") or [])])
