import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
ALL="Human36838 Human36841 Human36844 Human36847 Human36850 Human36853 Human36856 Human36859 Human36862 Human36865 Human36868 Human36871".split()
with RimBridge(host, port, token) as rb:
    for p in ALL:
        rb.call("jawa/pawn_health",{"pawn":p,"action":"remove","hediff":"RUT_SheenCoating"})
    print("cleared")
