import sys, time; sys.path.insert(0,"Transient")
from belt_lc6_lib import *
show(call("rimworld/load_game", saveName="belt_lc6_watchers"),300)
for i in range(60):
    time.sleep(3)
    try:
        r=call("rimworld/get_game_info")
        if r.get("state",{}).get("programState")=="Playing" and r.get("ticksGame",0)>1000: break
    except Exception as e: pass
print("loaded", call("rimworld/get_game_info").get("ticksGame"))
def hid():
    out=[]
    for p in census()["pawns"]:
        if p["kindDef"]=="RM_Piinnok" and not p["dead"]:
            g=call("jawa/pawn_get", pawn=p["id"])["pawns"][0]
            if any(h["def"]=="RM_WatcherHidden" for h in g["hediffs"]): out.append(p["id"])
    return sorted(out)
b=json.load(open("Transient/belt_lc6_p8.json"))
H=hid(); S=sorted((t["x"],t["z"]) for t in call("jawa/list_things", defName="RM_WatcherSign_SandDimple")["things"])
print("after load hidden",len(H),"signs",len(S),"same hidden set:",H==b["H"],"same sign cells:",S==[tuple(x) for x in b["S"]])
# orphan sign
call("jawa/spawn_batch", ops="RM_WatcherSign_SandDimple:100,60")
print("orphan present:", len(call("jawa/list_things", rect="100,60,1,1", defName="RM_WatcherSign_SandDimple")["things"]))
step(260)
print("orphan after 260 ticks:", len(call("jawa/list_things", rect="100,60,1,1", defName="RM_WatcherSign_SandDimple")["things"]))
