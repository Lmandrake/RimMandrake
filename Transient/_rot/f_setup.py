import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for p in ["Human36838","Human36841","Human36844"]:
        r=rb.call("jawa/pawn_severity_adjust",{"pawn":p,"hediff":"RUT_SheenCoating","offset":1.0})
        print("sev",p,r.get("success"),json.dumps({k:v for k,v in r.items() if k!="operation"})[:220])
    r=rb.call("jawa/game_condition",{"action":"start","condition":"RUT_SporeCloud","permanent":True})
    print("sporecloud:", json.dumps({k:v for k,v in r.items() if k!="operation"})[:400])
