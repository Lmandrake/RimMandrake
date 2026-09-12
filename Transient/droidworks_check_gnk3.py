import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    g = rb.call("jawa/pawn_get", {"pawn": "RSW_DW_Race_OuterRim_GNKDroid16918"})
    p = g["pawns"][0]
    print("keys:", list(p.keys()))
    print("hediffs:", json.dumps(p.get("hediffs"))[:1500])
