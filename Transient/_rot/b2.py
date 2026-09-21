import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    print("MAPINFO", json.dumps(rb.call("jawa/map_info", {}))[:1500])
    print()
    print("PAWNS", json.dumps(rb.call("jawa/list_pawns", {"faction":"player"}))[:1200])
