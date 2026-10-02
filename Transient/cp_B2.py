import sys; sys.path.insert(0,"Transient")
from cp_lib import *
st = json.load(open("Transient/cp_state.json")); wid, hid = st["wolf"], st["hare"]
def step(n): return call("rimworld/step_game_ticks", ticks=n, pauseFirst=True)
r = call("jawa/ordered_job", pawnId=wid, jobDef="PredatorHunt", targetAId=hid, waitTicks=5); print("order:", J(r,500))
for i in range(6):
    c = call("jawa/pawn_census", ids=wid+","+hid); rows={p["id"]:p for p in c["pawns"]}; w=rows[wid]
    print(i, "hunting", w["isPredatorHunting"], "preyId", w["preyId"], "job", J(w["job"],250), "hare dead", rows[hid]["dead"], "enemyTarget", w["enemyTargetId"])
    if w["isPredatorHunting"]: break
    step(60)
