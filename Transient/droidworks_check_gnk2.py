import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    g = rb.call("jawa/pawn_get", {"pawn": "RSW_DW_Race_OuterRim_GNKDroid16918"})
    print(json.dumps(g)[:2000])
