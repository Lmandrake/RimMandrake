import sys, json; sys.path.insert(0,"Transient")
from cp_lib import *
r=call("jawa/list_pawns", includeHealth=True, includeCorpses=False, limit=500)
for p in r["pawns"]:
    if p.get("isPlayer") and p.get("intelligence")=="Humanlike":
        print(p["id"], [(h["def"],h.get("part")) for h in p["health"]["hediffs"]])
