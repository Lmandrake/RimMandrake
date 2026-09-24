import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    pawns = rb.call("jawa/list_pawns", {})
    for p in pawns.get("pawns", []):
        if p.get("defName") == "RSW_Korrum" or "Korrum" in (p.get("id") or ""):
            print("KORRUM_PAWN", json.dumps(p)[:1000])
    ci = rb.call("rimworld/get_cell_info", {"x": 230, "z": 230})
    print("CELL_230_230", json.dumps(ci.get("cell"))[:800])
