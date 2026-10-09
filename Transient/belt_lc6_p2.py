import sys; sys.path.insert(0,"Transient")
from belt_lc6_lib import *
P="RM_Piinnok13311"
out=json.load(open("Transient/belt_lc6_p1.json"))
call("jawa/pawn_need", pawn=P, action="need", need="Food", level=0.95)
step(600); s=wstate(P); print("back to watch?", s)
# hide it with a colonist, then force a Goto while hidden (interrupted job)
r=spawn_pawn("Colonist",54,50,"player",1); cid=r["pawns"][0]["id"]
step(150); s=wstate(P); print("hidden again", s)
kill(cid)
r=call("jawa/ordered_job", pawnId=P, jobDef="Goto", targetAX=52, targetAZ=52, waitTicks=30)
step(60); s=wstate(P); print("C interrupted by forced Goto while hidden:", s); out["C_interrupt_clears_hidden_and_sign"]= (s["hidden"] is False and len(s["signs"])==0)
step(300)
# injury: small cut while visible
s=wstate(P); print("pre-injury", s)
r=call("jawa/damage", damageDef="Cut", amount=2, thingId=P, allowColonists=True); show(r,300)
step(60); s=wstate(P); print("D after 2 dmg:", s); out["D_injury_survives"]= not s["dead"]
r=call("jawa/pawn_get", pawn=P); print([h["def"] for h in r["pawns"][0]["hediffs"]])
open("Transient/belt_lc6_p1.json","w").write(json.dumps(out))
