import sys,json,time
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
r=S.call("rimworld/start_debug_game_ready"); print(json.dumps(r,default=str)[:400])
t0=time.time()
while time.time()-t0<90:
    g=S.call("rimworld/get_game_info")
    st=(g.get("state") or g) if isinstance(g,dict) else {}
    s=json.dumps(g,default=str)
    if '"hasCurrentGame": true' in s or "Playing" in s: print("up after",int(time.time()-t0)); print(s[:500]); break
    time.sleep(4)
else: print("timeout",s[:300])
