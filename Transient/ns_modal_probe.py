import sys, json; sys.path.insert(0,"Transient")
from cp_lib import *
def wl():
    r=call("jawa/window_list_close", action="list"); return [w["type"].split(".")[-1] for w in r["windows"]], r.get("ticksGame")
print(J(call("jawa/faction_name_set", action="set", defNames="PlayerColony", names="PlayerColony=Northstar Test Colony", dryRun=False, protectPlayer=False, onlyGenerated=False),500))
print(J(call("jawa/window_list_close", action="close", typeName="Dialog_NamePlayerFactionAndSettlement", closeAll=True),150))
for i in range(6):
    r=call("rimworld/step_game_ticks", ticks=1500, pauseFirst=True); print(i, wl())
