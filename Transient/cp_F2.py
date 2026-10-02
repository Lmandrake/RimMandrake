import sys; sys.path.insert(0,"Transient")
from cp_lib import *
def step(n): return call("rimworld/step_game_ticks", ticks=n, pauseFirst=True)
A = "Thing_Meat_Muffalo11422"
r = call("rimworld/spawn_thing", defName="Meat_Muffalo", x=135, z=106, stackCount=15); print("spawn2:", J(r,260))
B = r.get("thingId")
l = call("jawa/list_things", defName="Meat_Muffalo", rect="130,100,12,12"); print("things:", J([(t.get("id"),t.get("stackCount"),t.get("x"),t.get("z")) for t in (l.get("things") or l.get("results") or [])],400), l.get("countMatched"))
s = call("jawa/split_stack", thing=A, count=8); print("split:", J(s,400))
lin = call("jawa/thing_lineage", ids=A+","+(B or "")); print("lineage:", J(lin,2500))
