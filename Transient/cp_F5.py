import sys; sys.path.insert(0,"Transient")
from cp_lib import *
def step(n): return call("rimworld/step_game_ticks", ticks=n, pauseFirst=True)
step(400)
lin = call("jawa/thing_lineage", ids="Meat_Muffalo11429,Meat_Muffalo11425")
for res in lin["results"]:
    print(res["id"], "found", res["found"], "fate", res["fate"])
    for e in res["events"]: print("   ", e["seq"], e["tick"], e["kind"], "other", e["otherId"], "count", e["count"], "holder", e["holder"], e["destroyMode"])
