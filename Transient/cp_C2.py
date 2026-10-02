import sys; sys.path.insert(0,"Transient")
from cp_lib import *
st = json.load(open("Transient/cp_state.json")); wid, hid = st["wolf"], st["hare"]
def step(n): return call("rimworld/step_game_ticks", ticks=n, pauseFirst=True)
step(120)
d = call("jawa/damage_log", action="read", sinceSeq=2)
print("since 2:", d["matchedCount"], "complete", d["completeSinceSeq"])
for e in d["events"][:6]: print(J(e,520))
c = call("jawa/pawn_census", ids=hid, includeDead=True); print("hare:", J({k:c["pawns"][0][k] for k in ("dead","spawned","downed")}))
