import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rbc
host, port, token = rbc.resolve_endpoint()
with rbc.RimBridge(host, port, token, timeout=60.0) as rb:
    r = rb.call("jawa/pawn_thoughts", {"pawn": "Human163813"}, check=False)
    s = json.dumps(r); print(s.count("ReadMercyCarving"), s[:700])
    c = rb.call("jawa/inspect_string", {"thingIds": "RM_MercyCarving154707"}, check=False)
    print(json.dumps(c)[:400])
