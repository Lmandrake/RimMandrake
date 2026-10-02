import sys; sys.path.insert(0,"Transient")
from cp_lib import *
def step(n): return call("rimworld/step_game_ticks", ticks=n, pauseFirst=True)
pr = call("jawa/spawn_pawn", kindDef="Wolf_Timber", x=40, z=40, faction="none", count=1); print("pred:", J(pr,250))
wid = pr["pawns"][0]["id"]
hid = "Hare11402"
for i in range(8):
    step(120)
    c = call("jawa/pawn_census", ids=wid+","+hid)
    rows = {p["id"]:p for p in c["pawns"]}
    w = rows[wid]
    print(i, "wolf hunting:", w["isPredatorHunting"], "prey:", w["preyId"], "job:", J(w["job"],200), "hostile:", w["hostile"], "faction:", w["faction"], "| hare dead:", rows[hid]["dead"])
    if w["isPredatorHunting"]: break
print("sanity: hare row job", J(rows[hid]["job"],200))
open("Transient/cp_state.json","w").write(json.dumps({"wolf":wid,"hare":hid}))
