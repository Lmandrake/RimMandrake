import sys,json,time
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
t0=time.time()
while time.time()-t0<100:
    g=S.call("rimworld/get_game_info")
    s=json.dumps(g,default=str)
    if '"programState": "Playing"' in s: print("playing",int(time.time()-t0)); break
    time.sleep(4)
print(s[:700])
r=S.call("jawa/map_info"); print(json.dumps(r,default=str)[:500])
