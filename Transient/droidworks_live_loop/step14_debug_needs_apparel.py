import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    g = rb.call("jawa/pawn_get", {"pawn": "RSW_DW_Race_guy762_DroidRace_ADMkI53446"})
    p = g.get("pawns", [{}])[0]
    print("needs raw:", json.dumps(p.get("needs"), default=str))
    print()
    g2 = rb.call("jawa/pawn_get", {"pawn": "RSW_DW_Race_guy762_DroidRace_KM1HMD53443"})
    p2 = g2.get("pawns", [{}])[0]
    print("apparel raw:", json.dumps(p2.get("apparel"), default=str))
    print("equipment raw:", json.dumps(p2.get("equipment"), default=str))
    print()
    # check gear via jawa/pawn_gear (companion) rather than pawn_get, if it differs
    r = rb.call("jawa/pawn_gear", {"pawn": "RSW_DW_Race_guy762_DroidRace_KM1HMD53443", "action": "list"})
    print("pawn_gear list:", json.dumps(r, default=str)[:2000])
