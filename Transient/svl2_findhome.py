import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    pawns = rb.call("jawa/list_pawns", {})
    for p in pawns.get("pawns", []):
        if p.get("faction") == "PlayerColony":
            print("PC", p.get("id"), p.get("defName"), p.get("x"), p.get("z"))
