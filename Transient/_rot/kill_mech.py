import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for i in ["Mech_Scyther37426","Mech_Scyther37427","Mech_Scyther37428"]:
        for _ in range(6):
            rb.call("jawa/damage",{"thingId":i,"damageDef":"Bomb","amount":200})
    ps={p["id"]:p for p in rb.call("jawa/list_pawns",{"limit":500}).get("pawns",[])}
    print("remaining mechs:", [i for i in ["Mech_Scyther37426","Mech_Scyther37427","Mech_Scyther37428"] if i in ps])
