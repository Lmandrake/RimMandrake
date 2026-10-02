import sys; sys.path.insert(0,"Transient")
from cp_lib import *
def step(n): return call("rimworld/step_game_ticks", ticks=n, pauseFirst=True)
for i in range(10):
    r = step(300)
    res = call("jawa/thing_lineage", ids="Meat_Muffalo11429")["results"][0]
    print(i, "found", res["found"], "fate", res["fate"], "chain", res.get("holderChain", [None])[0])
    if not res["found"] or res.get("fate"): break
for e in res["events"]: print("   ", e["seq"], e["tick"], e["kind"], "other", e["otherId"], "count", e["count"], e["holder"], e["destroyMode"])
print(J(call("jawa/pawn_census", ids="Human963")["pawns"][0]["job"],200))
