import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    r = rb.call("jawa/list_pawns", {})
    pawns = r.get("pawns", [])
    animals = [pw for pw in pawns if pw.get("kind") not in ("Colonist",) and pw.get("def") != "Human"]
    print("total pawns:", len(pawns))
    for a in animals[:10]:
        print(a.get("id"), a.get("name"), a.get("def"), a.get("kind"), a.get("faction"), a.get("position"))
    # a colonist position for fire/explosion siting
    col = [pw for pw in pawns if pw.get("kind")=="Colonist"]
    if col:
        print("colonist pos sample:", col[0].get("position"))
