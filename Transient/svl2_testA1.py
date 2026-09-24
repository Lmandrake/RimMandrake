import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    td = rb.call("jawa/get_defs", {"defs": "ThingDef/RSW_Korrum"})
    print("THINGDEF", json.dumps(td)[:2000])
    pk = rb.call("jawa/get_defs", {"defs": "PawnKindDef/RSW_Korrum"})
    print("PAWNKINDDEF", json.dumps(pk)[:2000])
