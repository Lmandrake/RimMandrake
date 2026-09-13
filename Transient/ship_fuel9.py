import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    d = rb.call("jawa/get_defs", {"defs": "ThingDef/Astrofuel;ThingDef/VGE_Astrofuel;ThingDef/Chemfuel"})
    for row in d.get("defs", []):
        print(row.get("request"), "found:", row.get("found"), row.get("label"))
    pawns = rb.call("jawa/list_pawns", {"currentMapOnly": True})
    cols = [p for p in pawns.get("pawns", []) if p.get("faction") == "PlayerColony" or p.get("isColonist")]
    print("colonists:", [(p.get("id"), p.get("name")) for p in cols][:6])
