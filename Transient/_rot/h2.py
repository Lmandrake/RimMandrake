import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rb.call("jawa/set_game_speed",{"speed":"Ultrafast"})
import time; time.sleep(4)
with RimBridge(host, port, token) as rb:
    rb.call("jawa/set_game_speed",{"speed":"Paused"})
    g=rb.call("jawa/list_things",{"defName":"RUT_ChokingSpores","limit":200})
    print("choking spores:", len(g.get("things",[])), g.get("message")[:90] if g.get("message") else "")
    print("cells:", [(t["x"],t["z"]) for t in g.get("things",[])][:12])
