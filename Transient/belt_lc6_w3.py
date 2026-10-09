import sys; sys.path.insert(0,"Transient")
from belt_lc6_lib import *
W=json.load(open("Transient/belt_lc6_w1.json"))["W"]
show(call("jawa/damage", damageDef="Cut", amount=5, thingId=W, allowColonists=True),120)
step(60)
alive=[p for p in census()["pawns"] if p["id"]==W and not p["dead"]]
print("alive", bool(alive))
for d in ("RM_WatcherRemains_Watcher","RM_WatcherSign_SeamGlint"):
    r=call("jawa/list_things", defName=d); print(d, r.get("countMatched"), [(t["x"],t["z"]) for t in r["things"]])
cs=call("jawa/list_things", group="Corpse")["things"]; print("watcher corpses", [t for t in cs if "Watcher" in t["def"]])
r=call("jawa/get_defs", defs="ThingDef/RM_WatcherRemains_Watcher", fields="smeltProducts,costList,thingCategories,smeltable"); print(json.dumps(r["defs"][0].get("fields"))[:400])
r=call("jawa/get_defs", defs="RecipeDef/RM_SmeltWatcherHusk", fields="products,ingredients,defName"); print(json.dumps(r["defs"][0].get("fields"))[:400] if r["defs"] and "fields" in r["defs"][0] else r["notFound"])
