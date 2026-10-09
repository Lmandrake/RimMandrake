import sys, json, time
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
r = S.call("jawa/clear_area", rect="40,40,24,24"); print("clear", r.get("success"), str(r.get("message"))[:160], flush=True)
for i in range(4):
    time.sleep(2); print(i, S.call("jawa/map_info").get("success"), flush=True)
