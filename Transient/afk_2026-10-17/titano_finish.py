import sys, os, json, time
sys.path.insert(0, os.path.join("src","RimMandrake","Utils"))
from modcheck import reviewmap as RM
B = RM.LiveBridge()
r = B.call("rimworld/load_game_ready", saveName="RM_walk_20261017_creatures"); print("load", r.get("success"), str(r.get("message"))[:100])
for _ in range(40):
    time.sleep(3)
    i = B.call("rimworld/get_game_info")
    if (i.get("state") or {}).get("hasCurrentGame") and B.call("jawa/map_info").get("success"): break
B.call("rimworld/pause_game", pause=True)
a = B.call("rimworld/get_game_info"); time.sleep(3); b = B.call("rimworld/get_game_info")
print("ticks", a.get("ticksGame") or (a.get("state") or {}).get("ticksGame"), b.get("ticksGame") or (b.get("state") or {}).get("ticksGame"))
print(json.dumps(b)[:300])
