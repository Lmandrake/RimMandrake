import sys; sys.path.insert(0,"Transient")
from belt_lc6_lib import *
P="RM_Piinnok13311"
out={}
print("start", wstate(P))
# A. colonist 3 cells away -> hide + sign
r=spawn_pawn("Colonist",54,50,"player",1); cid=r["pawns"][0]["id"]; print("col",cid)
step(150); s=wstate(P); print("A after colonist near:", s); out["A_hide_by_colonist"]= bool(s["hidden"]) and len(s["signs"])==1
# B. kill colonist; hunger emerge: set food low while hidden -> job ends / emerges at once
kill(cid); step(30)
call("jawa/pawn_need", pawn=P, action="need", need="Food", level=0.1)
step(200); s=wstate(P); print("B hungry (food .1):", s, call("jawa/pawn_need", pawn=P, action="list")); out["B_hunger_emerge"]= (s["hidden"] is False and len(s["signs"])==0)
open("Transient/belt_lc6_p1.json","w").write(json.dumps(out))
