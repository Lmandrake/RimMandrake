import sys; sys.path.insert(0,"Transient")
from cp_lib import *
def step(n): return call("rimworld/step_game_ticks", ticks=n, pauseFirst=True)
cen = lambda **k: call("jawa/pawn_census", **k)
# A: mental break on a colonist
r = call("jawa/pawn_force_mental_break", pawn="Human960", breakDef="Wander_Sad", reason="companion proof"); print("A force:", J(r,400))
step(30)
c = cen(ids="Human960"); p = c["pawns"][0]
print("A census pawn:", J({k:p[k] for k in ("id","inMentalState","mentalState","job","isColonist")},700))
# B: predator + prey far from colonists
pr = call("jawa/spawn_pawn", kindDef="Wolf", x=40, z=40, faction="none", count=1); print("B pred spawn:", J(pr,300))
hz = call("jawa/spawn_pawn", kindDef="Hare", x=44, z=40, faction="none", count=1); print("B hare spawn:", J(hz,300))
open("Transient/cp_state.json","w").write(json.dumps({"wolf":pr,"hare":hz}, default=str))
