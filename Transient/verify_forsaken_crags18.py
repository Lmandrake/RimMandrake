"""Check needs on RSW_Skarnix24320 now, and try inspect_string differently."""
import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

with RimBridge(host, port, token) as rb:
    pg = rb.call("jawa/pawn_get", {"pawn": "RSW_Skarnix24320"})
    print("pawn_get:", json.dumps(pg)[:1200])

    try:
        insp = rb.call("jawa/inspect_string", {"thingIds": "RSW_Skarnix24320"})
        print("inspect_string(str):", json.dumps(insp)[:1500])
    except Exception as e:
        print("inspect_string(str) EXC", e)
