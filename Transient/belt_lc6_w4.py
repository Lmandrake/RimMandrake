import sys; sys.path.insert(0,"Transient")
from belt_lc6_lib import *
for p in census()["pawns"]:
    if p["isColonist"] and 85<p["x"]<125 and 20<p["z"]<55: kill(p["id"])
W=spawn_pawn("RM_Watcher",97,36,"none",1)["pawns"][0]["id"]
step(120)
c=spawn_pawn("Colonist",110,36,"player",1)["pawns"][0]; call("jawa/set_draft", pawnId=c["id"], drafted=True)
print("colonist", c["x"], c["z"])
for i in range(6):
    step(40)
    v=call("jawa/comp_read", thing=W, comp="WatcherStalk", members="phase,angle,hasTarget,targetAngle")["values"]
    print(i, v)
