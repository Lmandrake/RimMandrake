import sys; sys.path.insert(0,"Transient")
from cp_lib import *
st = json.load(open("Transient/cp_state.json")); wid, hid = st["wolf"], st["hare"]
def step(n): return call("rimworld/step_game_ticks", ticks=n, pauseFirst=True)
for i in range(5):
    step(60)
    d = call("jawa/damage_log", action="read", pawnsOnly=True)
    print(i, "events", d["matchedCount"], "totalRecorded", d["totalRecorded"])
    if d["matchedCount"]: break
for e in d["events"][:6]: print(J(e,500))
