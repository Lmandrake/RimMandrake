import sys, json
from collections import Counter
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    e = rb.call("rimworld/get_cell_info", {"x": 187, "z": 150})
    print("engine cell:", [(t.get("defName"), t.get("factionName")) for t in e.get("things", [])])
    # census things in footprint by def (key organs)
    r = rb.call("jawa/list_things", {"rect": "143,59,86,133", "limit": 5000}) if False else None
