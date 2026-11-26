"""python.exe, on the loaded walk save: where every RM_FurnaceBeast, RM_Ullai and RM_Ashwallow stands (alive or dead), and
the creatures station's rect (80,20,20,16). Visit 6: the close-up showed no furnace-beast at its spawn cell (88,30)."""
import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h, p, tk = resolve_endpoint()
with RimBridge(h, p, tk) as rb:
    r = rb.call("jawa/list_pawns", {"includeCorpses": True, "limit": 2000})
    rows = [x for x in r.get("pawns") or [] if x.get("kindDef") in ("RM_FurnaceBeast", "RM_Ullai", "RM_Ashwallow")]
    for x in rows:
        print(json.dumps({k: x.get(k) for k in ("id", "kindDef", "x", "z", "dead", "downed", "faction")}))
    print("in station rect (80..99, 20..35):", [x.get("id") for x in rows if x.get("x") is not None and 80 <= x["x"] < 100 and 20 <= x["z"] < 36])
