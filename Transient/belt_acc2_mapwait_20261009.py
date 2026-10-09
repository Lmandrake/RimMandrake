import sys,json,time
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
t0=time.time()
while time.time()-t0<90:
    r=S.call("jawa/map_info")
    if r.get("success"): print("map",int(time.time()-t0),json.dumps(r,default=str)[:600]); break
    time.sleep(5)
else:
    print(json.dumps(S.call("rimworld/get_game_info"),default=str)[:500])
