"""Quick health check + confirm ticks have advanced enough for CompTickRare to have fired."""
import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

with RimBridge(host, port, token) as rb:
    st = rb.call("rimbridge/get_bridge_status")
    print("status:", json.dumps(st)[:400])
    lp = rb.call("jawa/list_pawns", {})
    mine = [p for p in lp["pawns"] if p["kind"] in ("RSW_Cindermare", "RSW_Skarnix")]
    print("still", len(mine), "of our pawns alive")
