import sys,json,time
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
for i in range(60):
    g=S.call("rimworld/get_game_info"); s=json.dumps(g,default=str)
    if '"programState": "Playing"' in s and '"playable": true' in s: print("ready",i); break
    time.sleep(3)
else: print("notready",s[:400])
S.quiet()
print(S.call("jawa/map_info"))
