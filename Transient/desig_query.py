import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for cell in ("149,148,2,2", "149,151,2,2"):
        x,z,w,h = map(int, cell.split(","))
        d = rb.call("jawa/designate_batch", {"action": "query", "rect": f"{x},{z},{w},{h}"})
        print(cell, "->", json.dumps(d)[:250])
